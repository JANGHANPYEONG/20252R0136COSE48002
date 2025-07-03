import argparse
import json
import pandas as pd
import mlflow
import torch
import torch.optim as optim
import torch.nn as nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
import random
import numpy as np

from models.model import make_model
from utils.dataset import MeatDataset
from utils.split_data import split_data, read_data
from utils.epoch import regression, classification
from utils.log import log
from utils.add_param import add_arg, add_param

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)

config_argparser = argparse.ArgumentParser(description='read config')
config_argparser.add_argument('--config', default="./configs/default_ViT_config.json", type=str, help="Path to config file")
config_args, remaining_args = config_argparser.parse_known_args()

with open(config_args.config, 'r') as json_file:
    config = json.load(json_file)

args, train_type = add_arg(config, remaining_args)

experiment = args.experiment if args.experiment is not None else config.get('experiment', 'test')
run_name = args.run if args.run is not None else config.get('run', 'test')
save_model = args.save_model if args.save_model is not False else config['models'].get('save_model', False)
epochs = args.epochs if args.epochs is not None else config['hyperparameters'].get('epochs', 20)
lr = args.lr if args.lr is not None else config['hyperparameters'].get('learning_rate', 1e-5)
batch_size = args.batch_size if args.batch_size is not None else config['hyperparameters'].get('batch_size', 32)
weight_decay = args.weight_decay if args.weight_decay is not None else config['hyperparameters'].get('weight_decay', 5e-4)
num_workers = args.num_workers if args.num_workers is not None else config['hyperparameters'].get('num_workers', 4)
seed = args.seed if args.seed is not None else config['hyperparameters'].get('seed', 42)
cross_validation = args.cross_validation if args.cross_validation is not None else config['hyperparameters'].get('cross_validation', 0)
factor = config['hyperparameters'].get('factor', 0.3)
patience = config['hyperparameters'].get('patience', 2)
port = args.port
csv_path = args.csv_path
train_csv_path = args.train_csv
val_csv_path = args.val_csv
cla = args.classification

print(f"\ntrain type: {train_type}")

params = add_param(train_type, args)

# 랜덤 시드 설정
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

output_columns = config['output_columns']

if train_csv_path is None and val_csv_path is None:
    # csv 파일 읽기
    csv = pd.read_csv(csv_path)
    print(output_columns)

    # 데이터 분할 (cross_validation의 수 만큼 데이터 분할, cross_validation=0이면 5개로 분할 -> train 4 : val 1)
    fold_data = split_data(csv, output_columns, cross_validation)

elif train_csv_path is not None and val_csv_path is not None:
    train_csv = pd.read_csv(train_csv_path)
    val_csv = pd.read_csv(val_csv_path)

    train_data, val_data = read_data(train_csv, val_csv)

else:
    raise ValueError("csv path error")



# #########################################################################################################################################
# train

# mlflow 설정
mlflow.set_tracking_uri('http://0.0.0.0:'+str(port))
mlflow.set_experiment(experiment)

if cross_validation:
    n_folds = cross_validation
    print("\n" + "="*50)
    print(f"     K-Fold Cross Validation (K={n_folds}) Enabled")
    print("="*50 + "\n")
else:
    n_folds = 1
    print("\n" + "="*50)
    print("     Single Fold Training")
    print("="*50 + "\n")

# 학습 파라미터
params.update({
    'num_epochs':epochs,
    'optimizer':None,
    'train_dl':None,
    'val_dl':None,
    'scheduler':None,
    'save_model':save_model,
    'loss_func':None,
    'fold':(0, 0),
    'label_names':output_columns,
})

all_fold_results = []
for fold in range(n_folds):
    # cross_validation 시 run name 뒤에 fold (숫자) 붙임
    if cross_validation:
        r = run_name + " fold " + str(fold+1)
    else:
        r = run_name

    with mlflow.start_run(run_name=r) as run:
        print(f"run_id: {run.info.run_id}")

        # 기본 파라미터 mlflow에 기록
        mlflow.log_dict(config, 'config/configs.json')
        mlflow.log_param("model", config["models"].get('model_name', 'null'))
        mlflow.log_param("learning_rate", lr)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("weight_decay", weight_decay)    

        # train, val 데이터셋
        if train_csv_path is None and val_csv_path is None:
            val_data = fold_data[fold]
            train_data = pd.concat([fold_data[i] for i in range(len(fold_data)) if i != fold])
            mlflow.log_param("train_csv", csv_path)
            mlflow.log_param("val_csv", csv_path)

        else:
            mlflow.log_param("train_csv", train_csv_path)
            mlflow.log_param("val_csv", val_csv_path)
            
        val_dataset = MeatDataset(val_data, config, is_train=False)
        train_dataset = MeatDataset(train_data, config, is_train=True)

        # 모델 만들기
        model = make_model(config)
        model = model.to(device)

        # 모델의 파라미터 개수 기록
        total_params = sum(p.numel() for p in model.parameters())
        mlflow.log_param("total_params", total_params)

        # optimizer와 scheduler
        params['optimizer'] = optim.Adam(model.parameters(), lr = lr, weight_decay=weight_decay)
        params['scheduler'] = scheduler = ReduceLROnPlateau(params['optimizer'], mode='min', factor=factor, patience=patience, verbose=True)

        # dataloader
        params['train_dl'] = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
        params['val_dl'] = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

        ## loss function
        params['loss_func'] = nn.MSELoss()

        if cla:
            params['loss_func'] = nn.CrossEntropyLoss()

        if cross_validation:
            params['fold'] = (fold + 1, cross_validation)

        # 학습 진행
        if cla:
            fold_result = classification(model, params)
        else:
            fold_result = regression(model, params)

        # fold 결과 저장
        all_fold_results.append(fold_result)

        # 마지막 fold일 경우 결과 기록
        if fold + 1 == n_folds:
            log(all_fold_results, cross_validation, params['label_names'])

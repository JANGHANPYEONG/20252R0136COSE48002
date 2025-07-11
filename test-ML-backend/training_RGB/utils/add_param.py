# config를 읽는 코드

import argparse
import json

def add_arg(config, remaining_args):

    argparser=argparse.ArgumentParser(description='training pipeline')

    argparser.add_argument('--experiment', type=str)  # experiment 이름 설정
    argparser.add_argument('--run', type=str)  # run 이름 설정
    argparser.add_argument('--save_model', action='store_true')  # 모델 저장
    argparser.add_argument('--epochs', type=int)  #epochs
    argparser.add_argument('--lr', '--learning_rate', type=float)  # learning rate
    argparser.add_argument('--batch_size', type=int)
    argparser.add_argument('--weight_decay', type=float) # Adam의 weight_decay
    argparser.add_argument('--num_workers', type=int) # 서브 프로세스 개수 (cpu 코어 개수) - 기본 4개
    argparser.add_argument('--csv_path', default='./dataset/default.csv') # csv 경로
    argparser.add_argument('--train_csv', type=str)
    argparser.add_argument('--val_csv', type=str)
    argparser.add_argument('--seed', type=int) # 랜덤 시드
    argparser.add_argument('--cross_validation', type=int) # k-fold-cross-validation. 0: 비활성화, 2이상: k-fold 활성화 및 fold 개수 지정
    argparser.add_argument('--port', default=5000, type=int) # 포트 설정
    
    argparser.add_argument('--classification', action='store_true')

    train_type = config.get('train_type', 'default')

    if train_type == 'drloc':
        argparser.add_argument('-m', type=int, default=64)
        argparser.add_argument('-l', type=float, default=1.0)

    if train_type == 'local_guidance':
        argparser.add_argument('--distillation_weight', type=float, default=2.0)

    args = argparser.parse_args(remaining_args)

    return args, train_type


def add_param(train_type, args): 

    params_train = {
        'train_type':train_type
    }

    if train_type == 'drloc':
        m = args.m
        lambda_ = args.l

        params_train.update({
            'm':m,
            'lambda_':lambda_
        })

    if train_type == 'local_guidance':
        distillation_weight = args.distillation_weight if args.distillation_weight is not None else config['hyperparameters'].get('distillation_weight', 0.5)

        params_train.update({
            'distillation_weight':distillation_weight
        })
    

    return params_train

    

    



    


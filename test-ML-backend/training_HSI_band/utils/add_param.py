import argparse
import json
from typing import Dict, Tuple

# Parse config and command line arguments
def add_arg(config: Dict, remaining_args: list) -> Tuple[argparse.Namespace, str]:
  
    argparser = argparse.ArgumentParser(description='HSI Band Selection Pipeline')
    
    # Basic parameters
    argparser.add_argument('--experiment', type=str, help='MLflow experiment name')
    argparser.add_argument('--run', type=str, help='MLflow run name')
    argparser.add_argument('--save_model', action='store_true', help='Whether to save model')
    argparser.add_argument('--epochs', type=int, help='Number of training epochs')
    argparser.add_argument('--lr', '--learning_rate', type=float, help='Learning rate')
    argparser.add_argument('--batch_size', type=int, help='Batch size')
    argparser.add_argument('--weight_decay', type=float, help='Weight decay')
    argparser.add_argument('--num_workers', type=int, help='Number of data loader workers')
    argparser.add_argument('--csv_path', type=str, help='CSV file path')
    argparser.add_argument('--train_csv', type=str, help='Training CSV file path')
    argparser.add_argument('--val_csv', type=str, help='Validation CSV file path')
    argparser.add_argument('--seed', type=int, help='Random seed')
    argparser.add_argument('--port', default=5000, type=int, help='MLflow port')
    
    # Band selection parameters
    argparser.add_argument('--pre_target_bands', type=int, help='Number of target bands for preprocessing')
    argparser.add_argument('--final_target_bands', type=int, help='Number of final target bands')
    argparser.add_argument('--pre_config', type=str, help='Preprocessing config file path')
    argparser.add_argument('--train_config', type=str, help='Training config file path')
    
    # Result saving parameters
    argparser.add_argument('--output_dir', type=str, help='Output directory for results')
    argparser.add_argument('--save_results', action='store_true', help='Whether to save results')
    
    # Get train_type
    train_type = config.get('train_type', 'default')
    
    # Additional parameters by train_type
    if train_type == 'gpr_ard':
        argparser.add_argument('--kernel_type', type=str, default='rbf', 
                              choices=['rbf', 'matern', 'linear'], help='GPR kernel type')
        argparser.add_argument('--alpha', type=float, default=1e-6, help='GPR alpha value')
    
    elif train_type == 'random_frog':
        argparser.add_argument('--n_iterations', type=int, default=1000, 
                              help='Number of Random frog iterations')
        argparser.add_argument('--n_samples', type=int, default=50, 
                              help='Number of Random frog samples')
    
    elif train_type == 'shap':
        argparser.add_argument('--background_samples', type=int, default=100, 
                              help='Number of SHAP background samples')
        argparser.add_argument('--nsamples', type=int, default=100, 
                              help='Number of SHAP calculation samples')
    
    args = argparser.parse_args(remaining_args)
    return args, train_type

# Add parameters
def add_param(train_type: str, args: argparse.Namespace, config: Dict) -> Dict:
    
    params = {
        'train_type': train_type,
        'input_type': 'vector'  # 현재는 vector 고정
    }
    
    # 밴드 수 설정 (전처리와 본처리 분리)
    if args.pre_target_bands is not None:
        params['pre_target_bands'] = args.pre_target_bands
    else:
        params['pre_target_bands'] = config.get('preprocessing', {}).get('target_bands', 50)
    
    if args.final_target_bands is not None:
        params['final_target_bands'] = args.final_target_bands
    else:
        params['final_target_bands'] = config.get('training', {}).get('target_bands', 10)
    
    # config 파일 경로 설정
    if args.pre_config:
        params['pre_config_path'] = args.pre_config
    else:
        params['pre_config_path'] = config.get('preprocessing', {}).get('config_path', 'configs/pre/vector_pre_config.json')
    
    if args.train_config:
        params['train_config_path'] = args.train_config
    else:
        params['train_config_path'] = config.get('training', {}).get('config_path', 'configs/training/vector_training_config.json')
    
    # train_type별 파라미터
    if train_type == 'gpr_ard':
        params.update({
            'kernel_type': args.kernel_type or config.get('gpr_ard', {}).get('kernel_type', 'rbf'),
            'alpha': args.alpha or config.get('gpr_ard', {}).get('alpha', 1e-6)
        })
    
    elif train_type == 'random_frog':
        params.update({
            'n_iterations': args.n_iterations or config.get('random_frog', {}).get('n_iterations', 1000),
            'n_samples': args.n_samples or config.get('random_frog', {}).get('n_samples', 50)
        })
    
    elif train_type == 'shap':
        params.update({
            'background_samples': args.background_samples or config.get('shap', {}).get('background_samples', 100),
            'nsamples': args.nsamples or config.get('shap', {}).get('nsamples', 100)
        })
    
    # 결과 저장 관련
    if args.output_dir:
        params['output_dir'] = args.output_dir
    else:
        params['output_dir'] = config.get('output_dir', './results')
    
    params['save_results'] = args.save_results or config.get('save_results', False)
    
    return params

# Validate config file
def validate_config(config: Dict) -> bool:
    
    required_keys = ['train_type']
    
    for key in required_keys:
        if key not in config:
            print(f"Error: Missing required key '{key}' in config")
            return False
    
    # train_type 검증
    valid_train_types = ['default', 'gpr_ard', 'random_frog', 'shap']
    if config['train_type'] not in valid_train_types:
        print(f"Error: Invalid train_type '{config['train_type']}'. Must be one of {valid_train_types}")
        return False
    
    return True 
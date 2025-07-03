import importlib
import mlflow

def make_model(config):

    model_cfg = config['models']

    model_name = model_cfg['model_name']
    model_file = model_cfg['model_file']
    load_model = model_cfg['load_model']
    model_version = model_cfg['model_version']
    num_classes = model_cfg['num_classes']
    out_dim = model_cfg['out_dim']
    pretrained = model_cfg['pretrained']
    in_chans = model_cfg['in_chans']

    if not load_model :
        module = importlib.import_module(f'models.{model_file}')
        model = module.create_model(model_name, pretrained, num_classes, in_chans, out_dim, config)
    
    else :
        model_uri = f"models:/{model_name}/{model_version}"
        
        try:
            model = mlflow.pytorch.load_model(model_uri)
            print(f"Success to load model")
        except mlflow.exceptions.MlflowException as e:
            print(f"Error loading model: {e}")
    
    return model

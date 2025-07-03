# transform 저장하는 코드

from torchvision import transforms

def create_transform(transform_cfg):
    transform = []

    if 'RandomRotation' in transform_cfg and transform_cfg['RandomRotation']:
        transform.append(transforms.RandomRotation(transform_cfg['RandomRotation']))
    
    if 'Resize' in transform_cfg and transform_cfg['Resize']:
        transform.append(transforms.Resize(transform_cfg['Resize']))
    
    if 'CenterCrop' in transform_cfg and transform_cfg['CenterCrop']:
        transform.append(transforms.CenterCrop(transform_cfg['CenterCrop']))
    
    if 'RandomHorizontalFlip' in transform_cfg and transform_cfg['RandomHorizontalFlip'] is not None:
        transform.append(transforms.RandomHorizontalFlip(transform_cfg['RandomHorizontalFlip']))
    
    if 'RandomVerticalFlip' in transform_cfg and transform_cfg['RandomVerticalFlip'] is not None:
        transform.append(transforms.RandomVerticalFlip(transform_cfg['RandomVerticalFlip']))
    
    if 'ToTensor' in transform_cfg and transform_cfg['ToTensor']:
        transform.append(transforms.ToTensor())
    
    if 'Normalize' in transform_cfg and transform_cfg['Normalize']:
        mean = transform_cfg['Normalize'].get('mean', [0.485, 0.456, 0.406])
        std = transform_cfg['Normalize'].get('std', [0.229, 0.224, 0.225])
        transform.append(transforms.Normalize(mean=mean, std=std))

    return transforms.Compose(transform)

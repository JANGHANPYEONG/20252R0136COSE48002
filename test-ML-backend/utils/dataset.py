# 이미지, 라벨 매칭된 데이터셋 반환하는 코드

from torch.utils.data import Dataset
import torch
from PIL import Image, ExifTags
import torchvision.transforms.functional as TF
import numpy as np

from utils.transform import create_transform


class MeatDataset(Dataset):
    def __init__(self, dataframe, config, is_train=True):
        self.dataframe = dataframe
        self.config = config
        self.is_train = is_train
        self.transforms = self._create_transforms()


        if 'SEX' in self.dataframe.columns:
            self.dataframe['SEX'] = self.dataframe['SEX'].map({'암': 0, '거': 1})
        
    def __len__(self):
        return len(self.dataframe)
    
    def _create_transforms(self):
        transforms = []
        for dataset_config in self.config['datasets']:
            if self.is_train:
                transform_config = dataset_config['train_transform']
            else:
                transform_config = dataset_config['val_transform']
            transforms.append(create_transform(transform_config))
        return transforms
    
    def load_image(self, img_path):
        image = Image.open(img_path)

        try:
            orientation_tag = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            exif = image.getexif()
            if exif and orientation_tag in exif:
                orientation = exif[orientation_tag]
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except Exception as e:
            print(f"Error correcting orientation: {e}")
            # If EXIF data is missing or cannot be processed, proceed without correction
            pass

        if image.mode == 'RGBA':
            return image.convert('RGB')
        return image

    def process_image_group(self, row, input_columns, transform):
        images = []
        for col in input_columns:
            img_name = row[col]
            image = self.load_image(img_name)
            
            if row.get('is_flipped', False):
                image = TF.vflip(image)
            
            images.append(np.array(image))

        images = [np.expand_dims(img, axis=-1) if img.ndim == 2 else img for img in images]
        
        # 이미지들을 numpy 배열로 결합 (채널 방향으로)
        combined_image = np.concatenate(images, axis=2)

        if combined_image.shape[2] == 1:  # Grayscale 이미지
            combined_image = combined_image.squeeze(axis=2)  # (H, W, 1) -> (H, W)

        combined_image = Image.fromarray(combined_image)
        
        if transform:
            combined_image = transform(combined_image)

        if combined_image.shape[2] == 1:  # Grayscale 이미지
            combined_image = combined_image * 2 - 1
        
        return combined_image

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        row = self.dataframe.iloc[idx]
        
        processed_images = []
        for dataset_idx, dataset_config in enumerate(self.config['datasets']):
            input_columns = dataset_config['input_columns']
            transform = self.transforms[dataset_idx] if self.transforms else None
            
            processed_image = self.process_image_group(row, input_columns, transform)
            processed_images.append(processed_image)
        
        # 다른 input_columns 그룹의 이미지들을 채널 차원으로 연결
        final_image = torch.cat(processed_images, dim=0)
        
        label_columns = self.config['output_columns']
        labels = [row.get(col, float('nan')) for col in label_columns]
        labels = torch.tensor(labels, dtype=torch.float)
        
        # grade 가져오기
        grade = row.get('grade', None)
        
        return final_image, labels, grade

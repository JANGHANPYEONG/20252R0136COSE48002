import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import mlflow
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize

# +
# # 필요한 변수 설정
# mlflow.set_tracking_uri("http://0.0.0.0:5000")  # MLflow Tracking URI 설정 (필요에 따라 수정)
# run_id = "e205573782d94b6a8bac9194ac14f2ae"
# model_uri = f"runs:/{run_id}/best_model"
# model = mlflow.pytorch.load_model(model_uri)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)

# print(model)

# +
import mlflow.pyfunc
import torch

mlflow.set_tracking_uri("http://0.0.0.0:5000")

model_name = "Classification Model"  # 등록된 모델 이름
model_version = 1  # 버전 번호

model_uri = f"models:/{model_name}/{model_version}"

model = mlflow.pytorch.load_model(model_uri)

print(model)
# -

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

mean=[0.4834, 0.3656, 0.3474] # 데이터셋의 mean과 std
std=[0.2097, 0.2518, 0.2559]

def my_forward_wrapper(attn_obj):
    def my_forward(x):
        B, N, C = x.shape
        qkv = attn_obj.qkv(x).reshape(B, N, 3, attn_obj.num_heads, C // attn_obj.num_heads).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        attn = (q @ k.transpose(-2, -1)) * attn_obj.scale
        attn = attn.softmax(dim=-1)
        attn = attn_obj.attn_drop(attn)
        attn_obj.attn = attn  # Store in the expected attribute
        attn_obj.attn_map = attn
        attn_obj.cls_attn_map = attn[:, :, 0, 1:]

        x = (attn @ v).transpose(1, 2).reshape(B, N, C)
        x = attn_obj.proj(x)
        x = attn_obj.proj_drop(x)
        return x
    return my_forward

for block in model.blocks:
    block.attn.forward = my_forward_wrapper(block.attn)

# 전처리 함수
def preprocess_image(image_path):
    transform = Compose([
        Resize(256),
        CenterCrop(224),
        ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])
    image = Image.open(image_path)
    return transform(image).unsqueeze(0)

def get_all_attention_maps(model, image_path):
    input_tensor = preprocess_image(image_path).to(device)
    attention_maps = []
    cls_weights = []
    
    def hook_fn(module, input, output):
        if isinstance(output, tuple):
            attn = output[1]
        else:
            attn = module.attn
        attention_maps.append(attn.mean(dim=1).squeeze(0))
        cls_weights.append(attn[:, :, 0, 1:].mean(dim=1).view(14, 14))
    
    hooks = []
    for block in model.blocks:
        hooks.append(block.attn.register_forward_hook(hook_fn))
    
    with torch.no_grad():
        output = model(input_tensor)
        print(output)
    
    for hook in hooks:
        hook.remove()
    
    return input_tensor, attention_maps, cls_weights

# 이미지 표시 함수
def show_img2(img1, img2, alpha=0.8, ax=None):
    if isinstance(img1, torch.Tensor):
        img1 = img1.squeeze().cpu().numpy()
    if isinstance(img2, torch.Tensor):
        img2 = img2.squeeze().cpu().numpy()
    if ax is None:
        fig, ax = plt.subplots(figsize=(20, 4))
    ax.imshow(img1)
    ax.imshow(img2, alpha=alpha, cmap='viridis')
    ax.axis('off')

# 모든 어텐션 레이어 시각화
def visualize_all_attention_layers(image_path, model, threshold=0.5):
    input_tensor, attention_maps, cls_weights = get_all_attention_maps(model, image_path)
    
    original_img = np.array(Image.open(image_path))
    img_resized = F.interpolate(input_tensor, (224, 224), mode='bilinear').squeeze(0).permute(1, 2, 0)
    img_resized = np.clip(img_resized.cpu().numpy(), 0, 1)
    
    num_layers = len(attention_maps)
    fig, axes = plt.subplots(num_layers, 5, figsize=(20, 4 * num_layers))
    
    for layer, (attn_map, cls_weight) in enumerate(zip(attention_maps, cls_weights)):
        attn_map_img = attn_map.cpu().numpy()
        cls_weight_img = cls_weight.cpu().numpy()
        
        cls_resized = F.interpolate(cls_weight.unsqueeze(0).unsqueeze(0), (224, 224), mode='bilinear').squeeze()
        cls_resized = cls_resized.cpu().numpy()
        
        attn_map_img = (attn_map_img - attn_map_img.min()) / (attn_map_img.max() - attn_map_img.min())
        cls_weight_img = (cls_weight_img - cls_weight_img.min()) / (cls_weight_img.max() - cls_weight_img.min())
        cls_resized = (cls_resized - cls_resized.min()) / (cls_resized.max() - cls_resized.min())
        
        mask = cls_resized > threshold
        masked_img = img_resized.copy()
        masked_img[~mask] = 0
        
        overlay_img = img_resized.copy()
        overlay_img = overlay_img * 0.7 + cls_resized[:, :, np.newaxis] * 0.3
        
        images = [original_img, attn_map_img, cls_weight_img, masked_img, overlay_img]
        titles = ['Original', 'Attention Map', 'CLS Attention', 'Masked Image', 'Overlay']
        
        for i, (img, title) in enumerate(zip(images, titles)):
            if img.ndim == 2:
                axes[layer, i].imshow(img, cmap='viridis')
            else:
                axes[layer, i].imshow(img)
            axes[layer, i].set_title(f'Layer {layer + 1}: {title}')
            axes[layer, i].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    fig, axes = plt.subplots(num_layers, 1, figsize=(20, 4 * num_layers))
    for layer, cls_weight in enumerate(cls_weights):
        cls_resized = F.interpolate(cls_weight.unsqueeze(0).unsqueeze(0), (224, 224), mode='bilinear').squeeze()
        cls_resized = cls_resized.cpu().numpy()
        cls_resized = (cls_resized - cls_resized.min()) / (cls_resized.max() - cls_resized.min())
        show_img2(img_resized, cls_resized, ax=axes[layer])
        axes[layer].set_title(f'Layer {layer + 1}: CLS Attention Overlay')
    
    plt.tight_layout()
    plt.show()

# 실행
visualize_all_attention_layers('./dataset/meat_dataset/20240924/240924_개체사진/240924_(11).JPG', model, threshold=0.5)
#visualize_all_attention_layers('./dataset/meat_dataset/등심1++/등심1++_000123.jpg', model, threshold=0.5)

# +
# 모든 어텐션 레이어 시각화
import numpy as np
import matplotlib.pyplot as plt
import torch.nn.functional as F
from PIL import Image

def inference(output):
    # 출력할 라벨 리스트와 출력 텐서
    labels = ["마블링", "육색", "조직감", "표면 육즙", "기호도"]

    # 출력
    print("모델의 예측:")
    print("{:<8} {:<9}{:<8}{:<7} {:<8}".format(*labels))
    print("{:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f}".format(*output[0].tolist()))
    

def visualize_all_attention_layers(image_path, model, threshold=0.5):
    input_tensor, attention_maps, cls_weights, output = get_all_attention_maps(model, image_path)
    
    original_img = np.array(Image.open(image_path))
    img_resized = F.interpolate(input_tensor, (224, 224), mode='bilinear').squeeze(0).permute(1, 2, 0)
    img_resized = np.clip(img_resized.cpu().numpy(), 0, 1)
    
    # 마지막 레이어만 시각화하도록 설정
    last_layer = len(attention_maps) - 1
    attn_map = attention_maps[last_layer]
    cls_weight = cls_weights[last_layer]
    
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    
    attn_map_img = attn_map.cpu().numpy()
    cls_weight_img = cls_weight.cpu().numpy()
    
    cls_resized = F.interpolate(cls_weight.unsqueeze(0).unsqueeze(0), (224, 224), mode='bilinear').squeeze()
    cls_resized = cls_resized.cpu().numpy()
    
    attn_map_img = (attn_map_img - attn_map_img.min()) / (attn_map_img.max() - attn_map_img.min())
    cls_weight_img = (cls_weight_img - cls_weight_img.min()) / (cls_weight_img.max() - cls_weight_img.min())
    cls_resized = (cls_resized - cls_resized.min()) / (cls_resized.max() - cls_resized.min())
    
    mask = cls_resized > threshold
    masked_img = img_resized.copy()
    masked_img[~mask] = 0
    
    overlay_img = img_resized.copy()
    overlay_img = overlay_img * 0.7 + cls_resized[:, :, np.newaxis] * 0.3
    
    images = [original_img, attn_map_img, cls_weight_img, masked_img, overlay_img]
    titles = ['Original', 'Attention Map', 'CLS Attention', 'Masked Image', 'Overlay']
    
    for i, (img, title) in enumerate(zip(images, titles)):
        if img.ndim == 2:
            axes[i].imshow(img, cmap='viridis')
        else:
            axes[i].imshow(img)
        axes[i].set_title(f'Layer {last_layer + 1}: {title}')
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    inference(output)


# -

# 실행
visualize_all_attention_layers('./dataset/meat_dataset/20240927/240927_개체사진/240927_(1).JPG', model, threshold=0.5)

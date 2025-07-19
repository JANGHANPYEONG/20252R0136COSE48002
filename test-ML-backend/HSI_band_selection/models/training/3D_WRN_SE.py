import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import Counter
import numpy as np
import pprint
# from data.loader import load_dataset

# 1. data load 해서 변형하기
# data load
data = torch.load('/data/path')
x = data['x']  # (B, D, H, W)
y = data['y']  # (B, num_targets)

# data reshape
x = x.unsqueeze(1)  # (B, D, H, W) -> (B, C, D, H, W), C=1 (channel 수)

# 2. Wide ResNet with SE Block (model)
# SE Block 
class SEBlock3D(nn.Module):
    def __init__(self, channel, reduction=16):
        """
        channel: feature map의 개수
        reduction: 채널 수를 줄이는 비율 (기본값 16): hyperparameter
        """
        super(SEBlock3D, self).__init__()

        self.global_pool = nn.AdaptiveAvgPool3d(1)  # (B,C,D,H,W) -> (B,C,1,1,1)
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False), # Squeeze (channel 수 줄임)
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False), # Excitation (원래 채널 수로 복원)
            nn.Sigmoid()
        )

    # input -> ouput 
    def forward(self, x):
        b, c, _, _, _ = x.size()
        # (B,C,1,1,1) -> (B,C)
        y = self.global_pool(x).view(b, c)
        # 다시 (B,C,1,1,1)로 복원
        y = self.fc(y).view(b, c, 1, 1, 1)
        # channel 별 weight 곱함
        return x * y.expand_as(x)

# Wide ResNet Basic Block
class WideBasic3D(nn.Module):
    def __init__(self, in_planes, out_planes, stride=1, dropout_rate=0.3):
        """
        in_planes: 입력 채널 수
        out_planes: 출력 채널 수
        stride: downsampling 여부 (기본값 1) : hyperparameter
        dropout_rate: dropout 비율 (기본값 0.3) : hyperparameter
        """
        super(WideBasic3D, self).__init__()
        
        self.conv1 = nn.Conv3d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm3d(out_planes)
        self.relu1 = nn.ReLU(inplace=True)

        self.dropout = nn.Dropout3d(p=dropout_rate) # conv1 이후 conv2 이전에 dropout 적용

        self.conv2 = nn.Conv3d(out_planes, out_planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm3d(out_planes)
        self.relu2 = nn.ReLU(inplace=True)

        self.se = SEBlock3D(out_planes) # conv2 이후에 SE Block 추가

        # Skip connection
        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != out_planes:
            self.shortcut = nn.Sequential(
                nn.Conv3d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)
            )

    def forward(self, x):
        # conv1
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu1(out)
        # Dropout 적용
        out = self.dropout(out)
        # conv2
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu2(out)
        # SE Block 적용
        out = self.se(out)
        # Skip connection
        out += self.shortcut(x)

        return out

# Wide ResNet with SE Block
class SE_WRN_3D(nn.Module):
    def __init__(self, depth=16, widen_factor=4, num_targets=10, input_channels=1, dropout_rate=0.3):
        """
        depth: layer 수 (기본값 16) : hyperparameter
        widen_factor: 채널 수를 늘리는 비율 (기본값 4) : hyperparameter
        num_classes: label 개수 (기본값 10) : hyperparameter
        dropout_rate: dropout 비율 (기본값 0.3) : hyperparameter
        (내부) stride: downsampling 여부 (기본값 1) : hyperparameter
        """
        super(SE_WRN_3D, self).__init__()
        assert (depth - 4) % 6 == 0, "depth는 6n + 4 형태여야 합니다."
        n = (depth - 4) // 6
        k = widen_factor

        self.in_planes = 16 # residual block이 요구하는 input channel 수
        self.conv1 = nn.Conv3d(input_channels, 16, kernel_size=3, stride=1, padding=1, bias=False)

        # layer1, layer2, layer3: 각 residual block
        self.layer1 = self._make_layer(WideBasic3D, 16*k, n, stride=1, dropout_rate=dropout_rate)
        self.layer2 = self._make_layer(WideBasic3D, 32*k, n, stride=2, dropout_rate=dropout_rate)
        self.layer3 = self._make_layer(WideBasic3D, 64*k, n, stride=2, dropout_rate=dropout_rate)

        # BatchNorm, ReLU, Linear
        self.bn = nn.BatchNorm3d(64*k)
        self.relu = nn.ReLU(inplace=True)
        self.regressor = nn.Linear(64*k, num_targets)

    def _make_layer(self, block, out_planes, num_blocks, stride, dropout_rate):
        """
        block: WideBasic3D 클래스
        out_planes: 출력 채널 수 (기본값) : hyperparameter
        num_blocks: block 개수 (depth와 연결) : hyperparameter
        stride: downsampling 여부 (기본값 1) : hyperparameter
        dropout_rate: dropout 비율 (기본값 0.3) : hyperparameter
        """
        strides = [stride] + [1]*(num_blocks - 1) # 첫 번째 block 만 stride 2 가능 (downsampling)
        # 각 block 순차적 생성, self.in_planes는 이전 block의 out_planes로 업데이트
        layers = []
        for s in strides:
            layers.append(block(self.in_planes, out_planes, stride=s, dropout_rate=dropout_rate))
            self.in_planes = out_planes
        return nn.Sequential(*layers)

    def forward(self, x):
        # 입력을 16 채널로 변환
        out = self.conv1(x)

        # 각 residual block 통과
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)

        # Grad-CAM용 feature 저장
        self.feature_map = out

        out = self.bn(out)
        out = self.relu(out)

        # Global Average Pooling
        out = F.adaptive_avg_pool3d(out, 1)
        out = out.view(out.size(0), -1) # (B, C, 1, 1, 1) -> (B, C)
        out = self.regressor(out)
        return out
    
# 3. model instance 생성
model = SE_WRN_3D(
    depth=16, 
    widen_factor=4, 
    num_targets=10, # moisture, pH, ... label 개수
    input_channels=1, 
    dropout_rate=0.3
)

# 4. 예측
with torch.no_grad():
    output = model(x)  # (B, num_targets)

# 5. 중요 파장 추출
def grad_cam_band_importance(model, input_tensor, target_index, topk=5):
    """
    model: 학습된 SE_WRN_3D 회귀 모델
    input_tensor: 입력 텐서 (1, 1, D, H, W)
    target_index: 타겟 인덱스 (예: 0=moisture, 1=fat, 2=protein)
    topk: 상위 중요 파장 개수
    """

    # 모델 evaluation 모드
    model.eval()
    
    # gradient 추적을 위해 requires_grad 설정
    input_tensor.requires_grad = True

    # forward pass
    output = model(input_tensor)  # output.shape: (1, num_targets)

    # feature_map에 대한 gradient를 추적하기 위해 retain_grad 호출
    model.feature_map.retain_grad()
    
    # 특정 label(target_index)의 예측값만 선택
    target_output = output[:, target_index]  # shape: (1,)

    # backward 수행: 해당 target_output에 대한 gradient 계산
    model.zero_grad()
    target_output.backward()

    # feature_map: (1, C, D, H, W)
    gradients = model.feature_map.grad  # None 일 가능성 있음
    activations = model.feature_map     # shape: (1, C, D, H, W)

    # 만약 feature_map에서 gradient를 직접 구하지 못했다면 hook 필요
    if gradients is None:
        raise RuntimeError("feature_map에 gradient가 없습니다. .retain_grad()를 호출해야 합니다.")

    # Grad-CAM 공식: weighted sum of feature maps
    # 단일 sample 에 대한 Grad-CAM 계산 위함
    # (1, C, D, H, W) → (C, D, H, W)
    grads = gradients[0]
    acts = activations[0]

    # 파장 축 중요도 계산: gradients 평균을 spatial(H, W)과 channel(C) 축에 대해 평균
    weights = grads.mean(dim=[0, 2, 3])  # shape: (D,) — 파장별 importance
    cam = weights.detach().cpu()

    # top-k band index 추출
    topk_values, topk_indices = torch.topk(cam, k=topk)

    return topk_indices.tolist(), topk_values.tolist()

# 6. 여러 샘플에 대해 중요 파장 빈도 분포 계산
def compute_band_importance_distribution(model, batch_tensor, target_index, topk=5):
    """
    여러 샘플(batch)에 대해 Grad-CAM 기반 중요 파장 빈도 분포 계산
    
    model: 학습된 SE_WRN_3D 모델
    data_tensor: 입력 텐서 (B, 1, D, H, W)
    target_index: 예측할 타겟 인덱스
    topk: 각 샘플당 상위 중요한 파장 개수
    """
    model.eval()
    band_counter = Counter()

    for i in range(batch_tensor.size(0)):
        input_tensor = batch_tensor[i:i+1]  # (1, 1, D, H, W)

        # 반드시 retain_grad 호출 필요 (Grad-CAM 함수 내부에서 grad 얻기 위해)
        input_tensor.requires_grad = True
        model.feature_map = None  # 초기화 (혹시 이전 forward 값 남아 있을 경우 대비)

        # Grad-CAM을 통해 중요 band 추출
        try:
            topk_indices, _ = grad_cam_band_importance(
                model=model,
                input_tensor=input_tensor,
                target_index=target_index,
                topk=topk
            )
            band_counter.update(topk_indices)

        except RuntimeError as e:
            print(f"[Warning] Sample {i} skipped due to error: {e}")

    # 정규화
    total = sum(band_counter.values())
    normalized = {k: v / total for k, v in band_counter.items()}

    return normalized   

# 7. 예시
# 예: x의 앞 32개 샘플 사용
"""
batch_input = x[:32]  # (32, 1, D, H, W)
target_index = 0      # moisture

importance = compute_band_importance_distribution(model, batch_input, target_index, topk=5)

# 결과 출력
import pprint
pprint.pprint(sorted(importance.items()))
"""
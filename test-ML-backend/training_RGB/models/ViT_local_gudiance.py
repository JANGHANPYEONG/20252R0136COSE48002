# custom model

# +
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
import mlflow

# !export PYTHONPATH=$PYTHONPATH:/home/work/tiny-transformers/tiny-transformers
    
# from pycls.models.cnns.resnet import ResNet  # resnet.py에서 ResNet 모델 불러오기

class TeacherModel(nn.Module):
    def __init__(self, model_name='resnext101', version=1):
        super(TeacherModel, self).__init__()
        self.model_name = model_name
        self.version = version
        self.model = None
        self.features = []
        self.feature_layers = ['base_model.base_model.stages.0', 'base_model.base_model.stages.1', 'base_model.base_model.stages.2']

        self._load_pretrained_model()
        
        self.model.eval()
        self._register_hooks()

    def _load_pretrained_model(self):
        model_uri = f"models:/{self.model_name}/{self.version}"
        
        try:
            self.model = mlflow.pytorch.load_model(model_uri)
            print("Teacher model loaded successfully!")
        except mlflow.exceptions.MlflowException as e:
            print(f"Error loading Teacher model: {e}")

    def _register_hooks(self):
        def hook(module, input, output):
            #print("hook ----", output)
            self.features.append(output)

        for name, module in self.model.named_modules():
            # if 'stages.0' in name:
            #     print("name:", name, "module:", module)
            if name in self.feature_layers:
                #print("feature_layer:", name)
                module.register_forward_hook(hook)

    def forward(self, x):
        self.features = []
        output = self.model(x)
        #print("features:",self.features)
        return output, self.features


class StudentModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans, out_dim):
        super(StudentModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=0, in_chans=in_chans)
        self.features = []
        self.feature_layers = ['layers.0', 'layers.1', 'layers.2', 'layers.3']  # Hook SwinTransformerStage blocks
        
        self.mlp_layer = MLP_layer(self.base_model, out_dim)

        self._register_hooks()

    def _register_hooks(self):
        def hook(module, input, output):
            self.features.append(output)

        for name, module in self.base_model.named_modules():
            if name in self.feature_layers:
                module.register_forward_hook(hook)

    def forward(self, x):
        self.features = []
        base_output = self.base_model(x)  # Pass through the base model
        output = self.mlp_layer(base_output)  # Pass through the MLP layer
        return output, self.features


class FeatureTransform(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(FeatureTransform, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)
    
    def forward(self, x):
        # 입력이 [B, H, W, C] 형태라면 [B, C, H, W]로 변환
        # if x.dim() == 4 and x.shape[1] != x.shape[-1]:
        #     x = x.permute(0, 3, 1, 2)
        if x.dim() == 4 and x.shape[2] != x.shape[-1]:
            # [B, H, W, C] -> [B, C, H, W]
            x = x.permute(0, 3, 1, 2)
        
        x = self.conv(x)
        
        
        return x


class DistillationModel(nn.Module):
    def __init__(self, teacher_model, student_model):
        super(DistillationModel, self).__init__()
        self.teacher_model = teacher_model
        self.student_model = student_model
        self.transforms = None  # 초기에는 None으로 설정

    def forward(self, x):
        device = x.device  # Get the device of the input tensor

        with torch.no_grad():
            teacher_output, teacher_features = self.teacher_model(x)  # Teacher features remain frozen.
    
        student_output, student_features = self.student_model(x)  # Student features should be updated.

        # transforms가 아직 초기화되지 않았다면 여기서 초기화
        if self.transforms is None:
            self.transforms = nn.ModuleList()
            for t_feat, s_feat in zip(teacher_features, student_features[:-1]):
                in_channels = s_feat.shape[-1]  # Student feature 채널 수
                out_channels = t_feat.shape[1]  # Teacher feature 채널 수
                transform = FeatureTransform(in_channels, out_channels)
                self.transforms.append(transform.to(device))  # Move the transform to the correct device

        # 손실 및 변환을 동시에 계산
        distillation_loss = torch.tensor(0.0, device=device, requires_grad=True)  # 초기화
        # print(len(student_features[:-1]), len(teacher_features))
        for idx, (transform, s_feat, t_feat) in enumerate(zip(self.transforms, student_features[:-1], teacher_features)):
            # print(f"Layer {idx}: s_feat size before resizing: {s_feat.shape}, t_feat size: {t_feat.shape}")

            transformed_feat = transform(s_feat)  # Transform student feature
            # print(f"Layer {idx}: s_feat size after conv: {transformed_feat.shape}, t_feat size: {t_feat.shape}")
            layer_loss = F.mse_loss(transformed_feat, t_feat)

            # Feature Map 정규화
            #t_feat_normalized = (t_feat - t_feat.mean()) / (t_feat.std() + 1e-8)
            #transformed_feat_normalized = (transformed_feat - transformed_feat.mean()) / (transformed_feat.std() + 1e-8)

            # MSE Loss 계산
            #layer_loss = F.mse_loss(transformed_feat_normalized, t_feat_normalized)

            distillation_loss = distillation_loss + layer_loss
        #print(distillation_loss)
        #distillation_loss = distillation_loss / len(teacher_features)

        return student_output, distillation_loss




# # MLP Layer to output 'out_dim' different outputs
class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim

        # Get the number of features from the base model
        self.num_features = self.base_model.num_features

        # Create MLP heads, one for each output dimension (out_dim = 5 in this case)
        self.mlp_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.num_features, 64),
                nn.ReLU(),
                nn.Linear(64, 1)
            ) for _ in range(out_dim)
        ])

    def forward(self, base_output):
        features = base_output

        # Apply each MLP head to the base model output
        outputs = [head(features) for head in self.mlp_heads]

        # Concatenate the outputs along the last dimension
        return torch.cat(outputs, dim=1)

def create_model(student_model_name, pretrained, num_classes, in_chans, out_dim, config):
    teacher_model_name = config['models']['teacher_model']['name']
    version = config['models']['teacher_model']['version']
    teacher_model = TeacherModel(model_name=teacher_model_name, version=version)
    student_model = StudentModel(model_name=student_model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans, out_dim=out_dim)
    model = DistillationModel(teacher_model, student_model)

    return model
# -





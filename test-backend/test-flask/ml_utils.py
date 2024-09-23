import torch
from torch import nn
from torchvision import transforms, models
from PIL import Image
import mlflow

from opencv_utils import *


def predict_regression_sensory_eval(s3_image_object, meat_id, seqno):    
    # 설정
    image_resize = 256  # 이미지 리사이즈 크기
    input_size = 224    # 입력 이미지 크기
    mean = [0.4834, 0.3656, 0.3474]  # 데이터셋의 mean
    std = [0.2097, 0.2518, 0.2559]   # 데이터셋의 std

    # 전처리 파이프라인 정의
    transform = transforms.Compose([
        transforms.Resize(image_resize),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])
    model_location = "/home/ubuntu/mlflow/regression_model"
    model = serve_mlflow(model_location)

    model.eval()

    # 이미지 불러오기 및 전처리
    try:
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        s3 = boto3.client(
                service_name="s3",
                region_name=os.getenv("S3_REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
        object_key = s3_image_object

        response = s3.get_object(Bucket=s3_bucket, Key=object_key)
        img = Image.open(io.BytesIO(response['Body'].read())).convert("RGB")
        print("Success to create Image Object")
    except Exception as e:
        raise Exception({"msg": f"Fail to create Image Object From S3. {str(e)}"})
    
    image_tensor = transform(img).unsqueeze(0).to(device)  # 배치 차원 추가

    # 예측 수행
    with torch.no_grad():
        output = model(image_tensor)

    # 예측 결과 출력
    predict_result = {}
    predict_data = output.squeeze().tolist()
    
    predict_result["marbling"] = predict_data[0]
    predict_result["color"] = predict_data[0]
    predict_result["texture"] = predict_data[0]
    predict_result["surfaceMoisture"] = predict_data[0]
    predict_result["overall"] = predict_data[0]
    predict_result["xai_imagePath"] = None
    print(f"Predicted values: {predict_result}")
    
    # RDS에 저장 로직 추가하기
    return predict_result


def predict_classification_grade(s3_image_object):
    # 설정
    image_resize = 256  # 이미지 리사이즈 크기
    input_size = 224    # 입력 이미지 크기
    mean = [0.4694, 0.3536, 0.3339] # 데이터셋의 mean과 std 
    std = [0.2051, 0.2459, 0.2498]

    grade_to_label = {0: '1++', 1: '1+', 2: '1', 3: '2', 4: '3'}

    # 전처리 파이프라인 정의
    transform = transforms.Compose([
        transforms.Resize(image_resize),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    model_location = "/home/ubuntu/mlflow/classification_model"
    model = serve_mlflow(model_location)

    model.eval()

    # 이미지 불러오기 및 전처리
    try:
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        s3 = boto3.client(
                service_name="s3",
                region_name=os.getenv("S3_REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
        object_key = s3_image_object

        response = s3.get_object(Bucket=s3_bucket, Key=object_key)
        img = Image.open(io.BytesIO(response['Body'].read())).convert("RGB")
        print("Success to create Image Object")
    except Exception as e:
        raise Exception({"msg": f"Fail to create Image Object From S3. {str(e)}"})
    
    image_tensor = transform(img).unsqueeze(0).to(device)  # 배치 차원 추가

    # 예측 수행
    with torch.no_grad():
        output = model(image_tensor)

    # 예측 결과 처리
    _, predicted_class = torch.max(output, 1)
    predicted_index = predicted_class.item()
    # predicted_grade = grade_to_label[predicted_index]
    grade_data = {}
    grade_data["xai_gradeNum"] = predicted_index
    grade_data["xai_gradeNum_imagePath"] = None
    return grade_data
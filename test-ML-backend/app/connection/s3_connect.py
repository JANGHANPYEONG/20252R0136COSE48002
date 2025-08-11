import boto3  # S3 Server connection
import os
import numpy as np

import cv2

IMAGE_FOLDER_PATH = "./images/"


class S3_:
    def __init__(self,s3_bucket_name,service_name,region_name,aws_access_key_id,aws_secret_access_key):
        self.bucket = s3_bucket_name  # 버킷 지정
        # self.folder = ["meats","qr_codes"]  # 저장할 폴더 지정
        try:
            self.s3 = boto3.client(
                service_name=service_name,
                region_name=region_name,  # 버킷 region
                aws_access_key_id=aws_access_key_id,  # 액세스 키 ID
                aws_secret_access_key=aws_secret_access_key  # 비밀 액세스 키
            )
        except Exception as e:
            print(e)
        else:
            print("S3 Bucket Connected!")

    def server2s3(self, type, item_id):
        """
        Flask server -> S3 Database
        Params
        1. type : "meats" or "qr_codes"
        2. item_id: meat.id (육류 관리번호)

        Return 
        1. True: 전송 성공
        2. False: 전송 실패
        """
        local_folder_path = os.path.join(IMAGE_FOLDER_PATH, type)
        local_filename = f"{item_id}.png"
        local_filepath = os.path.join(local_folder_path, local_filename)
        if self.put_object(self.bucket, local_filepath, f"{type}/{local_filename}"):
            os.remove(local_filepath)
            return True
        else:
            print(f"No such file in Flask Server: {type}/{item_id}.png")
            return False
        
    def get_object(self, bucket, object_key):
        try:
            response = self.s3.get_object(Bucket=bucket, Key=object_key)
            data = response['Body'].read()  # Read the entire content of the object
            return data  # Return the binary data
        except Exception as e:
            print(f"Error downloading image from S3: {e}")
            return None
        
    def download_image(self, object_key):
        """S3에서 이미지를 다운로드하고 OpenCV 이미지로 변환 (최적화 버전)"""
        try:
            # 스트리밍 응답 사용
            response = self.s3.get_object(Bucket=self.bucket, Key=object_key)
            stream = response['Body']
            
            # 스트림에서 직접 이미지 디코딩
            file_bytes = np.asarray(bytearray(stream.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError(f"Failed to decode image: {object_key}")
            
            return image
        except Exception as e:
            print(f"Error downloading image from S3: {e}")
            return None

    def put_object(self, bucket, filepath, access_key):  # (S3 <- Server) Upload Pic
        """
        s3 bucket에 지정 파일 업로드
        :param bucket: 버킷명
        :param filepath: 파일 위치 - 올릴 파일
        :param access_key: 저장 파일명
        :return: 성공 시 True, 실패 시 False 반환
        """
        try:
            self.s3.upload_file(
                Filename=filepath,  # 업로드할 파일 경로
                Bucket=bucket,
                Key=access_key,  # 업로드할 파일의 S3 내 위치와 이름을 나타낸다.
                ExtraArgs={"ContentType": "image/png", "ACL": "public-read"},
                # ContentType 파일 형식 jpg로 설정
                # ACL: 파일에 대한 접근 권한 설정
                # public-read, private, public-read-write, authenticated-read
            )
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
        return True

    def get_image_url(self, bucket, filename):  # (S3 -> Server) Download Pic
        """
        :param bucket: 연결된 버킷명
        :param filename: s3에 저장된 파일 명
        """
        location = self.s3.get_bucket_location(Bucket=bucket)["LocationConstraint"]
        return f"https://{bucket}.s3.{location}.amazonaws.com/{filename}.png"

    def update_image(self, new_filepath, id, folder):
        # 1. 기존 파일 path
        old_filename = f"{folder}/{id}.png"

        # 2. 기존 파일 삭제
        self.delete_image(id, folder)

        # 3. 새 파일 업로드
        success = self.put_object(self.bucket, new_filepath, old_filename)
        if not success:
            print(f"Failed to upload new image for meat ID: {id}")

        # 4. 성공했는지 못했는지 반환
        return success

    def delete_image(self, folder, id):
        if folder == 'qr_codes':
            old_filename = f"{folder}/{id}"
        else:
            old_filename = f"{id}"
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=old_filename)
            print(f"Delete Image {old_filename} successfully")
        except Exception as e:
            print(f"Delete Image {old_filename} failed")

    def get_files_with_id(self, folder, id):
        """
        주어진 폴더에서 id로 시작하는 파일 리스트를 반환합니다.
        
        :param folder: 폴더 경로
        :param id: 파일 이름의 id 부분 (왼쪽의 id)
        :return: 일치하는 파일 목록
        """
        matching_files = []
        continuation_token = None
        
        while True:
            # list_objects_v2 호출 (계속되는 요청을 위한 continuation_token 처리)
            list_args = {
                'Bucket': self.bucket,
                'Prefix': f'{folder}/',  # 폴더 경로 지정
                'Delimiter': '/'
            }
            if continuation_token:
                list_args['ContinuationToken'] = continuation_token

            response = self.s3.list_objects_v2(**list_args)
            
            if 'Contents' in response:
                # 파일 리스트에서 id로 시작하는 파일 필터링
                for item in response['Contents']:
                    file_key = item['Key']
                    # id 부분이 왼쪽에 있는지 확인
                    if file_key.startswith(f'{folder}/{id}-'):
                        matching_files.append(file_key)
            
            # 다음 페이지가 있는지 확인
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
        
        return matching_files
    
    def upload_fileobj(self, file_obj, bucket, key):
        """
        S3 버킷에 파일 객체를 업로드합니다.
        :param file_obj: 파일 객체 (BytesIO 등)
        :param bucket: 업로드할 S3 버킷 이름
        :param key: S3 내에서 파일의 위치 및 이름
        :return: 업로드 성공 시 True, 실패 시 False 반환
        """
        try:
            self.s3.upload_fileobj(
                Fileobj=file_obj,  # 업로드할 파일 객체
                Bucket=bucket,  # 버킷 이름
                Key=key,  # S3 내의 파일 경로 및 이름
                ExtraArgs={"ContentType": "image/png", "ACL": "public-read"},
            )
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

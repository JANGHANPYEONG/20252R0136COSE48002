import boto3  # S3 Server connection
import os
from datetime import datetime  # 시간 출력용

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
        old_filename = f"{folder}/{id}.png"
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=old_filename)
            print(f"Delete Image {old_filename} successfully")
        except Exception as e:
            print(f"Delete Image {old_filename} failed")

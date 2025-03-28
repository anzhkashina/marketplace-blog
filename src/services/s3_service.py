import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
from fastapi import HTTPException
import os

# Загрузка переменных окружения из файла .env
load_dotenv()


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("MINIO_URL"),
            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        )
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.create_bucket()

    def create_bucket(self):
        try:
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            logging.info(f"Bucket '{self.bucket_name}' created successfully.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                logging.warning(f"Bucket '{self.bucket_name}' already exists.")
            else:
                logging.error(f"Failed to create bucket '{self.bucket_name}': {e}")
        except NoCredentialsError:
            logging.error("Credentials not available.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def upload_image(
        self,
        file,
        file_name,
        endpoint_url,
    ):
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, file_name)
            return f"{endpoint_url}/{self.bucket_name}/{file_name}"
        except NoCredentialsError:
            raise HTTPException(status_code=400, detail="Credentials not available")

    def get_image_url(self, file_name, endpoint_url):
        return f"{endpoint_url}/{self.bucket_name}/{file_name}"

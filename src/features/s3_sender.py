import boto3
import json
from PIL import Image
from dotenv import load_dotenv
import os

aws_access_key_id = os.getenv('env_aws_access_key_id')
aws_secret_access_key = os.getenv('env_aws_secret_access_key')

class S3SENDER:
    """Sends data to AWS S3 bucket"""

    def __init__(self, user_email: str, bucket: str):

        self.text = ''

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.user_email = user_email
        self.bucket = bucket

        self.s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-1',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def send_image(self, file_dir: str, image_name: str) -> None:
        """Sends image from file_dir"""

        self.get_image_format(file_dir)
        self.s3.Bucket(self.bucket).upload_file(file_dir, Key=image_name)

        
    def get_image_format(self, file_dir: str) -> None:
        """Gets image format"""
        
        image = Image.open(file_dir)
        self.img_format = image.format
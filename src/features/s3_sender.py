import boto3
import json
from PIL import Image


class S3SENDER:
    """Sends data to AWS S3 bucket"""

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, user_email: str, bucket: str):

        self.img_format = ''
        self.text = ''
        self.prefix = ''

        self.create_new_request = True
        self.result = False
        self.request_id = 1

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.user_email = user_email
        self.bucket = bucket

        self.s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-2',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

        self.check_path()

    def send_image(self, file_dir: str, image_name: str) -> None:
        """Sends image from file_dir"""

        self.get_image_format(file_dir)
        self.s3.Bucket(self.bucket).upload_file(file_dir, Key=self.prefix + '/' + image_name)

    def check_path(self) -> None:
        """Checks if directory in bucket already exists.
        Creates new path if one already exists.
        bucket -> email directory -> request_id directory."""

        self.prefix = self.user_email + '/' + 'request' + str(self.request_id)

        for object_summary in self.s3.Bucket(self.bucket).objects.filter(Prefix=self.prefix):
            self.request_id += 1
            self.check_path()
            break

    def get_image_format(self, file_dir: str) -> None:
        """Gets image format"""
        
        image = Image.open(file_dir)
        self.img_format = image.format
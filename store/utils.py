import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class ArvanImageUploadMixin:
    def upload_image_to_arvan(self, image_field, folder=''):
        endpoint_url = os.getenv('ARVAN_ENDPOINT')
        access_key = os.getenv('ARVAN_ACCESS_KEY')
        secret_key = os.getenv('ARVAN_SECRET_KEY')
        bucket = os.getenv('ARVAN_BUCKET')

        if not image_field:
            return None

        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        image_field.open('rb')
        key = f"{folder}/{os.path.basename(image_field.name)}" if folder else os.path.basename(image_field.name)
        s3.upload_fileobj(
            image_field,
            bucket,
            key,
            ExtraArgs={'ACL': 'public-read'}
        )
        image_field.close()

        url = f"{endpoint_url}/{bucket}/{key}"
        return url 
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

endpoint_url = os.getenv('ARVAN_ENDPOINT')
access_key = os.getenv('ARVAN_ACCESS_KEY')
secret_key = os.getenv('ARVAN_SECRET_KEY')
bucket = os.getenv('ARVAN_BUCKET')

s3 = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

with open('test.jpg', 'rb') as f:
    s3.upload_fileobj(f, bucket, 'products/test_upload.jpg', ExtraArgs={'ACL': 'public-read'})

print("آپلود تستی انجام شد.")
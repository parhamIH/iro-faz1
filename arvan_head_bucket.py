import boto3
import logging
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

# بارگذاری متغیرهای محیطی
load_dotenv()

endpoint_url = os.getenv('ARVAN_ENDPOINT')
access_key = os.getenv('ARVAN_ACCESS_KEY')
secret_key = os.getenv('ARVAN_SECRET_KEY')
bucket_name = os.getenv('ARVAN_BUCKET')

try:
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
except Exception as exc:
    logging.error(exc)
else:
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]

        if status == 404:
            logging.warning("Missing object, %s", errcode)
        elif status == 403:
            logging.error("Access denied, %s", errcode)
        else:
            logging.exception("Error in request, %s", errcode)
    else:
        print("دسترسی به باکت برقرار است.")
        print(response)
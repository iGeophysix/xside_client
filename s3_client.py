"""
S3 client to load data and save data
"""
import io
import logging

import boto3
import lz4.block
from botocore.exceptions import ClientError
from settings import AWS_S3_ENDPOINT_URL as S3_HOST, AWS_STORAGE_BUCKET_NAME as S3_BUCKET, \
    AWS_S3_ACCESS_KEY_ID as S3_USER, AWS_S3_SECRET_ACCESS_KEY as S3_PASSWORD

logger = logging.getLogger('s3_client')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

S3 = boto3.resource('s3',
                    endpoint_url=S3_HOST,
                    aws_access_key_id=S3_USER,
                    aws_secret_access_key=S3_PASSWORD, )


def compress_file(data: bytes) -> bytes:
    """Compress data"""
    return lz4.block.compress(data, mode='high_compression')


def decompress_file(data: bytes) -> bytes:
    """Decompress data"""
    return lz4.block.decompress(data)


def save_to_s3(path: str, data: bytes, compress: bool = False) -> None:
    """
    Save binary content to S3
    :param path: full path to the file in the bucket
    :param data: binary content to save
    :param compress: compress data before saving to s3
    :return:
    """
    if compress:
        f = io.BytesIO(compress_file(data))
    else:
        f = io.BytesIO(data)

    bucket = S3.Bucket(S3_BUCKET)

    try:
        bucket.upload_fileobj(f, path)
    except ClientError as e:
        logging.error(e)

    f.close()


def list_from_s3(path: str = 'raw_data') -> list:
    """
    Get list of files by prefix
    example: list_from_s3('raw_data')
    :param path: prefix
    :return: list of files with full path
    """
    bucket = S3.Bucket(S3_BUCKET)
    files = [obj.key for obj in bucket.objects.filter(Prefix=path)]
    return files


def load_from_s3(path: str, decompress: bool = False) -> bytes:
    """
    Load binary content from s3
    :param path: full path to the file in the bucket
    :param decompress: decompress data after loading from s3
    :return: byte-string
    """
    try:
        response = S3.Object(S3_BUCKET, path).get()
        if decompress:
            return decompress_file(response['Body'].read())
        else:
            return response['Body'].read()
    except ClientError as e:
        logger.error(e)


def move_on_s3(path: str, new_path: str) -> None:
    """Move file from one folder on s3 to another"""
    S3.Object(S3_BUCKET, new_path).copy_from(CopySource=f'{S3_BUCKET}/{path}')
    S3.Object(S3_BUCKET, path).delete()

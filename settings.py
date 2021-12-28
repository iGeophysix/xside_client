import logging
import os

XSIDE_HOST = os.environ.get("XSIDE_HOST", "http://192.168.1.80:8000")
XSIDE_USER = os.environ.get("XSIDE_USER", "svcModule@svcmodule.com")
XSIDE_PASSWORD = os.environ.get("XSIDE_PASS", "testPassword")

AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'https://storage.yandexcloud.net')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'xside')
AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID', 'sQu2CtP5NrfZ8QV6_dNv')
AWS_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_S3_SECRET_ACCESS_KEY')

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', 'media')

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

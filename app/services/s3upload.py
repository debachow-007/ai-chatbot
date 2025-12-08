import boto3
from uuid import uuid4
from app.config import settings
import mimetypes
from urllib.parse import urlparse

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_KEY,
    aws_secret_access_key=settings.AWS_SECRET
)

def upload_to_s3(file_bytes, filename, folder="portfolio"):
    file_type, _ = mimetypes.guess_type(filename)

    key = f"chatbot/{folder}/{uuid4()}-{filename}"
    s3.put_object(
        Bucket=settings.AWS_BUCKET,
        Key=key,
        Body=file_bytes,
        # ACL="public-read",
        ContentType=file_type or "image/png"   # fallback
    )
    return f"https://{settings.AWS_BUCKET}.s3.amazonaws.com/{key}"

def delete_from_s3(key: str):
    s3.delete_object(
        Bucket=settings.AWS_BUCKET, 
        Key=key
    )
    return True

def extract_key_from_url(url: str) -> str:
    parsed = urlparse(url)
    # Remove leading slash from path
    return parsed.path.lstrip("/")
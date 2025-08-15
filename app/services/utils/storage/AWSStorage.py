"""S3 blob storage connection"""
# External dependencies
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Built-in dependencies
import os
import io
import io
# Client dependencies
from app.services.utils.storage.Storage import Storage

load_dotenv()


class AWSStorage(Storage):
    def __init__(self):
        self.storage = boto3.client("s3", 
                                      aws_access_key_id=os.getenv("S3_ACCESS_KEY"), 
                                      aws_secret_access_key=os.getenv("S3_SECRET"), 
                                      region_name=os.getenv("AWS_REGION")
        )
        self.bucket = os.getenv("S3_BUCKET")

    def get(self, filename):
        """Get a file from the blob storage"""
        try:
            response = self.storage.get_object(Bucket=self.bucket, Key=filename)
        except Exception:
            # File wasn't found
            return False, False
        return io.BytesIO(response["Body"].read()), response["ContentType"]

    def delete(self, file):
        """Delete a file from the blob storage"""
        pass

    def upload(self, file, object_name):
        """Upload a file to the blob storage"""
        if not object_name:
            object_name = file.name
        try:
            # Restart the file stream
            file.seek(0)
            self.storage.upload_fileobj(file, self.bucket, object_name)
        except ClientError:
            return False
        return True
        
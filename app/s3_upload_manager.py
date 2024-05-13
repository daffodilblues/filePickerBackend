import boto3
from fastapi import HTTPException


class S3UploadManager():
    def __init__(self, user_id):
        self.user_id = user_id
        self.bucket_name = "file-picker-attachments"
        self.s3 = boto3.resource('s3')
        self.s3_bucket = self.s3.Bucket(self.bucket_name)

    def upload_file(self, file_id, content, mime_type):
        object_key = f"{self.user_id}/{file_id}"
        try:
            self.s3_bucket.put_object(Key=object_key, Body=content, ContentType=mime_type)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed with error: {str(e)}")

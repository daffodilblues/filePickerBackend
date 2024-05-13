from fastapi import APIRouter, HTTPException, Request, Query
import requests
from app.transformation_manager import TransformationManager
from app.s3_upload_manager import S3UploadManager

class ProcessedFileUploadManager:
    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token
        self.transformation_manager = TransformationManager()
        self.s3_upload_manager = S3UploadManager(self.user_id)

    def is_folder(mime_type):
        return mime_type == "application/vnd.google-apps.folder"

    def determine_export_format(mime_type):
        if mime_type == "application/vnd.google-apps.document":
            return "text/plain"
        elif mime_type == "application/vnd.google-apps.spreadsheet":
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif mime_type == "application/vnd.google-apps.presentation":
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        else:
            return None

    def __list_files_in_folder(self, folder_id):
        url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=files(id, name, mimeType)"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('files', [])
        else:
            raise HTTPException(status_code=response.status_code, detail="Error listing folder contents")

    def __download_and_process_file(self, file_data):
        mime_type = file_data['mimeType']
        file_id = file_data['id']
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
        if mime_type.startswith("application/vnd.google-apps."):
            # Handle Google Docs types with export
            export_format = ProcessedFileUploadManager.determine_export_format(mime_type)
            download_url += f"/export?mimeType={export_format}"
            # raise HTTPException(status_code=400, detail="Not a google drive file")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        download_file_response = requests.get(download_url, headers=headers)
        if download_file_response.status_code != 200:
            raise HTTPException(status_code=download_file_response.status_code, detail="Error downloading file")

        if mime_type == "application/vnd.google-apps.document":
            file_content = download_file_response.text
        else:
            file_content = download_file_response.content

        transformed_content = self.transformation_manager.apply_transformations(mime_type, file_content)
        # Upload to S3
        self.s3_upload_manager.upload_file(file_id, transformed_content, mime_type)


    def process_and_upload(self, file_id):
        # Get file metadata to determine if it's a folder or file
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=id,name,mimeType"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error getting file metadata")

        file_data = response.json()
        mime_type = file_data['mimeType']

        if ProcessedFileUploadManager.is_folder(mime_type):
            # It's a folder, list and process each item within
            files = self.__list_files_in_folder(file_id)
            for file in files:
                self.process_and_upload(file['id'])  # Recursive call
        else:
            # Process the file based on its MIME type
            self.__download_and_process_file(file_data)


    
import argparse
import os
from functools import cache

# from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# SERVICE_ACCT_GDRIVE_PATH_PREFIX = "service_acct_accessible/"
# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveUploader:
    # class variables
    folder_id_cache = {}
    credentials = None

    @classmethod
    def authenticate(cls, credential_file_path):
        """
        Uses credential file to authenticate with Google Drive API.

        There are two ways to authenticate:
        1. Service Account File 
        - recommended for server-side applications
        - especially useful for automation without user interaction
        2. OAuth2 Client ID
        - requires signing into in the browser and passing a consent screen
        """

        # NOTE: service account method is currently broken!
        # creds = service_account.Credentials.from_service_account_file(
        #     credential_file_path, 
        #     scopes=SCOPES
        # )
        if cls.credentials:
            return cls.credentials

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credential_file_path,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        cls.credentials = creds
        return creds


    @staticmethod
    def get_folder_id(service, folder_name, parent_folder_id=None):
        # Search for the folder in the current parent directory
        # query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)",
            pageSize=10
        ).execute()

        items = results.get('files', [])
        if items:
            # If the folder exists, return its ID
            return items[0]['id']
        else:
            # If the folder doesn't exist, create it
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            return folder['id']


    @classmethod
    def traverse_and_create_folders(cls, service, path):
        # exclude the file name
        folders = path.split('/')[:-1]
        parent_id = None
        cache_dict = cls.folder_id_cache
        for folder in folders:  
            if folder in cache_dict:
                parent_id = cache_dict[folder]["id"]
            else:
                parent_id = cls.get_folder_id(service, folder, parent_id)
                cache_dict[folder] = {
                    "id": parent_id,
                    "children": {},
                }
                cache_dict = cache_dict[folder]["children"]
        return parent_id


    @classmethod
    def upload_file(cls, file_path, destination_path, credential_file):
        creds = cls.authenticate(credential_file)
        service = build('drive', 'v3', credentials=creds)
        
        # Traverse or create folders
        parent_folder_id = cls.traverse_and_create_folders(service, destination_path)

        # Extract the file name from the destination path
        file_name = destination_path.split('/')[-1]
        
        # Upload the file
        file_metadata = {'name': file_name}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')
        return file_id


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psr.add_argument("file_path", type=str, help="Path to the file to upload")
    psr.add_argument("destination_path", type=str, help="Destination path in Google Drive")
    psr.add_argument(
        "--credential_file", "-c",
        type=str,
        default="credentials.json",
        help="Path to the credential file"
    )
    # NOTE: service account method is currently broken!
    # psr.add_argument("--use_client_id", action="store_true", help="Use OAuth2 Client ID for authentication instead of Service Account")
    args = psr.parse_args()

    file_id = GoogleDriveUploader.upload_file(
        args.file_path, 
        args.destination_path,
        args.credential_file,
    )

    print(f"File uploaded with ID: {file_id}")

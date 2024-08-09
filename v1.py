import argparse
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_folder_id(service, folder_name, parent_folder_id=None):
    # Search for the folder in the current parent directory
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
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


def traverse_and_create_folders(service, path):
    folders = path.split('/')
    parent_id = None

    for folder in folders[:-1]:  # Exclude the last part (the file name)
        parent_id = get_folder_id(service, folder, parent_id)

    return parent_id


def upload_file_to_drive(file_path, destination_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    # Traverse or create folders
    parent_folder_id = traverse_and_create_folders(service, destination_path)
    print(f'Parent folder ID: {parent_folder_id}')
    
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
    psr.add_argument('file_path', type=str, help='Path to the file to upload')
    psr.add_argument('destination_path', type=str, help='Destination path in Google Drive')
    args = psr.parse_args()

    upload_file_to_drive(args.file_path, args.destination_path)

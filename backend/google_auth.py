from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Path to the client secret JSON file
credentials_path = "client_secret.json"

# Scopes define the level of access to Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Access to files created/opened by the app


def authenticate_google_account():
    """
    Authenticate the user and retrieve OAuth 2.0 credentials.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=8501)
        return creds
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None


def get_drive_service():
    """
    Create a Google Drive API service using authenticated credentials.
    """
    creds = authenticate_google_account()
    if creds:
        try:
            drive_service = build('drive', 'v3', credentials=creds)
            return drive_service
        except Exception as e:
            print(f"Error initializing Drive service: {e}")
            return None
    else:
        print("Failed to authenticate")
        return None


def upload_to_drive(file_path, file_name):
    """
    Upload a file to Google Drive.
    :param file_path: The local path to the file to be uploaded.
    :param file_name: The name to be given to the file in Google Drive.
    """
    try:
        service = get_drive_service()
        if not service:
            raise Exception("Google Drive service initialization failed.")

        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, resumable=True)

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"File uploaded successfully. File ID: {uploaded_file.get('id')}")
        return uploaded_file.get('id')
    except Exception as e:
        print(f"Error uploading file to Google Drive: {e}")
        return None

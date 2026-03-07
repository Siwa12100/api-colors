import os
import definitions
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials



class GoogleDriveService:
    def __init__(self):
        self._SCOPES=['https://www.googleapis.com/auth/drive']
        _credential_path = os.path.join(definitions.ROOT_PROJECT, 'credential.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _credential_path

    def build(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), self._SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    
    def is_connected(self) -> bool:
        """
        Vérifie que la connexion à Google Drive fonctionne.
        """
        try:
            service = self.build()
            service.files().list(pageSize=1).execute()
            return True
        except Exception:
            return False
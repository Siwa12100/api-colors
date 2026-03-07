import os
import pytest
from app.services.g_drive_service import GoogleDriveService


@pytest.mark.integration
def test_google_drive_real_connection():
    """
    Test réel contre Google Drive.
    Nécessite un credential.json valide.
    """

    # Vérifie que le fichier existe
    credential_path = os.path.join(os.path.dirname(__file__), '../credential.json')
    assert os.path.exists(credential_path), "credential.json introuvable"

    service = GoogleDriveService()

    # Si ça plante → le test échoue
    assert service.is_connected() is True

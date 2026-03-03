from flask import Blueprint

from app.service.g_drive_service import GoogleDriveService

images_bp = Blueprint("images", __name__, url_prefix="/api/images")

# INFO : 
# list of metadata fields : https://developers.google.com/drive/api/v3/reference/files#resource

# ---------- GET all ----------
@images_bp.route("", methods=["GET"])
def get_images():
    """Récupérer toutes les images."""
    selected_fields = "files(id, name, fileExtension, hasThumbnail, thumbnailLink, size, imageMediaMetadata, webContentLink, webViewLink, description, createdTime, modifiedTime)" 
    g_drive_service = GoogleDriveService().build()
    list_file = g_drive_service.files().list(fields=selected_fields).execute()
    #for file in list_file:
        # logic insertion
    return {"files": list_file.get("files")}

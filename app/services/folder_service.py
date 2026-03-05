# app/services/folder_service.py
from app.extensions import db
from app.models.folder import Folder
from app.models.picture import Picture


class FolderService:

    @staticmethod
    def get_folders_children(folder_id):
        return Folder.query.filter_by(parent_folder_id=folder_id).order_by(Folder.id).all()

    @staticmethod
    def get_pictures(folder, page, per_page):
        return (
            Picture.query
            .filter(Picture.id.in_([pic.id for pic in folder.pictures]))
            .order_by(Picture.id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def create(name, workspace_id, parent_folder_id=None):
        folder = Folder(
            name=name,
            workspace_id=workspace_id,
            parent_folder_id=parent_folder_id,
        )
        db.session.add(folder)
        db.session.commit()
        return folder

    @staticmethod
    def update(folder, data):
        folder.name = data.get("name", folder.name)
        db.session.commit()
        return folder

    @staticmethod
    def delete(folder):
        db.session.delete(folder)
        db.session.commit()

    @staticmethod
    def check_duplicate(name, workspace_id, parent_folder_id):
        return Folder.query.filter_by(
            name=name,
            workspace_id=workspace_id,
            parent_folder_id=parent_folder_id
        ).first() is not None

    @staticmethod
    def validate_parent(parent, workspace_id):
        return parent.workspace_id == workspace_id
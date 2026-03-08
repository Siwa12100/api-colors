from app.extensions import db
from app.models.workspace import WorkSpace
from app.models.picture import Picture
from app.models.folder import Folder
from app.models.datasource import DataSource


class WorkspaceService:

    @staticmethod
    def get_by_user(user_id, page, per_page):
        return (
            WorkSpace.query
            .filter_by(user_id=user_id)
            .order_by(WorkSpace.id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def create_default(user_id):
        all_source_ids = [ds.id for ds in DataSource.query.all()]
        ws = WorkSpace(
            user_id=user_id,
            name="Mon Workspace",
            isSystem=True,
            favorites=[],
            sources=all_source_ids,
        )
        db.session.add(ws)
        db.session.commit()
        return ws
    
    @staticmethod
    def get_or_create_default(user_id):
        ws = WorkSpace.query.filter_by(user_id=user_id).first()
        if not ws:
            ws = WorkspaceService.create_default(user_id)
        return ws

    @staticmethod
    def get_pictures(ws, page, per_page):
        return (
            Picture.query
            .filter(Picture.datasource_id.in_(ws.sources))
            .order_by(Picture.id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def get_folders(workspace_id, page, per_page):
        return (
            Folder.query
            .filter_by(workspace_id=workspace_id, parent_folder_id=None)
            .order_by(Folder.id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def update(ws, data):
        ws.name = data.get("name", ws.name)
        ws.favorites = data.get("favorites", ws.favorites)
        ws.sources = data.get("sources", ws.sources)
        db.session.commit()
        return ws
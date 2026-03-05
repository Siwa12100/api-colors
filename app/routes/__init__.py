from app.routes.authentication import auth_bp
from app.routes.pictures import pictures_bp
from app.routes.tags import tags_bp

__all__ = ["pictures_bp", "tags_bp", "auth_bp"]

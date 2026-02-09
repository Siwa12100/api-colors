from datetime import datetime, timezone
from app.extensions import db


class Color(db.Model):
    __tablename__ = "colors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    hex_code = db.Column(db.String(7), nullable=False)  # ex: #FF5733
    rgb_r = db.Column(db.Integer, nullable=False)
    rgb_g = db.Column(db.Integer, nullable=False)
    rgb_b = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Color {self.name} ({self.hex_code})>"

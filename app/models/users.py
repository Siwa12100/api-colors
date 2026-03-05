"""
SQLAlchemy model for the 'users' table.

This table acts as a WHITELIST: only emails pre-registered
by an administrator can log in via Google OAuth.
"""

from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    """
    Each row represents an authorized user.
    An admin must first create the entry (with the email)
    BEFORE the user can log in via Google.
    """

    __tablename__ = "users"

    # ---- Columns ----

    # Unique auto-incremented identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Email is the verification key: it must be unique
    email = db.Column(db.String(255), nullable=False, unique=True)

    # Full name retrieved from the Google profile
    # (filled automatically on first login)
    full_name = db.Column(db.String(255), nullable=True)

    # The user's role: "admin" or "user"
    # By default, a newly authorized user gets the "user" role
    role = db.Column(db.String(50), nullable=False, default="user")

    # Is this user active?
    # An admin can disable an account without deleting it
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Date the entry was added to the whitelist
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Date of the last login via Google
    last_login_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.email} (role={self.role})>"
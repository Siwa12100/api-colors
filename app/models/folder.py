from app.extensions import db

picture_folder = db.Table(
    "picture_folder",
    db.Column("folder_id", db.BigInteger, db.ForeignKey("folder.id"), primary_key=True),
    db.Column("picture_id", db.BigInteger, db.ForeignKey("picture.id"), primary_key=True),
)

class Folder(db.Model):
    __tablename__ = "folder"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspace.id"), nullable=False)
    parent_folder_id = db.Column(
        db.BigInteger,
        db.ForeignKey("folder.id", ondelete="CASCADE"),
        nullable=True
    )

    children = db.relationship(
        "Folder",
        backref=db.backref("parent", remote_side=[id]),
        lazy="select",
        cascade="all, delete-orphan",
    )
    pictures = db.relationship("Picture", secondary=picture_folder, backref=db.backref("folders", lazy=True), lazy="select")

    def to_dict(self):
        return {
            "id":               self.id,
            "name":             self.name,
            "workspace_id":     self.workspace_id,
            "parent_folder_id": self.parent_folder_id,
            "pictures":         [pic.id for pic in self.pictures],
        }

    def __repr__(self):
        return f"<Folder : {self.name}>"
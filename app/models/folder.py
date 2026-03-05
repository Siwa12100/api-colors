from app.extensions import db

class Folder(db.Model):
    __tablename__ = "folder"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    workspaceId = db.Column(db.BigInteger, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Folder : {self.name}>"
from app.extensions import db

class ImageLocation(db.Model):
    __tablename__ = "imageLocation"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    folderId = db.Column(db.BigInteger, nullable=False)
    imageId = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<ImageLocation : {self.imageId}>"

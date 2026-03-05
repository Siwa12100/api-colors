from app.extensions import db

class PictureRatio(db.Model):
    __tablename__ = "pictureRatio" 

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ratioX = db.Column(db.Integer, nullable=False)
    ratioY = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<PictureRatio : ({self.ratioX},{self.ratioY})>"
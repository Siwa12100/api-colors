from app.extensions import db

class WorkSpace(db.Model):
    __tablename__ = "workspace"

    id = db.Column(db.BigInteger, primary_key = True, autoincrement=True)
    userId = db.Column(db.ARRAY(db.BigInteger), nullable=False)
    favorites = db.Column(db.ARRAY(db.BigInteger), nullable=False)
    isSystem = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    sources = db.Column(db.ARRAY(db.BigInteger), nullable=False)

    def __repr__(self):
        return f"<WorkSpace : {self.name}"
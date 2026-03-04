from app.extensions import db
class TagSystem(db.Model):
    __tablename__ = "tagSystem"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    color = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f"<TagSystem : {self.name}>"
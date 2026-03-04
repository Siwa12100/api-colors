from app.extensions import db
class TagCustom(db.Model):
    __tablename__ = "tagCustom"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    color = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f"<TagCustom : {self.name}>"
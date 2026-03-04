from app.extensions import db

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    rights = db.Column(db.ARRAY(db.BigInteger), nullable=False)

    def __repr__(self):
        return f"<Users : {self.name}>"

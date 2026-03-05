from app.extensions import db

class Admin(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Admin : {self.name}>"
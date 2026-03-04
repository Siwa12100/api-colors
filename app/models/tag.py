from app.extensions import db


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    hex_code = db.Column(db.String(7), nullable=False)  # ex: #FF5733

    def create(self, **kwargs):
        self.name=kwargs.get("name")
        self.hex_code=kwargs.get("hex_code")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "hex_code": self.hex_code,
        }

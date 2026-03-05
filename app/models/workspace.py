from app.extensions import db

class WorkSpace(db.Model):
    __tablename__ = "workspace"

    id = db.Column(db.BigInteger, primary_key = True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    favorites = db.Column(db.ARRAY(db.BigInteger), nullable=False)
    isSystem = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    sources = db.Column(db.ARRAY(db.BigInteger), nullable=False)

    def __repr__(self):
        return f"<WorkSpace : {self.name}"
    
    def to_dict(self):
        return {
            "id":        self.id,
            "user_id":   self.user_id,
            "name":      self.name,
            "isSystem":  self.isSystem,
            "favorites": self.favorites if self.favorites else [],
            "sources":   self.sources if self.sources else [],
        }
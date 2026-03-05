from app.extensions import db

class UserRights(db.Model):
    __tablename__ = "userRights"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    workspaceId = db.Column(db.BigInteger, nullable=False)
    readOnly = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<UserRights :\nUserId : {self.id}\nWorkSpaceId : {self.workspaceId}\nReadOnly : {self.readOnly}>"
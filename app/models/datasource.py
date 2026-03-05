from app.extensions import db

class DataSource(db.Model): 
    __tablename__ = "datasource"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

from app.extensions import db
import enum
class OrientationEnum(enum.db.Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    
class Picture(db.Model):
    __tablename__ = "picture"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    tagsSystem = db.Column(db.ARRAY(db.BigInteger), nullable=False)
    tagsCustom = db.Column(db.ARRAY(db.BigInteger), nullable=False)
    mainColors = db.Column(db.ARRAY(db.String(6)), nullable=False)
    orientation = db.Column(db.Enum(OrientationEnum), nullable=False)
    ratio = db.Column(db.BigInteger, nullable=False)
    resolutionX = db.Column(db.BigInteger, nullable=False)
    resolutionY = db.Column(db.BigInteger, nullable=False)
    contrast = db.Column(db.Integer, nullable=False)
    luminosity = db.Column(db.Integer, nullable=False)
    hasTest = db.Column(db.Boolean, nullable=False)
    isOutside = db.Column(db.Boolean, nullable=True)
    downloadLink = db.Column(db.String(510), nullable=False)
    lastUpdated = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    sources = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<Picture : {self.name}>"






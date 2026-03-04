from app.extensions import db
from app.models.tag import Tag
import enum

class OrientationEnum(enum.Enum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"

picture_tag = db.Table(
    "picture_tag",
    db.Column("picture_id", db.BigInteger, db.ForeignKey("picture.id"), primary_key=True),
    db.Column("tag_id", db.BigInteger, db.ForeignKey("tag.id"), primary_key=True),
)

class Picture(db.Model):
    __tablename__ = "picture"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    google_id = db.Column(db.String(510), nullable=False)
    name = db.Column(db.String, nullable=False)
    comment = db.Column(db.String(510), nullable=True)

    # - - - Tags - - - 
    tags = db.relationship(
        "Tag",
        secondary=picture_tag,
        backref=db.backref("pictures", lazy=True),
        lazy="select"
    )

    # - - - Visual data - - -
    mainColors = db.Column(db.ARRAY(db.String(6)), nullable=False)
    orientation = db.Column(
        db.Enum(OrientationEnum, name="format_enum"),
        nullable=False
    )
    ratio = db.Column(db.BigInteger, nullable=False)
    resolutionX = db.Column(db.BigInteger, nullable=False)
    resolutionY = db.Column(db.BigInteger, nullable=False)
    contrast = db.Column(db.Integer, nullable=False)
    luminosity = db.Column(db.Integer, nullable=False)

    # - - - Link - - -
    downloadLink = db.Column(db.String(510), nullable=False)
    thumbnailLink = db.Column(db.String(510), nullable=False)

    # - - - Other - - -
    lastUpdated = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    sources = db.Column(db.BigInteger, nullable=False)

    def create(self, **kwargs):
        self.name=kwargs.get("name")
        self.comment=kwargs.get("comment")
        self.google_id=kwargs.get("google_id")
        self.tags=kwargs.get("tags")
        self.mainColors=kwargs.get("mainColors")
        self.orientation=kwargs.get("orientation")
        self.ratio=kwargs.get("ratio")
        self.resolutionX=kwargs.get("resolutionX")
        self.resolutionY=kwargs.get("resolutionY")
        self.contrast=kwargs.get("contrast")
        self.luminosity=kwargs.get("luminosity")
        self.thumbnailLink=kwargs.get("thumbnailLink")
        self.downloadLink=kwargs.get("downloadLink")
        self.lastUpdated=kwargs.get("lastUpdated")
        self.sources=kwargs.get("sources")

    def to_dict(self):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "name": self.name,
            "comment": self.comment,
            "tags": [tag.to_dict() for tag in self.tags], 
            "thumbnailLink": self.thumbnailLink,
            "downloadLink": self.downloadLink,
            "lastUpdated": self.lastUpdated
        }

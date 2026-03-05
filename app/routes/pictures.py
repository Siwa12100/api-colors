from app.models.picture import Picture, OrientationEnum
from app.models.tag import Tag
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.service.g_drive_service import GoogleDriveService

pictures_bp = Blueprint("pictures", __name__, url_prefix="/api/pictures")

# INFO : 
# list of metadata fields : https://developers.google.com/drive/api/v3/reference/files#resource

@pictures_bp.route("/upload", methods=["GET"])
def upload_pictures():
    """Met toutes les images de la source google_drive en bd."""
    selected_fields = "files(id, name, hasThumbnail, thumbnailLink, size, imageMediaMetadata, webContentLink, webViewLink, modifiedTime)" 
    g_drive_service = GoogleDriveService().build()
    list_file = g_drive_service.files().list(fields=selected_fields).execute()

    for file in list_file["files"]:
        # Prevent duplicates
        if Picture.query.filter_by(google_id=file.get("id")).first():
            return jsonify({"error": "Cette image existe déjà"}), 409
    
        if (file.get("hasThumbnail", False) == False):
            break

        picture_width = file.get("imageMediaMetadata").get("width")
        picture_height = file.get("imageMediaMetadata").get("height")
        picture_orientation = OrientationEnum.PORTRAIT
        if (abs(picture_width - picture_height) < 10):
            picture_orientation = OrientationEnum.SQUARE
        elif (picture_width >= picture_height):
            picture_orientation = OrientationEnum.LANDSCAPE

        image = Picture()
        image.create(
            name=file.get("name"),
            comment=None,
            google_id=file.get("id"),
            tags=[],
            mainColors=[],
            ratio=0,
            orientation=picture_orientation,
            resolutionY=picture_height,
            resolutionX=picture_width,
            contrast=0,
            luminosity=0,
            thumbnailLink=file.get("thumbnailLink"),
            downloadLink=file.get("webContentLink"),
            lastUpdated=file.get("modifiedTime"),
            sources=0,
        )
        db.session.add(image)
        db.session.commit()

    res = db.session.execute(db.select(Picture)).scalars()

    list_file_name = []
    cmp = 0
    for ress in res:
        list_file_name.append(ress.name)
        cmp += 1

    return  {"files": list_file_name, "size": cmp}

# ---------- GET all with filter ----------
@pictures_bp.route("", methods=["GET"])
def get_pictures():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Picture.query

    # Picture data
    name = request.args.get("name")
    if name:
        query = query.filter(Picture.name.ilike(f"%{name}%"))

    comment = request.args.get("comment")
    if comment:
        query = query.filter(Picture.comment.ilike(f"%{comment}%"))

    # Picture Size/Resolution
    min_width = request.args.get("min_width", type=int)
    if min_width is not None:
        query = query.filter(Picture.resolutionX >= min_width)

    max_width = request.args.get("max_width", type=int)
    if max_width is not None:
        query = query.filter(Picture.resolutionX <= max_width)

    min_height = request.args.get("min_height", type=int)
    if min_height is not None:
        query = query.filter(Picture.resolutionY >= min_height)

    max_height = request.args.get("max_height", type=int)
    if max_height is not None:
        query = query.filter(Picture.resolutionY <= max_height)

    orientation = request.args.get("orientation", type=str)
    if orientation:
        query = query.filter(Picture.orientation == orientation)

    # Picture tags
    tags = request.args.get("tags")
    if tags:
        for tag_id in tags:
            query = Picture.query.join(Picture.tags).filter(Tag.id == tag_id).all()

    # Picture Visual
    main_colors = request.args.get("mainColors")
    if main_colors:
        colors = main_colors.split(",")
        query = query.filter(Picture.mainColors.overlap(colors))

    updated_after = request.args.get("updated_after")
    if updated_after:
        query = query.filter(Picture.lastUpdated >= updated_after)

    pagination = query.order_by(Picture.id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "data": [picture.to_dict() for picture in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


# ---------- GET one ----------
@pictures_bp.route("/<int:picture_id>", methods=["GET"])
def get_picture(picture_id):
    picture = db.session.get(Picture, picture_id)
    if not picture:
        return jsonify({"error": "Image introuvable"}), 404

    return jsonify(picture.to_dict()), 200

# ---------- PUT ----------
@pictures_bp.route("/<int:picture_id>", methods=["PUT"])
def add_tag(picture_id):
    picture = db.session.get(Picture, picture_id)
    if not picture:
        return jsonify({"error": "Image introuvable"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    picture.name = data.get("name", picture.name)
    picture.comment = data.get("comment", picture.comment)
    
    tag_ids = data.get("tags")
    if tag_ids is not None:
        picture.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.commit()

    return jsonify(picture.to_dict()), 200
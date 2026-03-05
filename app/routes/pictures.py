from flask import Blueprint, jsonify, request

from app.models.picture import Picture
from app.services.picture_service import PictureService
from app.utils.api_request import get_or_404, get_pagination_params, pagination_to_dict

pictures_bp = Blueprint("pictures", __name__, url_prefix="/api/pictures")

# INFO : 
# list of metadata fields : https://developers.google.com/drive/api/v3/reference/files#resource

# ---------- UPLOAD from Google Drive ----------
@pictures_bp.route("/upload", methods=["GET"])
def upload_pictures():
    cmp_pictures_added = PictureService.upload_from_drive()
    return jsonify({"pictures_added_count": cmp_pictures_added}), 200

# ---------- GET all with filters ----------
@pictures_bp.route("", methods=["GET"])
def get_pictures():
    page, per_page = get_pagination_params()

    query = PictureService.build_filter_query(request.args)
    pagination = query.order_by(Picture.id).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(pagination_to_dict(pagination)), 200

# ---------- GET one ----------
@pictures_bp.route("/<int:picture_id>", methods=["GET"])
def get_picture(picture_id):
    picture, err, code = get_or_404(Picture, picture_id, "Image introuvable")
    if err:
        return err, code

    return jsonify(picture.to_dict()), 200

# ---------- PUT ----------
@pictures_bp.route("/<int:picture_id>", methods=["PUT"])
def update_picture(picture_id):
    picture, err, code = get_or_404(Picture, picture_id, "Image introuvable")
    if err:
        return err, code

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    picture = PictureService.update(picture, data)

    return jsonify(picture.to_dict()), 200
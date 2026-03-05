from flask import Blueprint, request, jsonify

from app.models.tag import Tag
from app.services.tag_service import TagService
from app.utils.api_request import get_or_404, get_pagination_params, pagination_to_dict


tags_bp = Blueprint("tags", __name__, url_prefix="/api/tags")

# ---------- GET all ----------
@tags_bp.route("", methods=["GET"])
def get_tags():
    page, per_page = get_pagination_params()
    pagination = TagService.get_all(page, per_page)

    return jsonify(pagination_to_dict(pagination)), 200



# ---------- GET one ----------
@tags_bp.route("/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    tag, err, code = get_or_404(Tag, tag_id, "Tag introuvable")
    if err:
        return err, code

    return jsonify(tag.to_dict()), 200

# ---------- POST ----------
@tags_bp.route("", methods=["POST"])
def create_tag():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    name     = data.get("name")
    hex_code = data.get("hex_code")

    if not name or not hex_code:
        return jsonify({"error": "name and hex_code are required"}), 400

    if TagService.check_duplicate(name):
        return jsonify({"error": "This tag already exists"}), 409

    tag = TagService.create(name, hex_code)

    return jsonify(tag.to_dict()), 201


# ---------- PUT ----------
@tags_bp.route("/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    tag, err, code = get_or_404(Tag, tag_id, "Tag introuvable")
    if err:
        return err, code

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    tag = TagService.update(tag, data)

    return jsonify(tag.to_dict()), 200


# ---------- DELETE ----------
@tags_bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    tag, err, code = get_or_404(Tag, tag_id, "Tag introuvable")
    if err:
        return err, code

    TagService.delete(tag)

    return jsonify({"message": f"Tag '{tag.name}' supprimée"}), 200
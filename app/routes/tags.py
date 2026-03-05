from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.tag import Tag

tags_bp = Blueprint("tags", __name__, url_prefix="/api/tags")

# ---------- GET all ----------
@tags_bp.route("", methods=["GET"])
def get_tags():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = Tag.query.order_by(Tag.id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "data": [tag.to_dict() for tag in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


# ---------- GET one ----------
@tags_bp.route("/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    tag = db.session.get(Tag, tag_id)
    if not tag:
        return jsonify({"error": "Tag introuvable"}), 404

    return jsonify(tag.to_dict()), 200


# ---------- POST ----------
@tags_bp.route("", methods=["POST"])
def create_tag():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    name = data.get("name")
    hex_code = data.get("hex_code")

    if not name or not hex_code:
        return jsonify({"error": "name and hex_code are required"}), 400

    # Prevent duplicates
    if Tag.query.filter_by(name=name).first():
        return jsonify({"error": "This tag already exists"}), 409

    tag = Tag()
    tag.create(name=name, hex_code=hex_code)

    db.session.add(tag)
    db.session.commit()

    return jsonify(tag.to_dict()), 201


# ---------- PUT ----------
@tags_bp.route("/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    tag = db.session.get(Tag, tag_id)
    if not tag:
        return jsonify({"error": "Tag introuvable"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400


    tag.name = data.get("name", tag.name)
    tag.hex_code = data.get("hex_code", tag.hex_code)

    db.session.commit()

    return jsonify(tag.to_dict()), 200


# ---------- DELETE ----------
@tags_bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    tag = db.session.get(Tag, tag_id)
    if not tag:
        return jsonify({"error": "Tag introuvable"}), 404

    db.session.delete(tag)
    db.session.commit()

    return jsonify({"message": f"Tag '{tag.name}' supprimée"}), 200

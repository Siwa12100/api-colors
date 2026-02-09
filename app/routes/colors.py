from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.extensions import db
from app.models.color import Color
from app.schemas.color_schema import ColorSchema, ColorCreateSchema

colors_bp = Blueprint("colors", __name__, url_prefix="/api/colors")

color_schema = ColorSchema()
colors_schema = ColorSchema(many=True)
color_create_schema = ColorCreateSchema()


# ---------- GET all ----------
@colors_bp.route("", methods=["GET"])
def get_colors():
    """Récupérer toutes les couleurs."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = Color.query.order_by(Color.id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "colors": colors_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


# ---------- GET one ----------
@colors_bp.route("/<int:color_id>", methods=["GET"])
def get_color(color_id):
    """Récupérer une couleur par son ID."""
    color = db.session.get(Color, color_id)
    if not color:
        return jsonify({"error": "Couleur introuvable"}), 404

    return jsonify(color_schema.dump(color)), 200


# ---------- POST ----------
@colors_bp.route("", methods=["POST"])
def create_color():
    """Créer une nouvelle couleur."""
    try:
        data = color_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if Color.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Cette couleur existe déjà"}), 409

    color = Color(**data)
    db.session.add(color)
    db.session.commit()

    return jsonify(color_schema.dump(color)), 201


# ---------- PUT ----------
@colors_bp.route("/<int:color_id>", methods=["PUT"])
def update_color(color_id):
    """Mettre à jour une couleur existante."""
    color = db.session.get(Color, color_id)
    if not color:
        return jsonify({"error": "Couleur introuvable"}), 404

    try:
        data = color_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    color.name = data["name"]
    color.hex_code = data["hex_code"]
    color.rgb_r = data["rgb_r"]
    color.rgb_g = data["rgb_g"]
    color.rgb_b = data["rgb_b"]

    db.session.commit()

    return jsonify(color_schema.dump(color)), 200


# ---------- DELETE ----------
@colors_bp.route("/<int:color_id>", methods=["DELETE"])
def delete_color(color_id):
    """Supprimer une couleur."""
    color = db.session.get(Color, color_id)
    if not color:
        return jsonify({"error": "Couleur introuvable"}), 404

    db.session.delete(color)
    db.session.commit()

    return jsonify({"message": f"Couleur '{color.name}' supprimée"}), 200

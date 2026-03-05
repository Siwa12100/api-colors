from flask import request, jsonify
from app.extensions import db

def get_or_404(model, id, message):
    obj = db.session.get(model, id)
    if not obj:
        return None, jsonify({"error": message}), 404
    return obj, None, None


def get_pagination_params():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    return page, per_page

def pagination_to_dict(pagination):
    return {
        "data": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }
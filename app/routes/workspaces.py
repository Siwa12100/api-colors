from flask import Blueprint, request, jsonify

from app.models.workspace import WorkSpace
from app.models.user import User
from app.services.workspace_service import WorkspaceService
from app.utils.api_request import get_or_404, get_pagination_params, pagination_to_dict

workspaces_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")


# ---------- GET all ----------
@workspaces_bp.route("", methods=["GET"])
def get_workspaces():
    page, per_page = get_pagination_params()
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    pagination = WorkspaceService.get_by_user(user_id, page, per_page)

    if pagination.total == 0:
        user, err, code = get_or_404(User, user_id, "Utilisateur introuvable")
        if err:
            return err, code
        WorkspaceService.create_default(user_id)
        pagination = WorkspaceService.get_by_user(user_id, page, per_page)

    return jsonify(pagination_to_dict(pagination)), 200


# ---------- GET one ----------
@workspaces_bp.route("/<int:workspace_id>", methods=["GET"])
def get_workspace(workspace_id):
    ws, err, code = get_or_404(WorkSpace, workspace_id, "Workspace introuvable")
    if err:
        return err, code

    return jsonify(ws.to_dict()), 200

# ---------- GET pictures by workspace ----------
@workspaces_bp.route("/<int:workspace_id>/pictures", methods=["GET"])
def get_workspace_pictures(workspace_id):
    ws, err, code = get_or_404(WorkSpace, workspace_id, "Workspace introuvable")
    if err:
        return err, code

    if not ws.sources:
        return jsonify({"data": [], "total": 0}), 200

    page, per_page = get_pagination_params()
    pagination = WorkspaceService.get_pictures(ws, page, per_page)

    return jsonify(pagination_to_dict(pagination)), 200

# ---------- GET folders by workspace ----------
@workspaces_bp.route("/<int:workspace_id>/folders", methods=["GET"])
def get_workspace_folders(workspace_id):
    ws, err, code = get_or_404(WorkSpace, workspace_id, "Workspace introuvable")
    if err:
        return err, code

    page, per_page = get_pagination_params()
    pagination = WorkspaceService.get_folders(workspace_id, page, per_page)

    return jsonify(pagination_to_dict(pagination)), 200

# ---------- PUT ----------
@workspaces_bp.route("/<int:workspace_id>", methods=["PUT"])
def update_workspace(workspace_id):
    ws, err, code = get_or_404(WorkSpace, workspace_id, "Workspace introuvable")
    if err:
        return err, code

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    ws = WorkspaceService.update(ws, data)

    return jsonify(ws.to_dict()), 200
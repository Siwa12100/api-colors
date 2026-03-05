from flask import Blueprint, request, jsonify

from app.models.folder import Folder
from app.models.workspace import WorkSpace
from app.services.folder_service import FolderService
from app.utils.api_request import get_pagination_params, pagination_to_dict, get_or_404

folders_bp = Blueprint("folders", __name__, url_prefix="/api/folders")


# ---------- GET one ----------
@folders_bp.route("/<int:folder_id>", methods=["GET"])
def get_folder(folder_id):
    folder, err, code = get_or_404(Folder, folder_id, "Folder introuvable")
    if err: 
        return err, code

    return jsonify(folder.to_dict()), 200


# ---------- GET images of a folder ----------
@folders_bp.route("/<int:folder_id>/pictures", methods=["GET"])
def get_folder_images(folder_id):
    folder, err, code = get_or_404(Folder, folder_id, "Folder introuvable")
    if err:
        return err, code

    page, per_page = get_pagination_params()
    pagination = FolderService.get_pictures(folder, page, per_page)

    return jsonify(pagination_to_dict(pagination)), 200

# ---------- GET children folders ----------
@folders_bp.route("/<int:folder_id>/folders", methods=["GET"])
def get_children_folders(folder_id):
    folder, err, code = get_or_404(Folder, folder_id, "Folder introuvable")
    if err:
        return err, code

    children = FolderService.get_folders_children(folder_id)

    return jsonify({
        "data": [f.to_dict() for f in children],
        "total": len(children),
    }), 200

# ---------- POST ----------
@folders_bp.route("", methods=["POST"])
def create_folder():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    name             = data.get("name")
    workspace_id     = data.get("workspace_id")
    parent_folder_id = data.get("parent_folder_id")

    if not name or not workspace_id:
        return jsonify({"error": "name and workspace_id are required"}), 400

    ws, err, code = get_or_404(WorkSpace, workspace_id, "Workspace introuvable")
    if err:
        return err, code

    if parent_folder_id:
        parent, err, code = get_or_404(Folder, parent_folder_id, "Folder parent introuvable")
        if err:
            return err, code
        if not FolderService.validate_parent(parent, workspace_id):
            return jsonify({"error": "Le folder parent n'appartient pas à ce workspace"}), 400

    if FolderService.check_duplicate(name, workspace_id, parent_folder_id):
        return jsonify({"error": "Ce folder existe déjà dans ce workspace"}), 409

    folder = FolderService.create(name, workspace_id, parent_folder_id)

    return jsonify(folder.to_dict()), 201

# ---------- PUT ----------
@folders_bp.route("/<int:folder_id>", methods=["PUT"])
def update_folder(folder_id):
    folder, err, code = get_or_404(Folder, folder_id, "Folder introuvable")
    if err:
        return err, code

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    folder = FolderService.update(folder, data)

    return jsonify(folder.to_dict()), 200


# ---------- DELETE ----------
@folders_bp.route("/<int:folder_id>", methods=["DELETE"])
def delete_folder(folder_id):
    folder, err, code = get_or_404(Folder, folder_id, "Folder introuvable")
    if err:
        return err, code

    FolderService.delete(folder)

    return jsonify({"message": f"Folder '{folder.name}' supprimé"}), 200
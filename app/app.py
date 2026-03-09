import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import config_by_name
from app.routes import pictures_bp, tags_bp, workspaces_bp, folders_bp, auth_bp


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    config = config_by_name.get(config_name)
    if config is None:
        raise ValueError(f"Config inconnue : {config_name}")

    config.validate()
    app.config.from_object(config)

<<<<<<< Updated upstream
    # ✅ CORS totalement ouvert
    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)
=======
    # Activer CORS pour que le frontend Angular puisse appeler l'API
    CORS(app, origins=["http://localhost:4200"], supports_credentials=True)

    db.init_app(app)    
>>>>>>> Stashed changes
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(pictures_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(workspaces_bp)
    app.register_blueprint(folders_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return jsonify({"name": "Colors API", "version": "1.0"})

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Ressource introuvable"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Erreur interne du serveur"}), 500

    return app





# Ouais c'est dégueux de tout commenter comme ça et alors ????


# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from app.extensions import db, migrate
# from app.config import config_by_name
# from app.routes import pictures_bp, tags_bp, workspaces_bp, folders_bp, auth_bp

# def create_app(config_name=None):
#     app = Flask(__name__)

#     if config_name is None:
#         config_name = os.getenv("FLASK_ENV", "development")

#     config = config_by_name.get(config_name)
#     if config is None:
#         raise ValueError(f"Config inconnue : {config_name}")

#     # Validation seulement au moment de créer l'app, pas à l'import
#     config.validate()

#     app.config.from_object(config)

#     # Activer CORS pour que le frontend Angular puisse appeler l'API
#     CORS(app, 
#         origins=["http://localhost:4200", "https://colors.valorium-mc.fr"], 
#         supports_credentials=True,
#         allow_headers=["Authorization", "Content-Type"],
#         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         always_send=True
#     )

#     @app.after_request
#     def after_request(response):
#         origin = request.headers.get('Origin')
#         allowed = ["http://localhost:4200", "https://colors.valorium-mc.fr"]
#         if origin in allowed:
#             response.headers['Access-Control-Allow-Origin'] = origin
#         response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
#         response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
#         response.headers['Access-Control-Allow-Credentials'] = 'true'
#         return response

#     db.init_app(app)    
#     migrate.init_app(app, db)
    
#     # Register blueprints
#     app.register_blueprint(pictures_bp)
#     app.register_blueprint(tags_bp)
#     app.register_blueprint(workspaces_bp)
#     app.register_blueprint(folders_bp)
#     app.register_blueprint(auth_bp)

#     @app.route("/")
#     def index():
#         return jsonify({"name": "Colors API", "version": "1.0"})

#     with app.app_context():
#         db.create_all()

#     @app.errorhandler(404)
#     def not_found(error):
#         return jsonify({"error": "Ressource introuvable"}), 404

#     @app.errorhandler(500)
#     def internal_error(error):
#         return jsonify({"error": "Erreur interne du serveur"}), 500
    
#     @app.errorhandler(500)
#     def internal_error(error):
#         response = jsonify({"error": "Erreur interne du serveur"})
#         origin = request.headers.get('Origin')
#         allowed = ["http://localhost:4200", "https://colors.valorium-mc.fr"]
#         if origin in allowed:
#             response.headers['Access-Control-Allow-Origin'] = origin
#             response.headers['Access-Control-Allow-Credentials'] = 'true'
#         return response, 500

#     return app
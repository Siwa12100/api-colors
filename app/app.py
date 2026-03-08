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

    # Validation seulement au moment de créer l'app, pas à l'import
    config.validate()

    app.config.from_object(config)

    # Activer CORS pour que le frontend Angular puisse appeler l'API
    CORS(app, 
     origins=["http://localhost:4200"], 
     supports_credentials=True,
     # pour désactiver le preflight qui bloque qu'on a le front en localhost et
     # l'api en prod # TODO : on peut le suppr quand le dev sera finis
     allow_headers=["Authorization", "Content-Type"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # pour désactiver le preflight qui bloque qu'on a le front en localhost et
    # l'api en prod # TODO : on peut le suppr quand le dev sera finis
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    db.init_app(app)    
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
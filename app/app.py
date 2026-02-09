from flask import Flask, jsonify
from app.extensions import db


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///colors.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import colors_bp
    app.register_blueprint(colors_bp)

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



# from flask import Flask
# from app.extensions import db, migrate
# from app.config import Config

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app)
#     migrate.init_app(app, db)

#     from app.routes import colors_bp
#     app.register_blueprint(colors_bp)

#     return app

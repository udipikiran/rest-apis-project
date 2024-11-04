import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api

from blocklist import BLOCKLIST
from db import db
from resources.items import blp as ItemBluePrint
from resources.stores import blp as StoreBluePrint
from resources.tags import blp as TagBluePrint
from resources.user import blp as UserBluePrint


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.1.0"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URI", "sqlite:///data.db"
    )
    db.init_app(app)
    migrate = Migrate(app, db)

    # Below 2 lines are not required since we are using flak-migrate
    # with app.app_context():
    #     db.create_all()

    api = Api(app)
    app.config["JWT_SECRET_KEY"] = "242748319268838638903465221410414972388"
    # secrets.SystemRandom().getrandbits(128)
    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def fresh_token_callback(jwt_header, jwt_payload):
        return jsonify(
            {"description": "The token is not fresh", "error": "fresh token required"}
        )

    @jwt.token_in_blocklist_loader
    def check_token_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify(
            {"message": "The token has been revoked", "error": "Revoked token"}
        )

    @jwt.additional_claims_loader
    def addition_claims_callback(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired", "error": "token expired"})

    @jwt.invalid_token_loader
    def invalid_token_callbakc(error):
        return jsonify(
            {"message": "Signature verification failed", "error": "Invalid token"}
        )

    @jwt.unauthorized_loader
    def unauthorized_token_callback(error):
        return jsonify(
            {
                "description": "request doesn't contain access token",
                "error": "unauthorized request",
            }
        )

    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)

    return app

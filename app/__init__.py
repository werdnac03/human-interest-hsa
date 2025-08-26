from flask import Flask, request
from .config import Config
from .extensions import db, migrate
from .blueprints.accounts import bp as accounts_bp
from .blueprints.users import bp as users_bp
from .blueprints.cards import bp as cards_bp
from .blueprints.transactions import bp as tx_bp
from .blueprints.funding import bp as fd_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(accounts_bp, url_prefix="/accounts")
    app.register_blueprint(cards_bp, url_prefix="/cards")
    app.register_blueprint(tx_bp, url_prefix="/transactions")
    app.register_blueprint(fd_bp, url_prefix="/funding")

    @app.get("/")
    def index():
        return "HSA"

    return app

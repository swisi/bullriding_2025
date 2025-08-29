import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask import request
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'main.login'  # Hier 'main.login' statt 'login'
csrf = CSRFProtect()

def create_app(config_class=Config):
    # Load .env for local development; does not override existing env by default
    load_dotenv(override=False)

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Basic config validation: require SECRET_KEY in production
    if app.config.get('FLASK_ENV') == 'production' and not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY must be set in production environment')

    # Ensure SQLite directory exists (for local dev without Docker)
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri.startswith('sqlite:///'):
        db_path = uri.replace('sqlite:///', '', 1)
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    # Ensure upload folder exists
    try:
        os.makedirs(app.config.get('UPLOAD_FOLDER', ''), exist_ok=True)
    except Exception:
        pass

    from app import routes, models
    app.register_blueprint(routes.bp)

    @app.context_processor
    def inject_site_name():
        return {"site_name": app.config.get("SITE_NAME", "Mechanical Bullriding")}

    @app.context_processor
    def inject_theme():
        theme = request.cookies.get("theme")
        if theme not in ("dark", "light"):
            theme = None
        return {"theme": theme}

    return app

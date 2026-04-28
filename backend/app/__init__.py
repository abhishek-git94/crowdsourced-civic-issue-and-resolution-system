import os
from flask import Flask
from flask_login import LoginManager
from .config import Config
from .database import init_db
from .models import User

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    init_db(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.objects(id=user_id).first()
        except Exception:
            return None

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.issues import issues_bp
    from .routes.admin import admin_bp
    from .routes.api import api_bp
    from .routes.main import main_bp
    from .routes.forum import forum_bp
    from .routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(chat_bp)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create database tables (optional, usually handled by migrations)
    # Base.metadata.create_all(bind=engine)

    return app

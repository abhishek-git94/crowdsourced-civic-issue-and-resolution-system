import os
from flask import Flask
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from .config import Config
from .database import init_db
from .models import User

login_manager = LoginManager()
oauth = OAuth()

def create_app(config_class=Config):
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    frontend_dir = os.path.join(base_dir, 'frontend')
    app = Flask(__name__, 
                template_folder=os.path.join(frontend_dir, 'templates'),
                static_folder=os.path.join(frontend_dir, 'static'))
    app.config.from_object(config_class)

    # Initialize extensions
    init_db(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    oauth.init_app(app)
    



    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=os.environ.get("GOOGLE_CLIENT_ID", "mock_client_id"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", "mock_client_secret"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

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


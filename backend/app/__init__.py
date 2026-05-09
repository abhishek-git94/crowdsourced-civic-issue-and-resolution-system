import os
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

from .config import Config
from .database import init_db
from .models import User

import firebase_admin
from firebase_admin import credentials
import logging

cred_path = os.path.join(os.path.dirname(__file__), 'firebase-adminsdk.json')
if os.path.exists(cred_path):
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logging.info("Firebase Admin initialized securely.")
    except Exception as e:
        logging.warning(f"Firebase Admin SDK init failed: {e}")
else:
    logging.info("firebase-adminsdk.json not found. Running Firebase Auth in DEV mode.")

login_manager = LoginManager()
oauth = OAuth()

def create_app(config_class=Config):
    import os
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, supports_credentials=True)


    # Initialize extensions
    init_db(app)
    login_manager.init_app(app)
    
    # Handle JSON for unauthorized requests
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, jsonify
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

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
    
    # Mobile API Authentication - Stateless support
    @login_manager.request_loader
    def request_loader(request):
        user_id = request.headers.get('X-User-ID')
        if user_id:
            try:
                user = User.objects(id=user_id).first()
                if user:
                    return user
            except Exception:
                pass
        return None

    # Ensure session is populated if using headers (backward compatibility for some routes)
    @app.before_request
    def sync_session():
        from flask import session
        from flask_login import current_user
        if current_user.is_authenticated and 'user_id' not in session:
            session['user_id'] = str(current_user.id)
            session['user_name'] = current_user.name
            session['user_role'] = current_user.role

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

    # Modern Admin Dashboard (Indore Portal) - Serve as static
    from flask import send_from_directory
    @app.route('/admin-portal/')
    @app.route('/admin-portal/<path:path>')
    def serve_admin_portal(path='index.html'):
        admin_dir = os.path.abspath(os.path.join(app.root_path, '../../admin_dashboard'))
        return send_from_directory(admin_dir, path)

    # Create database tables (optional, usually handled by migrations)
    # Base.metadata.create_all(bind=engine)

    return app
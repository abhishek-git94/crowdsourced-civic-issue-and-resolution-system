from functools import wraps
from flask import abort, request, jsonify
from flask_login import current_user

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                    return jsonify({"success": False, "message": f"Required role: {role}"}), 403
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

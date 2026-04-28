import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from .issues import ai_analyzer

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/analyze-image", methods=["POST"])
def analyze_image_api():
    try:
        file = request.files.get("image")
        location = request.form.get("location", "Unknown")
        if not file:
            return jsonify({"error": "No image provided"}), 400

        filename = f"tmp_{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        result = ai_analyzer.analyze_civic_issue(path, location)
        if not isinstance(result, dict):
            return jsonify({"error": "Analyzer returned unexpected result"}), 500
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("analyze-image error")
        return jsonify({"error": str(e)}), 500

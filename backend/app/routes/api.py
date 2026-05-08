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

        from ..models import Issue
        existing_issues = Issue.objects()[:50]

        result = ai_analyzer.analyze_civic_issue(path, location, existing_issues)
        if not isinstance(result, dict):
            return jsonify({"error": "Analyzer returned unexpected result"}), 500
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("analyze-image error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/analyze-text", methods=["POST"])
def analyze_text_api():
    try:
        text = request.json.get("text", "")
        location = request.json.get("location", "Unknown")
        
        if not text:
            return jsonify({"error": "No text provided"}), 400

        from ..services.advanced_ai import analyze_sentiment, smart_assign_department, predict_resolution_days
        
        sentiment = analyze_sentiment(text)
        dept, dept_conf = smart_assign_department(None, text, [])
        predicted_days = predict_resolution_days(None, "Medium")
        
        return jsonify({
            "text": text,
            "sentiment": sentiment['sentiment'],
            "urgency_score": sentiment['urgency_score'],
            "detected_keywords": sentiment['detected_keywords'],
            "recommended_department": dept,
            "department_confidence": dept_conf,
            "predicted_resolution_days": predicted_days
        })
    except Exception as e:
        current_app.logger.exception("analyze-text error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/cluster-issues", methods=["GET"])
def cluster_issues_api():
    try:
        from ..models import Issue
        from ..services.advanced_ai import cluster_issues
        
        issues = Issue.objects()[:100]
        clusters = cluster_issues(issues, similarity_threshold=0.7)
        
        return jsonify({
            "clusters": clusters,
            "total_clusters": len(clusters),
            "unclustered_count": len(issues) - sum(c['count'] for c in clusters)
        })
    except Exception as e:
        current_app.logger.exception("cluster-issues error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/detect-anomalies", methods=["GET"])
def detect_anomalies_api():
    try:
        from ..models import Issue
        from ..services.advanced_ai import detect_anomalies
        
        issues = Issue.objects()[:500]
        result = detect_anomalies(issues)
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("detect-anomalies error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/natural-query", methods=["POST"])
def natural_query_api():
    try:
        query = request.json.get("query", "")
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        from ..models import Issue
        from ..services.advanced_ai import natural_language_query
        
        issues = Issue.objects()[:200]
        result = natural_language_query(issues, query)
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("natural-query error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/compare-images", methods=["POST"])
def compare_images_api():
    try:
        before_file = request.files.get("before_image")
        after_file = request.files.get("after_image")
        
        if not before_file or not after_file:
            return jsonify({"error": "Both images required"}), 400
        
        import cv2
        import numpy as np
        
        before_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"before_{datetime.now().timestamp()}_" + secure_filename(before_file.filename))
        after_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"after_{datetime.now().timestamp()}_" + secure_filename(after_file.filename))
        
        before_file.save(before_path)
        after_file.save(after_path)
        
        before_img = cv2.imread(before_path)
        after_img = cv2.imread(after_path)
        
        if before_img is None or after_img is None:
            return jsonify({"error": "Could not read images"}), 400
        
        before_gray = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after_img, cv2.COLOR_BGR2GRAY)
        
        before_hist = cv2.calcHist([before_gray], [0], None, [256], [0, 256])
        after_hist = cv2.calcHist([after_gray], [0], None, [256], [0, 256])
        
        hist_diff = cv2.compareHist(before_hist, after_hist, cv2.HISTCMP_CORREL)
        
        if hist_diff > 0.85:
            resolution_status = "Resolved"
            confidence = round(hist_diff * 100, 1)
        elif hist_diff > 0.6:
            resolution_status = "Partially Resolved"
            confidence = round(hist_diff * 100, 1)
        else:
            resolution_status = "Not Resolved"
            confidence = round((1 - hist_diff) * 100, 1)
        
        os.remove(before_path)
        os.remove(after_path)
        
        return jsonify({
            "resolution_status": resolution_status,
            "confidence": confidence,
            "similarity_score": round(hist_diff, 3)
        })
    except Exception as e:
        current_app.logger.exception("compare-images error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/user/stats", methods=["GET"])
def get_user_stats():
    try:
        from flask import request
        user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        from ..models import Issue
        from datetime import datetime, timedelta
        
        user_issues = Issue.objects(user=user_id) if user_id else []
        
        reported = len(user_issues)
        resolved = len([i for i in user_issues if 'Resolved' in (i.status or '')])
        pending = len([i for i in user_issues if i.status == 'Pending'])
        upvotes = sum([i.upvotes or 0 for i in user_issues])
        
        return jsonify({
            "reported": reported,
            "resolved": resolved,
            "pending": pending,
            "upvotes": upvotes
        })
    except Exception as e:
        current_app.logger.exception("user-stats error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/notifications", methods=["GET"])
def get_notifications():
    try:
        from flask import request
        user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Demo notifications - in production, store in database
        notifications = [
            {"id": "1", "type": "status", "title": "Issue Status Updated", "message": "Your reported pothole has been marked as In Progress", "time": "2 hours ago", "read": False},
            {"id": "2", "type": "system", "title": "Welcome to Jan Suvidha", "message": "Start reporting civic issues in your area", "time": "1 day ago", "read": True},
        ]
        
        return jsonify({"notifications": notifications})
    except Exception as e:
        current_app.logger.exception("notifications error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/forum/posts", methods=["GET", "POST"])
def forum_posts():
    try:
        from flask import request
        
        if request.method == "GET":
            # Demo posts
            posts = [
                {"id": "1", "title": "Best way to report water leakage?", "author": "Rahul S.", "replies": 5, "time": "2h ago"},
                {"id": "2", "title": "Road repair update - Sector 15", "author": "Admin", "replies": 12, "time": "5h ago"},
                {"id": "3", "title": "Garbage collection timing", "author": "Priya M.", "replies": 3, "time": "1d ago"},
            ]
            return jsonify({"posts": posts})
        
        # POST - create new post
        data = request.json
        new_post = {
            "id": str(datetime.now().timestamp()),
            "title": data.get("title", ""),
            "author": "User",
            "replies": 0,
            "time": "Just now"
        }
        return jsonify({"success": True, "post": new_post})
    except Exception as e:
        current_app.logger.exception("forum error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/search", methods=["GET"])
def search_issues():
    try:
        query = request.args.get("q", "")
        category = request.args.get("category", "")
        status = request.args.get("status", "")
        
        from ..models import Issue
        
        issues = Issue.objects()
        
        if query:
            issues = Issue.objects(issue__icontains=query) | Issue.objects(location__icontains=query)
        if category:
            issues = issues.filter(category=category)
        if status:
            issues = issues.filter(status=status)
        
        results = []
        for i in issues[:50]:
            results.append({
                "id": str(i.id),
                "issue": i.issue,
                "location": i.location,
                "status": i.status,
                "category": i.category,
                "severity": i.severity,
                "created_at": i.created_at.isoformat() if i.created_at else None
            })
        
        return jsonify({"results": results, "count": len(results)})
    except Exception as e:
        current_app.logger.exception("search error")
        return jsonify({"error": str(e)}), 500

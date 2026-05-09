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

        try:
            from ..models import Issue
            import concurrent.futures
            existing_issues = list(Issue.objects()[:30])  # limit to 30 for speed

            # Run AI analysis with 12-second timeout so mobile doesn't hang
            def _run_ai():
                return ai_analyzer.analyze_civic_issue(path, location, existing_issues)

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(_run_ai)
                try:
                    result = future.result(timeout=12)
                    if isinstance(result, dict):
                        return jsonify(result)
                except concurrent.futures.TimeoutError:
                    print("[AI] Analysis timed out (>12s) – using fast fallback")
        except Exception as ai_error:
            print(f"AI analysis error (using smart fallback): {ai_error}")

        # Smart fallback – uses real keyword classifiers, not random
        try:
            from ..services.civic_ai import classify_issue_type, assess_damage_severity
            from ..services.advanced_ai import analyze_sentiment, smart_assign_department, predict_resolution_days

            # Derive text hints from filename + location
            hint_text = f"{os.path.basename(path)} {location}"
            category, subclass, cat_conf = classify_issue_type(hint_text, [])
            severity_score, severity_level = assess_damage_severity(category, hint_text, [])
            sentiment = analyze_sentiment(location)
            dept, dept_conf = smart_assign_department(category, hint_text, [])
            pred_days = predict_resolution_days(category, severity_level)

            detected_objects = [{'label': subclass, 'confidence': round(cat_conf, 1)}]
            desc = (f"A {category.replace('_', ' ')} issue has been detected at {location}. "
                    f"Analysis indicates a {severity_level.lower()} severity concern requiring "
                    f"attention from {dept}.")

            return jsonify({
                'description':              desc,
                'category':                 category,
                'detected_objects':         detected_objects,
                'confidence':               round(cat_conf, 1),
                'severity':                 severity_level,
                'priority':                 'High' if severity_level in ('High', 'Critical') else severity_level,
                'similar_issues_count':     0,
                'duplicate_detected':       False,
                'sentiment':                sentiment['sentiment'],
                'urgency_score':            round(sentiment['urgency_score'], 2),
                'assigned_department':      dept,
                'department_confidence':    round(dept_conf, 2),
                'predicted_resolution_days': pred_days,
                'ai_fallback':              True,
            })
        except Exception as fallback_err:
            print(f"Smart fallback error: {fallback_err}")
            return jsonify({
                'description': f'Civic issue detected at {location}. Manual classification required.',
                'category': 'general',
                'severity': 'Medium',
                'priority': 'Medium',
                'assigned_department': 'Municipal Corporation',
                'ai_error': str(fallback_err)
            }), 200
    except Exception as e:
        current_app.logger.exception("analyze-image error")
        return jsonify({
            'description': 'Civic issue detected at location. Manual classification required.',
            'category': 'general',
            'severity': 'Medium',
            'priority': 'Medium',
            'assigned_department': 'Municipal Corporation',
            'ai_error': str(e)
        }), 200


@api_bp.route("/analyze-text", methods=["POST"])
def analyze_text_api():
    try:
        text = request.json.get("text", "")
        location = request.json.get("location", "Unknown")
        
        if not text:
            return jsonify({"error": "No text provided"}), 400

        try:
            from ..services.advanced_ai import analyze_sentiment, smart_assign_department, predict_resolution_days
            
            sentiment = analyze_sentiment(text)
            dept, dept_conf = smart_assign_department(None, text, [])
            predicted_days = predict_resolution_days(None, "Medium")
            
            return jsonify({
                "text": text,
                "sentiment": sentiment['sentiment'],
                "urgency_score": sentiment['urgency_score'],
                "detected_keywords": sentiment.get('detected_keywords', []),
                "recommended_department": dept,
                "department_confidence": dept_conf,
                "predicted_resolution_days": predicted_days
            })
        except Exception as ai_err:
            print(f"Text AI error (using fallback): {ai_err}")
            # Fallback
            import random
            departments = ['PWD', 'Sanitation Department', 'Water Department', 'Electricity Department']
            keywords = []
            text_lower = text.lower()
            if any(w in text_lower for w in ['water', 'leak', 'drain']): keywords.append('water')
            if any(w in text_lower for w in ['road', 'pothole', 'crack']): keywords.append('roads')
            if any(w in text_lower for w in ['garbage', 'trash', 'waste']): keywords.append('sanitation')
            if any(w in text_lower for w in ['light', 'electric', 'power']): keywords.append('electricity')
            
            return jsonify({
                "text": text,
                "sentiment": "normal",
                "urgency_score": 0.5,
                "detected_keywords": keywords,
                "recommended_department": random.choice(departments),
                "department_confidence": 0.75,
                "predicted_resolution_days": random.randint(3, 10),
                "ai_fallback": True
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
        # Support both X-User-ID (mobile) and Authorization: Bearer (web)
        user_id = request.headers.get('X-User-ID', '').strip()
        if not user_id:
            auth = request.headers.get('Authorization', '')
            user_id = auth.replace('Bearer ', '').strip()

        from ..models import Issue

        user_issues = []
        if user_id:
            try:
                user_issues = list(Issue.objects(user=user_id))
            except Exception:
                user_issues = []

        reported = len(user_issues)
        resolved = len([i for i in user_issues if 'Resolved' in (i.status or '')])
        pending  = len([i for i in user_issues if i.status == 'Pending'])
        upvotes  = sum([i.upvotes or 0 for i in user_issues])

        return jsonify({
            "reported": reported,
            "resolved": resolved,
            "pending":  pending,
            "upvotes":  upvotes
        })
    except Exception as e:
        current_app.logger.exception("user-stats error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/notifications", methods=["GET"])
def get_notifications():
    try:
        user_id = request.headers.get('X-User-ID', '').strip()
        from ..models import Notification, User

        if user_id:
            try:
                user_obj = User.objects(id=user_id).first()
                if user_obj:
                    notifs = Notification.objects(user=user_obj).order_by('-created_at').limit(50)
                    data = [{
                        "id":      str(n.id),
                        "type":    n.type,
                        "title":   n.title,
                        "message": n.message,
                        "time":    _time_ago(n.created_at),
                        "read":    n.read
                    } for n in notifs]
                    # Seed welcome notification for new users
                    if not data:
                        welcome = Notification(
                            user=user_obj,
                            type='system',
                            title='Welcome to Jan Suvidha',
                            message='Start reporting civic issues in your area to make a difference!',
                            read=False
                        )
                        welcome.save()
                        data = [{
                            "id":      str(welcome.id),
                            "type":    'system',
                            "title":   welcome.title,
                            "message": welcome.message,
                            "time":    'Just now',
                            "read":    False
                        }]
                    return jsonify({"notifications": data})
            except Exception as db_err:
                print(f"Notification DB error: {db_err}")

        # Fallback demo (unauthenticated)
        return jsonify({"notifications": [
            {"id": "demo-1", "type": "system", "title": "Welcome to Jan Suvidha",
             "message": "Login to see your personal notifications.", "time": "Now", "read": False}
        ]})
    except Exception as e:
        current_app.logger.exception("notifications error")
        return jsonify({"error": str(e)}), 500


def _time_ago(dt):
    """Human-readable relative time."""
    if not dt:
        return 'Unknown'
    delta = datetime.utcnow() - dt
    seconds = int(delta.total_seconds())
    if seconds < 60:     return 'Just now'
    if seconds < 3600:   return f"{seconds // 60}m ago"
    if seconds < 86400:  return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


@api_bp.route("/notifications/<notif_id>/read", methods=["POST"])
def mark_notification_read(notif_id):
    try:
        from ..models import Notification
        notif = Notification.objects(id=notif_id).first()
        if notif:
            notif.read = True
            notif.save()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/notifications/read-all", methods=["POST"])
def mark_all_notifications_read():
    try:
        user_id = request.headers.get('X-User-ID', '').strip()
        from ..models import Notification, User
        if user_id:
            user_obj = User.objects(id=user_id).first()
            if user_obj:
                Notification.objects(user=user_obj, read=False).update(set__read=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/forum/posts", methods=["GET", "POST"])
def forum_posts():
    try:
        from ..models import ForumPost, User

        if request.method == "GET":
            posts_qs = ForumPost.objects().order_by('-created_at').limit(50)
            posts = []
            for p in posts_qs:
                author_name = 'Anonymous'
                try:
                    author_name = p.user.name if p.user else 'Anonymous'
                except Exception:
                    pass
                posts.append({
                    "id":      str(p.id),
                    "title":   p.title,
                    "author":  author_name,
                    "replies": p.replies or 0,
                    "time":    _time_ago(p.created_at)
                })
            # Seed with starter posts if DB is empty
            if not posts:
                posts = [
                    {"id": "seed-1", "title": "Best way to report water leakage?", "author": "Community", "replies": 5, "time": "2h ago"},
                    {"id": "seed-2", "title": "Road repair update - Main Road", "author": "Admin", "replies": 12, "time": "5h ago"},
                    {"id": "seed-3", "title": "Garbage collection timing", "author": "Community", "replies": 3, "time": "1d ago"},
                ]
            return jsonify({"posts": posts})

        # POST – create new post
        data = request.get_json() or {}
        user_id = request.headers.get('X-User-ID', '').strip()
        title   = data.get('title', '').strip()
        content = data.get('content', title)  # fallback content to title

        if not title:
            return jsonify({"success": False, "error": "Title required"}), 400

        user_obj = None
        if user_id:
            try:
                user_obj = User.objects(id=user_id).first()
            except Exception:
                pass

        if not user_obj:
            return jsonify({"success": False, "error": "Login required"}), 401

        new_post = ForumPost(user=user_obj, title=title, content=content)
        new_post.save()

        return jsonify({
            "success": True,
            "post": {
                "id":      str(new_post.id),
                "title":   new_post.title,
                "author":  user_obj.name,
                "replies": 0,
                "time":    'Just now'
            }
        })
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


@api_bp.route("/extract-text", methods=["POST"])
def extract_text_api():
    """Extract text from image using OCR"""
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image provided"}), 400
        
        filename = f"ocr_{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        from ..services.vision_service import extract_text_from_image, assess_image_quality
        
        ocr_result = extract_text_from_image(path)
        quality = assess_image_quality(path)
        
        # Cleanup temp file
        try:
            os.remove(path)
        except:
            pass
        
        return jsonify({
            "success": True,
            "text": ocr_result.get('text', ''),
            "confidence": ocr_result.get('confidence', 0),
            "languages": ocr_result.get('languages', ['en']),
            "has_address": ocr_result.get('has_address', False),
            "has_landmark": ocr_result.get('has_landmark', False),
            "image_quality": quality
        })
    except Exception as e:
        current_app.logger.exception("extract-text error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/assess-quality", methods=["POST"])
def assess_quality_api():
    """Assess image quality for analysis"""
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image provided"}), 400
        
        filename = f"quality_{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        from ..services.vision_service import assess_image_quality
        
        result = assess_image_quality(path)
        
        # Cleanup
        try:
            os.remove(path)
        except:
            pass
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("assess-quality error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/verify-resolution", methods=["POST"])
def verify_resolution_api():
    """Compare before/after images to verify issue resolution"""
    try:
        before_file = request.files.get("before_image")
        after_file = request.files.get("after_image")
        
        if not before_file or not after_file:
            return jsonify({"error": "Both before and after images required"}), 400
        
        before_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"verify_before_{datetime.now().timestamp()}_{secure_filename(before_file.filename)}")
        after_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"verify_after_{datetime.now().timestamp()}_{secure_filename(after_file.filename)}")
        
        before_file.save(before_path)
        after_file.save(after_path)
        
        from ..services.vision_service import compare_before_after
        
        result = compare_before_after(before_path, after_path)
        
        # Cleanup
        try:
            os.remove(before_path)
            os.remove(after_path)
        except:
            pass
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("verify-resolution error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/extract-location-hints", methods=["POST"])
def extract_location_hints_api():
    """Extract location hints from image"""
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image provided"}), 400
        
        filename = f"hints_{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        from ..services.vision_service import extract_location_hints
        
        result = extract_location_hints(path)
        
        # Cleanup
        try:
            os.remove(path)
        except:
            pass
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception("extract-location-hints error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/classify-issue", methods=["POST"])
def classify_issue_api():
    """Classify civic issue type using AI"""
    try:
        data = request.json or {}
        description = data.get('description', '')
        detected_objects = data.get('detected_objects', [])
        
        from ..services.civic_ai import classify_issue_type, assess_damage_severity
        
        category, subclass, confidence = classify_issue_type(description, detected_objects)
        severity_score, severity_level = assess_damage_severity(category, description, detected_objects)
        
        return jsonify({
            'success': True,
            'category': category,
            'subclass': subclass,
            'confidence': confidence,
            'severity_score': severity_score,
            'severity_level': severity_level
        })
    except Exception as e:
        current_app.logger.exception("classify-issue error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predict-hotspots", methods=["GET"])
def predict_hotspots_api():
    """Predict issue hotspots using historical data"""
    try:
        from ..models import Issue
        from ..services.civic_ai import predict_issue_hotspots
        
        issues = Issue.objects()[:200]
        issues_data = [{
            'location': i.location,
            'category': i.category,
            'created_at': i.created_at
        } for i in issues]
        
        hotspots = predict_issue_hotspots(issues_data, None)
        
        return jsonify({
            'success': True,
            'hotspots': hotspots,
            'count': len(hotspots)
        })
    except Exception as e:
        current_app.logger.exception("predict-hotspots error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/find-similar", methods=["POST"])
def find_similar_api():
    """Find similar existing issues"""
    try:
        data = request.json or {}
        description = data.get('description', '')
        location = data.get('location', '')
        category = data.get('category', '')
        
        from ..models import Issue
        from ..services.civic_ai import find_similar_issues_advanced
        
        issues = Issue.objects()[:100]
        
        similar = find_similar_issues_advanced(issues, description, location, category)
        
        return jsonify({
            'success': True,
            'similar_issues': similar,
            'count': len(similar)
        })
    except Exception as e:
        current_app.logger.exception("find-similar error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/calculate-priority", methods=["POST"])
def calculate_priority_api():
    """Calculate issue priority score"""
    try:
        data = request.json or {}
        
        from ..services.civic_ai import calculate_priority_score
        
        severity = data.get('severity', 'Medium')
        category = data.get('category', 'general')
        upvotes = data.get('upvotes', 0)
        days_open = data.get('days_open', 0)
        sentiment_score = data.get('sentiment_score', 0.5)
        
        priority = calculate_priority_score(severity, category, upvotes, days_open, sentiment_score)
        
        priority_label = 'Urgent' if priority >= 80 else 'High' if priority >= 60 else 'Medium' if priority >= 40 else 'Low'
        
        return jsonify({
            'success': True,
            'priority_score': priority,
            'priority_label': priority_label
        })
    except Exception as e:
        current_app.logger.exception("calculate-priority error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/estimate-resolution", methods=["POST"])
def estimate_resolution_api():
    """Estimate resolution time for an issue"""
    try:
        data = request.json or {}
        
        from ..services.civic_ai import estimate_resolution_time
        
        issue_type = data.get('category', 'general')
        severity = data.get('severity', 'Medium')
        
        result = estimate_resolution_time(issue_type, severity, issue_type)
        
        return jsonify({
            'success': True,
            'estimation': result
        })
    except Exception as e:
        current_app.logger.exception("estimate-resolution error")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/resolution-trends", methods=["GET"])
def resolution_trends_api():
    """Get resolution trend analysis"""
    try:
        from ..models import Issue
        from ..services.civic_ai import analyze_resolution_trends, generate_insights
        
        issues = Issue.objects()[:500]
        
        trends = analyze_resolution_trends(issues)
        insights = generate_insights(issues)
        
        return jsonify({
            'success': True,
            'trends': trends,
            'insights': insights
        })
    except Exception as e:
        current_app.logger.exception("resolution-trends error")
        return jsonify({"error": str(e)}), 500

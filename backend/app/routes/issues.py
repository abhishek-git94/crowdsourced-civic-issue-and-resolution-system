import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ..models import Issue, Upvote, User
from ..services.ai_service import CivicAIAnalyzer
from ..utils.duplicate_detector import (
    get_local_embedding, get_openai_embedding,
    cosine_similarity, embed_to_json
)

issues_bp = Blueprint("issues", __name__)

# Initialize AI Analyzer
ai_analyzer = CivicAIAnalyzer()

@issues_bp.route("/view")
@login_required
def view_issues():
    try:
        issues = Issue.objects.order_by('-created_at')
        voted_ids = {str(upvote.issue.id) for upvote in Upvote.objects(user=current_user.id)}
        
        for issue in issues:
            issue.has_upvoted = str(issue.id) in voted_ids
            
        return render_template("view_issues.html", issues=issues)
    except Exception as e:
        current_app.logger.error(f"Error viewing issues: {e}")
        flash("Error loading issues.", "danger")
        return render_template("downtime.html")

@issues_bp.route("/issue/<issue_id>/upvote", methods=["POST"])
@login_required
def upvote_issue(issue_id):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        issue = Issue.objects(id=issue_id).first()
        if not issue:
            if is_ajax: return jsonify({"success": False, "error": "Issue not found"}), 404
            flash("Issue not found.", "danger")
            return redirect(url_for("issues.view_issues"))

        existing_vote = Upvote.objects(user=current_user.id, issue=issue.id).first()

        if existing_vote:
            existing_vote.delete()
            issue.upvotes = max(0, issue.upvotes - 1)
            issue.save()
            if is_ajax: return jsonify({"success": True, "upvoted": False, "upvotes": issue.upvotes, "status": "removed"})
            flash("Vote removed.", "info")
            return redirect(url_for("issues.view_issues"))

        new_vote = Upvote(user=current_user.id, issue=issue.id)
        new_vote.save()
        issue.upvotes += 1
        
        # Gamification: Award points to the reporter
        if issue.user:
            issue.user.points += 5
            issue.user.save()
            
        issue.save()
        if is_ajax: return jsonify({"success": True, "upvoted": True, "upvotes": issue.upvotes, "status": "added"})
        flash("Upvoted! Reporter earned points.", "success")
        return redirect(url_for("issues.view_issues"))
    except Exception as e:
        current_app.logger.error(f"Upvote error: {e}")
        if is_ajax: return jsonify({"success": False, "error": "Database error"}), 500
        flash("Database error. Please try again later.", "danger")
        return redirect(url_for("issues.view_issues"))

@issues_bp.route("/report", methods=["GET", "POST"])
@login_required
def report_issue():
    if request.method == "POST":
        name = current_user.name
        location = request.form.get("location", "")
        
        # Geolocation
        lat_str = request.form.get("latitude", "")
        lng_str = request.form.get("longitude", "")
        latitude = float(lat_str) if lat_str else None
        longitude = float(lng_str) if lng_str else None

        file = request.files.get("attachment")
        analysis = None
        file_path = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            file_path = f"uploads/{filename}"

            try:
                analysis = ai_analyzer.analyze_civic_issue(full_path, location)
                issue_text = analysis.get("description", "") if isinstance(analysis, dict) else ""
            except Exception:
                current_app.logger.exception("AI analyze error")
                issue_text = request.form.get("issue", "")
        else:
            issue_text = request.form.get("issue", "")

        embed_text = f"{issue_text}\nLocation: {location}"
        try:
            if analysis and isinstance(analysis, dict):
                detected = analysis.get("detected_objects", [])
                if detected:
                    object_labels = [obj["label"] if isinstance(obj, dict) and "label" in obj else str(obj) for obj in detected]
                    embed_text += "\nObjects: " + ", ".join(object_labels)
        except Exception:
            current_app.logger.exception("Error building embed_text")

        try:
            embedding = get_openai_embedding(embed_text) if current_app.config['EMBED_BACKEND'] == "openai" else get_local_embedding(embed_text)
        except Exception:
            embedding = None

        similar = []
        if embedding:
            try:
                recent = Issue.objects(embedding__ne=None).order_by('-created_at').limit(current_app.config['RECENT_CHECK_COUNT'])
                for old in recent:
                    try:
                        old_emb = json.loads(old.embedding)
                        sim = cosine_similarity(embedding, old_emb)
                        if sim >= current_app.config['SIMILARITY_THRESHOLD']:
                            similar.append({"id": str(old.id), "issue": old.issue, "location": old.location, "upvotes": old.upvotes, "similarity": round(sim, 3)})
                    except Exception: continue
            except Exception: pass

        if similar:
            session["_pending_issue"] = {
                "name": name, "issue": issue_text, "location": location,
                "latitude": latitude, "longitude": longitude,
                "file_path": file_path, "analysis": analysis,
                "embedding": embed_to_json(embedding) if embedding else None
            }
            return render_template("confirm_duplicate.html", candidates=similar, pending=session["_pending_issue"])

        # Auto-Routing Logic
        def get_department(category):
            dept_map = {
                'pothole': 'Public Works Department (PWD)',
                'road_damage': 'Public Works Department (PWD)',
                'garbage': 'Sanitation Department',
                'traffic': 'Traffic Police',
                'street_furniture': 'Municipal Corporation',
                'general_infrastructure': 'Municipal Corporation'
            }
            return dept_map.get(category, 'Municipal Corporation')

        category = analysis.get("category") if isinstance(analysis, dict) else None
        assigned_dept = get_department(category) if category else 'Municipal Corporation'

        try:
            new_issue = Issue(
                name=name, issue=issue_text, location=location, 
                latitude=latitude, longitude=longitude,
                file=file_path, status="Pending",
                category=category,
                confidence=(analysis.get("confidence") if isinstance(analysis, dict) else None),
                severity=(analysis.get("severity") if isinstance(analysis, dict) else None),
                embedding=(embed_to_json(embedding) if embedding else None),
                assigned_to=assigned_dept,
                user=current_user.id
            )
            new_issue.save()
            
            # Gamification: Award points for reporting
            current_user.points += 10
            current_user.save()
            
        except Exception as e:
            current_app.logger.error(f"Report save error: {e}")
            flash("Database error. Could not save your report.", "danger")
            return redirect(url_for("issues.report_issue"))

        flash("Issue reported successfully! You earned 10 points.", "success")
        return redirect(url_for("issues.report_issue"))

    return render_template("report_issues.html")

@issues_bp.route("/report/confirm_link", methods=["POST"])
@login_required
def confirm_link():
    pending = session.pop("_pending_issue", None)
    link_to = request.form.get("link_to")
    if not pending:
        flash("No pending issue!", "danger")
        return redirect(url_for("issues.report_issue"))

    try:
        new_issue = Issue(
            name=pending["name"], issue=pending["issue"], location=pending["location"],
            latitude=pending.get("latitude"), longitude=pending.get("longitude"),
            file=pending["file_path"], status="Linked", is_duplicate_of=link_to,
            embedding=pending.get("embedding"), user=current_user.id
        )
        new_issue.save()
    except Exception:
        flash("Database error. Could not link issue.", "danger")
        return redirect(url_for("issues.report_issue"))

    flash("Issue linked successfully.", "success")
    return redirect(url_for("issues.view_issues"))

@issues_bp.route("/report/force_create", methods=["POST"])
@login_required
def force_create():
    pending = session.pop("_pending_issue", None)
    if not pending:
        flash("Nothing to create.", "danger")
        return redirect(url_for("issues.report_issue"))

    try:
        new_issue = Issue(
            name=pending["name"], issue=pending["issue"], location=pending["location"],
            latitude=pending.get("latitude"), longitude=pending.get("longitude"),
            file=pending["file_path"], status="Pending",
            embedding=pending.get("embedding"), user=current_user.id
        )
        new_issue.save()
    except Exception:
        flash("Database error. Could not create issue.", "danger")
        return redirect(url_for("issues.report_issue"))

    flash("Issue created.", "success")
    return redirect(url_for("issues.view_issues"))

@issues_bp.route("/trending")
@login_required
def trending_issues():
    try:
        issues = Issue.objects.order_by('-upvotes').limit(5)
    except Exception:
        issues = []
    return render_template("trending_issues.html", issues=issues)

@issues_bp.route("/issue/<issue_id>/confirm_resolve", methods=["POST"])
@login_required
def confirm_resolve(issue_id):
    try:
        issue = Issue.objects(id=issue_id).first()
        if not issue:
            flash("Issue not found.", "danger")
            return redirect(url_for("issues.view_issues"))
        
        if str(issue.user.id) != str(current_user.id):
            flash("Only the original reporter can confirm resolution.", "danger")
            return redirect(url_for("issues.view_issues"))
        
        if issue.status != "Resolved (Unconfirmed)":
            flash("This issue is not marked as resolved by officials yet.", "warning")
            return redirect(url_for("issues.view_issues"))
        
        issue.status = "Resolved"
        issue.is_confirmed_by_citizen = True
        issue.resolved_at = datetime.utcnow()
        
        # Gamification: Bonus points for confirmation
        current_user.points += 20
        current_user.save()
        
        issue.save()
        flash("Resolution confirmed! Thank you for your feedback.", "success")
    except Exception as e:
        current_app.logger.error(f"Confirm resolve error: {e}")
        flash("An error occurred.", "danger")
    
    return redirect(url_for("issues.view_issues"))

@issues_bp.route("/leaderboard")
def leaderboard():
    try:
        top_users = User.objects.order_by('-points').limit(10)
        return render_template("leaderboard.html", users=top_users)
    except Exception:
        flash("Error loading leaderboard.", "danger")
        return redirect(url_for("main.index"))

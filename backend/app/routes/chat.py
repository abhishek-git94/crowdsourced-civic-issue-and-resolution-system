from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import Message, User, Issue

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("/")
@login_required
def index():
    try:
        # Get unique users the current user has chatted with
        # MongoEngine/MongoDB way to get distinct values
        sent = Message.objects(sender=current_user.id).distinct('receiver')
        received = Message.objects(receiver=current_user.id).distinct('sender')
        
        user_ids = set(sent) | set(received)
        
        chat_users = User.objects(id__in=user_ids) if user_ids else []
        return render_template("chat/index.html", chat_users=chat_users)
    except Exception as e:
        print(f"Chat index error: {e}")
        flash("Error loading chats.", "danger")
        return redirect(url_for("main.index"))

@chat_bp.route("/with/<user_id>", methods=["GET", "POST"])
@login_required
def chat_with(user_id):
    if request.method == "POST":
        content = request.form.get("content")
        issue_id = request.form.get("issue_id")
        if content:
            try:
                msg = Message(
                    sender=current_user.id,
                    receiver=user_id,
                    content=content,
                    issue=issue_id if issue_id else None
                )
                msg.save()
                return redirect(url_for("chat.chat_with", user_id=user_id))
            except Exception as e:
                print(f"Send message error: {e}")
                flash("Error sending message.", "danger")
    
    try:
        other_user = User.objects(id=user_id).first()
        if not other_user:
            flash("User not found.", "danger")
            return redirect(url_for("chat.index"))
        
        messages = Message.objects(
            (Message.sender == current_user.id) & (Message.receiver == user_id) |
            (Message.sender == user_id) & (Message.receiver == current_user.id)
        ).order_by('created_at')
        
        # Mark received messages as read
        for m in messages:
            if str(m.receiver.id) == str(current_user.id) and not m.is_read:
                m.is_read = True
                m.save()
            
        return render_template("chat/conversation.html", other_user=other_user, messages=messages)
    except Exception as e:
        print(f"Chat with error: {e}")
        flash("Error loading conversation.", "danger")
        return redirect(url_for("chat.index"))

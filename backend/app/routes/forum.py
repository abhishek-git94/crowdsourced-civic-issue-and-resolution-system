from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import ForumPost, ForumComment

forum_bp = Blueprint("forum", __name__, url_prefix="/forum")

@forum_bp.route("/")
@login_required
def index():
    try:
        posts = ForumPost.objects.order_by('-created_at')
        return render_template("forum/index.html", posts=posts)
    except Exception:
        flash("Error loading forum.", "danger")
        return redirect(url_for("main.index"))

@forum_bp.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if not title or not content:
            flash("Title and content are required.", "warning")
            return redirect(url_for("forum.new_post"))
        
        try:
            post = ForumPost(title=title, content=content, user=current_user.id)
            post.save()
            current_user.points += 2 # Points for community participation
            current_user.save()
            flash("Post created!", "success")
            return redirect(url_for("forum.index"))
        except Exception:
            flash("Could not create post.", "danger")
            
    return render_template("forum/new_post.html")

@forum_bp.route("/post/<post_id>")
@login_required
def view_post(post_id):
    try:
        post = ForumPost.objects(id=post_id).first()
        if not post:
            flash("Post not found.", "danger")
            return redirect(url_for("forum.index"))
        # comments are handled via ReferenceField in models, but we can query them
        comments = ForumComment.objects(post=post.id).order_by('created_at')
        return render_template("forum/view_post.html", post=post, comments=comments)
    except Exception:
        flash("Error loading post.", "danger")
        return redirect(url_for("forum.index"))

@forum_bp.route("/post/<post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    content = request.form.get("content")
    if not content:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("forum.view_post", post_id=post_id))
    
    try:
        comment = ForumComment(content=content, post=post_id, user=current_user.id)
        comment.save()
        flash("Comment added!", "success")
    except Exception:
        flash("Error adding comment.", "danger")
        
    return redirect(url_for("forum.view_post", post_id=post_id))

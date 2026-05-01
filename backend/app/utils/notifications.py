import os
from flask import current_app

def init_firebase():
    """Firebase is disabled for now."""
    print("ℹ️ Firebase integration is disabled. Notifications will be simulated.")

def send_push_notification(fcm_token, title, body, data=None):
    """
    Simulated push notification.
    """
    print(f"[SIMULATED FCM] To: {fcm_token} | Title: {title} | Body: {body}")
    return True

def notify_status_change(issue):
    """
    Called when an issue status changes to notify the reporter.
    """
    user_name = issue.user.name if issue.user else 'Unknown'
    fcm_token = issue.user.fcm_token if (issue.user and hasattr(issue.user, 'fcm_token')) else 'NO_TOKEN'
    
    print(f"[SIMULATED NOTIFICATION] Notify User: {user_name} | Issue: {issue.name} | Status: {issue.status}")
    
    return send_push_notification(fcm_token, f"Issue Update: {issue.name}", f"Your reported issue is now: {issue.status}", {"issue_id": str(issue.id)})

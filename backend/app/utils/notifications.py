import os
import firebase_admin
from firebase_admin import credentials, messaging
from flask import current_app

def init_firebase():
    try:
        if not firebase_admin._apps:
            # We would use a real service account JSON in production
            cred_path = os.environ.get("FIREBASE_CREDENTIALS", "mock_firebase_credentials.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized successfully.")
            else:
                print("⚠️ Firebase credentials not found. Notifications will be simulated.")
    except Exception as e:
        print(f"⚠️ Firebase init error: {e}")

def send_push_notification(fcm_token, title, body, data=None):
    """
    Sends a push notification to a specific device token.
    """
    if not firebase_admin._apps:
        print(f"[SIMULATED FCM] To: {fcm_token} | Title: {title} | Body: {body}")
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=fcm_token,
        )
        response = messaging.send(message)
        print(f"✅ Successfully sent message: {response}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send notification: {e}")
        return False

def notify_status_change(issue):
    """
    Called when an issue status changes to notify the reporter.
    """
    if not issue.user or not hasattr(issue.user, 'fcm_token') or not issue.user.fcm_token:
        # Fallback simulated logging
        print(f"[SIMULATED FCM] User {issue.user.name if issue.user else 'Unknown'} does not have an FCM token. Status changed to {issue.status}.")
        return False
        
    title = f"Issue Update: {issue.name}"
    body = f"Your reported issue is now: {issue.status}"
    
    return send_push_notification(issue.user.fcm_token, title, body, {"issue_id": str(issue.id)})

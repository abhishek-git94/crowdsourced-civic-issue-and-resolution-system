import os

class PushNotificationService:
    def __init__(self):
        self.initialized = False
        print("ℹ️ PushNotificationService initialized in simulation mode.")

    def send_status_update(self, device_token, issue_title, new_status):
        """Simulate sending a push notification about an issue status change."""
        print(f"[SIMULATED PUSH] To: {device_token} | Title: Civic Issue Status Update | Body: Your reported issue '{issue_title[:30]}...' is now: {new_status}")
        return True

# Singleton instance
notification_service = PushNotificationService()

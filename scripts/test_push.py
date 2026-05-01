import sys
sys.path.append('Jansuvidha')
from app.services.notification_service import notification_service

TEST_DEVICE_TOKEN = "eO7iQ9z4S46bC_C6G8d:APA91bF1sU8oR5l5H7oN9yL3K0r2P9j1X9n8m7J6k5l4M3N2O1P0Q9R8S7T6U5V4W3X2Y1Z0"

print("Testing push notification...")
success = notification_service.send_status_update(
    device_token=TEST_DEVICE_TOKEN,
    issue_title="Pothole on Main Street",
    new_status="In Progress"
)

if success:
    print("Successfully sent to device!")
else:
    print("Failed. Ensure your token is valid.")

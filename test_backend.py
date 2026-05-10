import sys
import traceback

try:
    print('Testing Backend Initialization...')
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        from backend.app.models import Issue, User, Notification, ForumPost
        print('Models loaded successfully.')
        from backend.app.services.ai_service import CivicAIAnalyzer
        print('AI Service loaded successfully.')
    print('Backend Initialization: SUCCESS')
except Exception as e:
    print('Backend Initialization: FAILED')
    traceback.print_exc()
    sys.exit(1)

from backend.app.models import User
from backend.app import create_app
import json

app = create_app()
with app.app_context():
    users = User.objects()
    data = []
    for u in users:
        data.append({
            "name": u.name,
            "email": u.email,
            "role": u.role
        })
    print(json.dumps(data, indent=2))

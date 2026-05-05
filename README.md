# Jan Suvidha - Civic Issue Reporting System

An AI-powered civic issue reporting and management platform that enables citizens to report infrastructure problems using images, with automated severity assessment, duplicate detection, and department routing.

## Features

### For Citizens
- **Image-based Issue Reporting** - Upload photos of civic issues (potholes, garbage, broken streetlights, etc.)
- **AI Analysis** - Automatic object detection (YOLO) and severity assessment
- **Duplicate Detection** - Semantic similarity matching to find related issues
- **Upvoting System** - Prioritize important issues
- **Real-time Status Tracking** - Get notified when issues are resolved
- **Gamification** - Earn points for reporting and confirming resolutions

### For Administrators
- **Admin Dashboard** - Full analytics with charts (status distribution, category breakdown, daily trends)
- **Department Assignment** - Auto-route issues to appropriate departments (PWD, Sanitation, Traffic, etc.)
- **Issue Management** - Filter, assign, update status, generate PDF reports
- **Efficiency Rankings** - Track department resolution times

### For Managers
- **Department Dashboard** - View and update issues assigned to your department

## Tech Stack

- **Backend**: Flask, Flask-Login, MongoDB (MongoEngine)
- **AI/ML**: YOLO (image detection), Sentence-Transformers (embeddings), SVM (severity classification), Ollama (description generation)
- **Frontend**: HTML/CSS/JS, Bootstrap 5, Leaflet.js (maps), Plotly (charts)
- **Database**: MongoDB

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB (local or Atlas)
- Ollama (optional, for AI descriptions)

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd crowdsourced-civic-issue-and-resolution-system
```

2. Create virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Create `.env` file in `backend/`:
```env
SECRET_KEY=your_secret_key
MONGODB_URI=mongodb://localhost:27017/JanSuvidha
EMBED_BACKEND=local
OLLAMA_MODEL=llama3
SIMILARITY_THRESHOLD=0.78
```

5. Start MongoDB and run:
```powershell
cd backend
python run.py
```

6. Open `http://127.0.0.1:5000`

### Getting Admin Access
After registering, manually set your user's `role` to `admin` in MongoDB to access the admin dashboard.

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── models.py       # MongoDB models (User, Issue, Upvote, etc.)
│   │   ├── routes/        # Flask blueprints (auth, issues, admin, api)
│   │   ├── services/      # AI services (ai_service.py, ml_service.py)
│   │   └── utils/         # Helpers (duplicate_detector, notifications)
│   └── run.py
├── frontend/
│   └── templates/          # Jinja2 templates
├── models_ai/              # YOLO model weights
├── SETUP.md               # Detailed setup guide
└── requirements.txt
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | GET/POST | User registration |
| `/auth/login` | GET/POST | User login |
| `/issues/report` | GET/POST | Report new issue |
| `/issues/view` | GET | List all issues |
| `/issues/<id>/upvote` | POST | Upvote an issue |
| `/admin/dashboard` | GET | Admin analytics |
| `/admin/issues` | GET | Manage issues |
| `/map` | GET | Interactive map view |
| `/trending` | GET | Top voted issues |

## License

MIT
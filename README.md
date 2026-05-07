<<<<<<< HEAD
# JanSuvidha - AI-Driven Civic Issue Reporting & Management System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3+-blue?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/MongoDB-6.0-green?style=for-the-badge&logo=mongodb" alt="MongoDB">
  <img src="https://img.shields.io/badge/YOLOv8-Computer%20Vision-orange?style=for-the-badge" alt="YOLOv8">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

---

## 📋 Overview

**JanSuvidha** is an AI-powered civic issue reporting and management platform that enables citizens to report local infrastructure issues (potholes, broken streetlights, garbage, etc.) using photos. The system uses advanced AI models to automatically detect, classify, and predict resolution times for reported issues.

---

## 🎯 Key Features

### 👤 For Citizens
- 📸 **Photo-based Reporting** - Report issues with images
- 🗺️ **Interactive Map** - View issues in your area
- 👍 **Upvote System** - Prioritize important issues
- 🏆 **Leaderboard** - Gamification for active reporters
- 💬 **Forum & Chat** - Community discussions

### 👮 For Authorities
- 📊 **Admin Dashboard** - Manage all issues
- 🤖 **AI Auto-Detection** - YOLO-based issue detection
- 📈 **Analytics** - Track resolution times
- 📄 **PDF Reports** - Generate issue summaries
- 🔔 **Notifications** - Real-time alerts

### 🤖 AI/ML Features
- **Object Detection** - YOLOv8 for automatic issue detection
- **Severity Classification** - SVM model for issue severity
- **Resolution Prediction** - LSTM model for resolution time estimation
- **Duplicate Detection** - Find similar existing issues
- **RAG-powered Chat** - AI assistant for queries

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask, Python 3.10+ |
| **Database** | MongoDB (MongoEngine) |
| **Frontend** | Bootstrap 5, Jinja2, JavaScript |
| **AI/ML** | YOLOv8, TensorFlow, Scikit-learn |
| **NLP** | LangChain, Ollama (LLM) |
| **Vector DB** | ChromaDB |
| **Authentication** | Flask-Login, Google OAuth |
| **Maps** | Leaflet.js, OpenStreetMap |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MongoDB 6.0+
- Ollama (for NLP features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/abhishek-git94/crowdsourced-civic-issue-and-resolution-system.git
cd crowdsourced-civic-issue-and-resolution-system
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create `backend/.env` file:
```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=mongodb://localhost:27017/civic_db
=======
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
>>>>>>> 1838493f358f9dc728c66ed2b374995e931d7893
EMBED_BACKEND=local
OLLAMA_MODEL=llama3
SIMILARITY_THRESHOLD=0.78
```

<<<<<<< HEAD
5. **Run the application**
```bash
=======
5. Start MongoDB and run:
```powershell
>>>>>>> 1838493f358f9dc728c66ed2b374995e931d7893
cd backend
python run.py
```

<<<<<<< HEAD
6. **Access the app**
Open http://127.0.0.1:5000 in your browser

---

## 📁 Project Structure
=======
6. Open `http://127.0.0.1:5000`

### Getting Admin Access
After registering, manually set your user's `role` to `admin` in MongoDB to access the admin dashboard.

## Project Structure
>>>>>>> 1838493f358f9dc728c66ed2b374995e931d7893

```
├── backend/
│   ├── app/
<<<<<<< HEAD
│   │   ├── routes/          # Flask blueprints
│   │   ├── models/          # MongoDB models
│   │   ├── services/        # AI/ML services
│   │   └── utils/           # Helpers
│   ├── models_ai/           # Trained ML models
│   └── run.py               # Entry point
│
├── frontend/
│   ├── templates/           # Jinja2 templates
│   ├── static/
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript
│   │   └── uploads/        # User uploads
│
├── models_ai/              # YOLO weights
├── scripts/                # Utility scripts
└── README.md
```

---

## 🔧 Configuration

### AI Models Setup
```bash
# Pull Ollama model (for NLP)
ollama pull llama3

# YOLO models are already in models_ai/
```

### Database
- MongoDB should be running on `localhost:27017`
- Database name: `civic_db`

---

## 📱 User Roles

| Role | Access |
|------|--------|
| **Citizen** | Report issues, view map, forum, chat |
| **Manager** | Manage assigned issues, view dashboard |
| **Admin** | Full access, manage all issues, PDF export |

To upgrade a user to admin, manually update the `role` field in MongoDB.

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature-name`
5. Create a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com) - YOLOv8
- [Ollama](https://ollama.com) - Local LLM
- [Bootstrap](https://getbootstrap.com) - UI Framework
- [Leaflet](https://leafletjs.com) - Maps

---

<p align="center">Made with ❤️ for better civic infrastructure</p>
=======
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
>>>>>>> 1838493f358f9dc728c66ed2b374995e931d7893

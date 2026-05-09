# Jan Suvidha - Civic Issue Reporting System

An AI-powered civic issue reporting and management platform with 3 platforms:
1. **Mobile App** - For citizens to report issues
2. **Backend API** - Flask server with AI/ML
3. **Admin Dashboard** - For administrators

## Features

### Mobile App (Citizens)
- User Login/Registration
- Report issues with photo + GPS + AI analysis
- View all issues with search
- Interactive map view
- My reported issues tracking
- Community forum
- User profile with stats
- Voice input for reporting

### Backend API
- AI-powered image analysis (YOLO)
- Automatic severity & priority calculation
- Duplicate detection with embeddings
- Smart department assignment
- Sentiment analysis
- Issue clustering
- Anomaly detection
- Natural language query

### Admin Dashboard
- Overview with charts & stats
- Issue management (filter, edit, assign)
- Department CRUD & efficiency tracking
- Analytics & reports
- User management
- Settings configuration
- CSV export

---

## Quick Start

### 1. Start Backend
```powershell
cd backend
python run.py
```
Backend runs at: `http://192.168.29.159:5000`

### 2. Mobile App
```powershell
cd mobile
npm install
npx expo start
```
- Scan QR code with Expo Go on phone
- Or build APK for standalone use

### 3. Admin Dashboard
Open `admin_dashboard/index.html` in browser

---

## Configuration

### Update IP Address

**Mobile** (`mobile/App.js` line ~31):
```javascript
const API_URL = 'http://192.168.29.159:5000';
```

**Admin** (`admin_dashboard/index.html` line ~938):
```javascript
const API_BASE = 'http://192.168.29.159:5000';
```

Find your IP by running `ipconfig` on Windows.

---

## Making a User Admin

```powershell
mongosh
use JanSuvidha
db.users.updateOne({"email": "admin@email.com"}, {$set: {"role": "admin"}})
```

---

## Project Structure

```
crowdsourced-civic-issue-and-resolution-system/
├── backend/              # Flask API Server
│   ├── app/
│   │   ├── routes/      # auth, issues, admin, api, forum, chat
│   │   ├── services/    # AI services
│   │   ├── models.py    # MongoDB models
│   │   └── config.py    # Configuration
│   ├── uploads/         # Uploaded images
│   └── run.py           # Entry point
│
├── mobile/              # React Native/Expo App
│   ├── src/screens/     # 9 screens
│   ├── App.js           # Main app
│   └── package.json
│
├── admin_dashboard/     # HTML Admin Dashboard
│   └── index.html
│
├── models_ai/           # YOLO models
├── scripts/            # Helper scripts
├── .venv/              # Python environment
└── README.md           # This file
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User login |
| `/issues/report` | POST | Report new issue |
| `/issues/view` | GET | List all issues |
| `/issues/my` | GET | User's issues |
| `/issues/<id>/upvote` | POST | Upvote issue |
| `/admin/dashboard` | GET | Admin stats |
| `/admin/issues/<id>/status` | POST | Update status |
| `/api/analyze-image` | POST | AI image analysis |
| `/api/analyze-text` | POST | AI text analysis |
| `/api/cluster-issues` | GET | Issue clustering |
| `/api/detect-anomalies` | GET | Anomaly detection |
| `/api/natural-query` | POST | AI search query |
| `/api/user/stats` | GET | User statistics |
| `/api/notifications` | GET | Notifications |
| `/api/search` | GET | Issue search |

---

## Tech Stack

- **Backend**: Flask, Flask-Login, MongoDB (MongoEngine)
- **AI/ML**: YOLO, Sentence-Transformers, SVM, Ollama
- **Mobile**: React Native, Expo
- **Database**: MongoDB
- **Admin**: HTML, Bootstrap 5, Chart.js

---

## Prerequisites

- Python 3.10+
- MongoDB (local or Atlas)
- Node.js (for mobile)
- Ollama (optional, for AI descriptions)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot connect to backend | Check IP address in mobile/admin |
| Mobile app not loading | Keep backend running |
| Login fails | User role must be "admin" in MongoDB |
| Camera not working | Grant camera permission on phone |

---

## License

MIT
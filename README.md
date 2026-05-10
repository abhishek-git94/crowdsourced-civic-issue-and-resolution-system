# Jan Suvidha - Civic Issue Reporting System

An AI-powered civic issue reporting and management platform with 3 platforms:
1. **Mobile App** - For citizens to report issues
2. **Backend API** - Flask server with AI/ML
3. **Admin Dashboard** - For administrators

---

## Features

### Mobile App (Citizens)
- User Login/Registration
- Report issues with photo + GPS + AI analysis
- View all issues with search & filter
- Interactive map view
- My reported issues tracking
- Community forum
- User profile with stats
- Notifications

### AI/ML Features (12+ Models)
| # | Component | Technology | Purpose |
|---|-----------|------------|---------|
| 1 | YOLO Object Detection | YOLOv8 (Custom) | Detect civic issues in images |
| 2 | Issue Classification | Custom Model | Categorize: Roads, Sanitation, Traffic, etc. |
| 3 | Severity Assessment | ML Model | Calculate severity (1-10) |
| 4 | Smart Department Routing | Keyword + ML | Assign to PWD, Sanitation, Traffic, etc. |
| 5 | Resolution Prediction | ML Model | Predict days to fix |
| 6 | Sentiment Analysis | NLP | Detect urgency from text |
| 7 | Hotspot Prediction | ML Regression | Predict problem areas |
| 8 | Description Generation | Ollama/Llama 3 | Auto-generate descriptions |

### Admin Dashboard
- Overview with charts & stats
- Issue management (filter, edit, assign)
- Department CRUD
- Analytics & reports
- User management
- Real-time data from MongoDB

---

## Quick Start

### 1. Start MongoDB
Make sure MongoDB is running (default: localhost:27017)

### 2. Start Backend
```powershell
cd backend
python run.py
```
Backend runs at: `http://YOUR_IP:5000` (binds to 0.0.0.0)

### 3. Mobile App
```powershell
cd mobile
npm install
npx expo start
```
- Scan QR code with Expo Go on phone
- Make sure phone is on same WiFi as backend laptop

### 4. Admin Dashboard
Open `admin_dashboard/index.html` in browser

**Login Credentials:**
- Email: `admin@js.com`
- Password: `admin123`

---

## Custom YOLO Model

The project uses a custom-trained YOLO model for civic issue detection:

**Model file**: `models_ai/last_jansuvidha.pt`

**10 Trained Classes**:
1. Pothole Issues
2. Damaged Road issues
3. Illegal Parking Issues
4. Broken Road Sign Issues
5. Fallen trees
6. Littering/Garbage on Public Places
7. Vandalism Issues
8. Dead Animal Pollution
9. Damaged concrete structures
10. Damaged Electric wires and poles

---

## Configuration

### Find Your IP Address
```powershell
ipconfig
```
Look for IPv4 Address (e.g., `10.138.152.42`)

### Update IP in Mobile App
Edit `mobile/App.js`:
```javascript
const API_URL = 'http://YOUR_IP:5000';
```

### Update IP in Admin Dashboard
Edit `admin_dashboard/src/admin-logic.js`:
```javascript
const API_BASE = 'http://YOUR_IP:5000';
```

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
│   │   ├── routes/       # auth, issues, admin, api, forum
│   │   ├── services/     # AI services (ai_service, civic_ai, advanced_ai)
│   │   ├── models.py     # MongoDB models
│   │   └── config.py     # Configuration
│   ├── uploads/          # Uploaded images
│   ├── models_ai/        # YOLO models (last_jansuvidha.pt)
│   └── run.py            # Entry point
│
├── mobile/               # React Native/Expo App
│   ├── src/screens/     # 10 screens
│   ├── App.js           # Main app
│   └── package.json
│
├── admin_dashboard/      # HTML Admin Dashboard
│   ├── index.html
│   ├── css/
│   └── src/
│
├── models_ai/            # AI Models
│   └── last_jansuvidha.pt
│
└── README.md            # This file
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User login |
| `/issues/report` | POST | Report new issue |
| `/issues/view` | GET | List all issues (JSON) |
| `/issues/my` | GET | User's issues |
| `/issues/<id>/upvote` | POST | Upvote issue |
| `/api/analyze-image` | POST | AI image analysis |
| `/api/test-yolo` | POST | Debug YOLO detection |
| `/api/health` | GET | API health check |
| `/admin/dashboard` | GET | Admin stats |
| `/admin/issues/<id>/status` | POST | Update status |

---

## Tech Stack

- **Backend**: Flask, Flask-Login, MongoDB (MongoEngine)
- **AI/ML**: YOLO v8 (Custom), Ollama/Llama 3, NLP
- **Mobile**: React Native, Expo
- **Database**: MongoDB
- **Admin**: HTML5, Bootstrap 5, Chart.js

---

## Prerequisites

- Python 3.10+
- MongoDB (local or Atlas) - required
- Node.js (for mobile)
- Ollama (optional - AI works with fallback)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot connect to backend | Check IP address in mobile/admin matches laptop IP |
| Mobile app not loading | Keep backend running, ensure same WiFi |
| Login fails | Use admin@js.com / admin123 for admin |
| Camera not working | Grant camera permission on phone |
| AI analysis timeout | Increase timeout or check backend logs |
| YOLO not detecting | Check image quality - needs clear civic issue |

---

## Additional Documentation

- `PROJECT_DOCUMENTATION.md` - Complete project reference
- `PRESENTATION_CONTENT.md` - Presentation outline for demo

---

## License

MIT
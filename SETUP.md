# Jan Suvidha: Setup & Run Guide

A complete civic issue reporting system with 3 platforms:
1. **Mobile App** - For citizens (React Native/Expo)
2. **Backend API** - Flask server with AI/ML
3. **Admin Dashboard** - For administrators

## Prerequisites
- **Python 3.10+**
- **MongoDB** (local or Atlas cloud)
- **Node.js** (for mobile app - optional)
- **Ollama** (optional, for AI descriptions)

---

## Quick Start

### Step 1: Start Backend (Required for all platforms)
```powershell
cd backend
python run.py
```

Backend runs at: `http://192.168.1.X:5000` (X = your IP)

---

## Platform Setup

### 📱 Mobile App (Citizens)
```powershell
cd mobile
npm install
npx expo start
```
- Scan QR code with Expo Go app on phone
- Or build APK for standalone installation
- Update IP in `App.js` to match your laptop's IP

**Features:**
- Login/Register
- Report Issues (with photo + GPS)
- View All Issues
- Map View
- My Reported Issues

---

### 🖥️ Admin Dashboard (Administrators)
1. Open `admin_dashboard/index.html` in browser
2. Login with admin account
3. Access dashboards:
   - Overview (stats + charts)
   - All Issues (manage, assign, update status)
   - Departments (efficiency rankings)
   - Analytics
   - Users

**Features:**
- Full analytics with Chart.js
- Issue management (assign, status updates)
- Department efficiency tracking
- User management
- Export capabilities

---

## Configuration

### Backend Environment
The backend uses `.env` file in `/backend`:
```env
SECRET_KEY=your_secret_key
MONGODB_URI=mongodb://localhost:27017/JanSuvidha
EMBED_BACKEND=local
OLLAMA_MODEL=llama3
SIMILARITY_THRESHOLD=0.78
```

### Mobile App
Edit `mobile/App.js`:
```javascript
const API_URL = 'http://192.168.1.X:5000';  // Your laptop's IP
```

### Admin Dashboard
Edit `admin_dashboard/index.html`:
```javascript
const API_BASE = 'http://192.168.1.X:5000';  // Your laptop's IP
```

---

## Making a User Admin

Access MongoDB:
```powershell
mongosh
use JanSuvidha
db.users.updateOne({"email": "admin@email.com"}, {$set: {"role": "admin"}})
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot connect to backend | Check IP address is correct in mobile/admin |
| Mobile app not loading | Keep backend running on same network |
| Login fails | Check user role is "admin" in MongoDB |
| Camera not working | Grant camera permission on phone |

---

## Project Structure
```
JanSuvidha/
├── backend/           # Flask API Server
│   ├── app/           # Routes, Models, Services
│   └── .env          # Configuration
│
├── mobile/            # React Native App
│   ├── App.js        # Main app
│   └── src/screens/  # All screens
│
├── admin_dashboard/   # Admin Portal
│   └── index.html    # Single-page dashboard
│
├── models_ai/         # YOLO models
├── SETUP.md          # This guide
└── requirements.txt   # Python dependencies
```
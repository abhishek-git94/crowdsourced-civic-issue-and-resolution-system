# Jan Suvidha Admin Dashboard

A dedicated admin platform for managing the civic issue reporting system.

## 3-Section Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     JAN SUVIDHA PLATFORM                        │
├─────────────────┬─────────────────┬───────────────────────────┤
│   Mobile App    │    Backend      │   Admin Dashboard          │
│   (Citizens)    │    (API)        │   (Administrators)         │
│                 │                 │                           │
│  /mobile/       │   /backend/     │   /admin_dashboard/        │
│  - Report       │   - Flask API    │   - Analytics             │
│  - View Issues  │   - MongoDB     │   - Issue Management       │
│  - My Issues    │   - YOLO/AI     │   - Department Control    │
│  - Map          │   - Auth        │   - User Management       │
└─────────────────┴─────────────────┴───────────────────────────┘
```

## How to Run

### 1. Start Backend (Required)
```powershell
cd backend
python run.py
```

### 2. Open Admin Dashboard
Open `admin_dashboard/index.html` in your browser:
```
file:///C:/.../admin_dashboard/index.html
```

Or serve it:
```powershell
cd admin_dashboard
python -m http.server 8000
# Then open http://localhost:8000
```

### 3. Login
- Use an admin account (role = 'admin')
- Or login with any user and it will check for admin role

## Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Overview with stats, charts, recent issues |
| **All Issues** | Full issue list with filters and search |
| **Departments** | Department efficiency and rankings |
| **Analytics** | Charts and metrics |
| **Users** | User management |

## Important

1. **Keep backend running** while using admin dashboard
2. **Update API URL** in index.html if needed (line ~320)
3. Default backend: `http://192.168.1.100:5000`

## For Presentation

- Open admin dashboard on laptop
- Show different sections:
  - Overview with charts
  - Issue management
  - Department efficiency
  - User analytics
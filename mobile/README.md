# Jan Suvidha Mobile App

React Native (Expo) mobile application for the Jan Suvidha Civic Issue Reporting System.

## Features

- 🔐 User Login/Registration
- 📸 Report Issues with Photo & Location
- 🗺️ Interactive Map View
- 📋 View All Issues
- 👤 My Issues Dashboard

## Prerequisites

1. **Node.js** installed (v18 or higher)
2. **Backend** running on your laptop

## Setup Instructions

### Step 1: Configure Backend IP Address

Before running the app, you need to set your laptop's IP address:

1. Open `App.js` in the mobile folder
2. Find this line:
   ```javascript
   const API_URL = 'http://YOUR_LAPTOP_IP:5000';
   ```
3. Replace `YOUR_LAPTOP_IP` with your actual IP address:
   - **Windows**: Run `ipconfig` in command prompt, look for "IPv4 Address"
   - **Example**: `http://192.168.1.100:5000`

### Step 2: Install Dependencies

```bash
cd mobile
npm install
```

### Step 3: Run the App

```bash
npx expo start
```

### Step 4: Connect Your Phone

**Option A: Expo Go App (Recommended)**
1. Install "Expo Go" app on your phone from App Store/Play Store
2. Scan the QR code shown in terminal
3. App will load on your phone

**Option B: Build APK (For offline use)**
1. `npx expo prebuild`
2. `npx expo run:android`
3. Install generated APK on your phone

## How It Works

```
┌─────────────────────────────────────────────┐
│           Your Laptop (Backend)             │
│            http://192.168.1.X:5000          │
└─────────────────────────────────────────────┘
                     ↑
                     │ API Calls
                     │
┌─────────────────────────────────────────────┐
│          Mobile App (Your Phone)           │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │  Home  │ │ Report  │ │   Map   │       │
│  │ Issues │ │  Issue  │ │  View   │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│                                             │
│  ┌─────────┐                                │
│  │My Issues│                                │
│  └─────────┘                                │
└─────────────────────────────────────────────┘
```

## Important Notes

1. **Keep backend running** while using the mobile app
2. **Same WiFi** - Phone and laptop must be on same network
3. **Firewall** - If issues arise, disable Windows Firewall temporarily

## Troubleshooting

- **"Cannot connect to server"**: Check your IP address is correct
- **Camera not working**: Grant camera permission in phone settings
- **Location not working**: Grant location permission in phone settings
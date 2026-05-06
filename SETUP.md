# Jan Suvidha: Setup & Run Guide

Follow these steps to set up the development environment and run the Jan Suvidha platform.

## Prerequisites
- **Python 3.10+**
- **MongoDB** (local or Atlas cloud)
- **Ollama** (optional, for AI description generation)

---

## 1. Environment Setup

### Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 2. Configuration (`.env`)

Create a `.env` file in the `backend/` directory with the following variables:

```env
SECRET_KEY=your_secret_key_here
MONGODB_URI=mongodb://localhost:27017/JanSuvidha
EMBED_BACKEND=local
OLLAMA_MODEL=llama3
SIMILARITY_THRESHOLD=0.78
```

> [!IMPORTANT]
> - For local MongoDB: `mongodb://localhost:27017/JanSuvidha`
> - For MongoDB Atlas: Use your connection string
> - Ensure MongoDB service is running before starting the app

---

## 3. AI Model Setup

### Ollama (NLP - Optional)
1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull the required model:
   ```bash
   ollama pull llama3
   ```
If Ollama is not available, the system will use fallback descriptions.

### YOLO (Image Detection)
Ensure the following weights exist in the `models_ai/` directory:
- `last_jansuvidha.pt` (Custom trained model - Required)
- `yolov8n.pt` or `yolov8s.pt` (Fallback)

### Sentence Transformers (Duplicate Detection)
The `sentence-transformers` package will download `all-MiniLM-L6-v2` automatically on first use.

---

## 4. Database Initialization
MongoDB will automatically create the `JanSuvidha` database and collections on first run. No manual setup required.

---

## 5. Running the Project

### Start the Backend
```powershell
cd backend
python run.py
```

The application will be available at: `http://127.0.0.1:5000`

---

## 6. Accessing the System
- **Citizen Access**: Register a new account on the landing page.
- **Official Access**: After registering, manually change the user's `role` to `admin` or `manager` in MongoDB to access the Authority Dashboard.

### Accessing MongoDB (for role change)
```powershell
mongosh
use JanSuvidha
db.users.updateOne({"email": "your@email.com"}, {$set: {"role": "admin"}})
```

---

## Troubleshooting
- **Database Connection Error**: Verify your `MONGODB_URI` and ensure MongoDB is running.
- **AI Analysis Fails**: Ensure Ollama is running (`ollama serve`) or use fallback mode.
- **Missing Images**: Ensure the `frontend/static/uploads` directory exists (created automatically on first upload).
- **Embedding Errors**: First run will download the sentence-transformer model (~90MB).
# Jan Suvidha: Setup & Run Guide

Follow these steps to set up the development environment and run the Jan Suvidha platform.

## Prerequisites
- **Python 3.10+**
- **PostgreSQL** (Installed and running)
- **Ollama** (For NLP description generation)

---

## 1. Environment Setup

### Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
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
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civic_db
EMBED_BACKEND=local
OLLAMA_MODEL=llama3
SIMILARITY_THRESHOLD=0.78
```

> [!IMPORTANT]
> Ensure the `DATABASE_URL` matches your local PostgreSQL credentials and that the database `civic_db` exists.

---

## 3. AI Model Setup

### Ollama (NLP)
1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull the required model:
   ```bash
   ollama pull llama3
   ```

### YOLO (Image Detection)
Ensure the following weights exist in the `models_ai/` directory:
- `last_jansuvidha.pt` (Required)
- `yolov8n.pt` (Fallback)

---

## 4. Database Initialization
The project is configured to automatically create tables on the first run. Ensure your PostgreSQL service is running before starting the app.

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
- **Official Access**: After registering, manually change the user's `role` to `admin` or `manager` in the database to access the Authority Dashboard.

---

## Troubleshooting
- **Database Connection Error**: Verify your `DATABASE_URL` and ensure PostgreSQL is allowing connections on port 5432.
- **AI Analysis Fails**: Ensure Ollama is running in the background (`ollama serve`) and the models have been pulled.
- **Missing Images**: Ensure the `backend/app/static/uploads` directory exists (it should be created automatically).

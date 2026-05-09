import os
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*authlib.jose module is deprecated.*")

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\nJan Suvidha System Active!")
    print(f"   Backend API:       http://127.0.0.1:{port}")
    print(f"   Admin Dashboard:   http://127.0.0.1:{port}/admin-portal/")
    print(f"\n   Use the Backend API URL for mobile app and dashboard configuration.\n")
    
    app.run(debug=True, host=host, port=port)

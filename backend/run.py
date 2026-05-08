from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Bind to 0.0.0.0 to allow access from any device on network
    # Get port from environment or use default 5000
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n🚀 Jan Suvidha Backend Running!")
    print(f"   Local:   http://127.0.0.1:{port}")
    print(f"   Network: http://{host}:{port}")
    print(f"\n   Use this URL for mobile app & admin dashboard\n")
    
    app.run(debug=True, host=host, port=port)

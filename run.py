import os
from dotenv import load_dotenv
from app.app import create_app

load_dotenv()  # ← charge le .env

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
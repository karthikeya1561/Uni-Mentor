
from app import create_app
from dotenv import load_dotenv
import os

load_dotenv() # Load variables from .env

if os.environ.get("GEMINI_API_KEY"):
    print("✅ GEMINI_API_KEY found in environment!")
else:
    print("❌ GEMINI_API_KEY NOT found in environment. Please check your .env file.")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

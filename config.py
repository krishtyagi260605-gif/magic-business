import os
from dotenv import load_dotenv

load_dotenv()

# App settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Default brand configuration
DEFAULT_BRAND_COLOR = "#2563EB"  # Magic Blue

# Ensure required directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

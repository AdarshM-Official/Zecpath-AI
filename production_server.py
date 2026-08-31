import logging
import os
import sys

# Configure production logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/production.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("waitress")

try:
    from waitress import serve
except ImportError:
    logger.error("Waitress WSGI server not installed. Please run: pip install waitress")
    sys.exit(1)

# Import the main Flask app
from app import app

def start_production_server():
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Zecpath-AI Production Server on port {port}...")
    
    # Waitress is a production-quality pure-Python WSGI server suitable for Windows
    serve(
        app, 
        host="0.0.0.0", 
        port=port, 
        threads=8, 
        connection_limit=1000,
        cleanup_interval=30
    )

if __name__ == "__main__":
    start_production_server()

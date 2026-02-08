"""
Learning Finnish Flask backend.
Serves React SPA from /static and provides API endpoints.
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get absolute path to static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

# Configure Flask for static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

@app.route('/health')
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return {"status": "ok"}, 200

@app.route('/')
def serve_root():
    """Serve index.html for root path"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files or fall back to index.html for SPA routing"""
    file_path = os.path.join('static', path)
    if os.path.isfile(file_path):
        return send_from_directory('static', path)
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=False, port=8000, host='0.0.0.0')

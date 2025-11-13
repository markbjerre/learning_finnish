from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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
    app.run(debug=False, port=8000)

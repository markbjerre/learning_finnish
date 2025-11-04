from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import time
import logging
from prompts import build_word_lookup_prompt, build_translation_prompt
from cache import WordCache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Static folder path: {os.path.abspath('static')}")
logger.info(f"Static folder exists: {os.path.exists('static')}")
if os.path.exists('static'):
    logger.info(f"Static folder contents: {os.listdir('static')[:5]}")  # First 5 items

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize cache
word_cache = WordCache(cache_dir='cache', ttl_hours=24)

# ===== API ROUTES (must come BEFORE wildcard routes) =====

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/debug')
def debug():
    """Debug route to check server state"""
    return jsonify({
        "cwd": os.getcwd(),
        "static_exists": os.path.exists('static'),
        "index_exists": os.path.exists('static/index.html'),
        "static_contents": os.listdir('static') if os.path.exists('static') else []
    }), 200

@app.route('/api/word/<word>', methods=['GET'])
def get_word(word):
    """
    Get word translation and details using AI
    Query params: source_lang (default: 'fi'), target_lang (default: 'da')
    """
    start_time = time.time()
    source_lang = request.args.get('source_lang', 'fi')
    target_lang = request.args.get('target_lang', 'da')
    
    try:
        # Check cache first (< 1ms!)
        cache_start = time.time()
        cached_result = word_cache.get(word, source_lang, target_lang)
        cache_time = time.time() - cache_start
        
        if cached_result:
            # Cache hit! Return immediately
            total_time = time.time() - start_time
            cached_result['_timing'] = {
                'total_ms': round(total_time * 1000, 2),
                'cache_lookup_ms': round(cache_time * 1000, 2),
                'cached': True,
                'openai_api_ms': 0
            }
            app.logger.info(f"✅ Cache hit for word: {word} in {total_time*1000:.2f}ms")
            return jsonify(cached_result), 200
        
        # Cache miss - call OpenAI
        app.logger.info(f"⚠️ Cache miss for word: {word}, calling OpenAI...")
        
        # Build prompts using external module
        prompt_start = time.time()
        system_prompt, user_prompt = build_word_lookup_prompt(word, source_lang, target_lang)
        prompt_time = time.time() - prompt_start
        
        # Call OpenAI API
        api_start = time.time()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Faster alternative to gpt-4o-mini
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        api_time = time.time() - api_start
        
        # Parse response
        parse_start = time.time()
        result = json.loads(response.choices[0].message.content)
        parse_time = time.time() - parse_start
        
        # Cache the result for next time
        word_cache.set(word, result, source_lang, target_lang)
        
        total_time = time.time() - start_time
        
        # Add timing information to response
        result['_timing'] = {
            'total_ms': round(total_time * 1000, 2),
            'cache_lookup_ms': round(cache_time * 1000, 2),
            'prompt_build_ms': round(prompt_time * 1000, 2),
            'openai_api_ms': round(api_time * 1000, 2),
            'parse_ms': round(parse_time * 1000, 2),
            'cached': False
        }
        
        app.logger.info(f"Successfully processed word: {word} in {total_time:.2f}s")
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Error processing word {word}: {str(e)}")
        return jsonify({
            "error": "Failed to process word",
            "message": str(e)
        }), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """
    Translate text using AI
    Body: { "text": str, "source_lang": str, "target_lang": str }
    """
    start_time = time.time()
    data = request.get_json()
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'fi')
    target_lang = data.get('target_lang', 'da')
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        # Build prompts using external module
        system_prompt, user_prompt = build_translation_prompt(text, source_lang, target_lang)
        
        # Call OpenAI API
        api_start = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        api_time = time.time() - api_start
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        total_time = time.time() - start_time
        
        # Add timing information
        result['_timing'] = {
            'total_ms': round(total_time * 1000, 2),
            'openai_api_ms': round(api_time * 1000, 2)
        }
        
        app.logger.info(f"Translated from {source_lang} to {target_lang} in {total_time:.2f}s")
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Translation error: {str(e)}")
        return jsonify({
            "error": "Translation failed",
            "message": str(e)
        }), 500

@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    return jsonify(word_cache.stats()), 200

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache (optionally for specific word)"""
    data = request.get_json() or {}
    word = data.get('word')
    word_cache.clear(word)
    return jsonify({
        "message": f"Cache cleared for '{word}'" if word else "All cache cleared"
    }), 200

# ===== STATIC FILE ROUTES (must come AFTER all API routes) =====

@app.route('/')
def serve_index():
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        return {"error": f"Could not serve index.html: {str(e)}"}, 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        # Get full file path
        file_path = os.path.join('static', path)
        abs_file_path = os.path.abspath(file_path)
        static_abs = os.path.abspath('static')
        
        # Security check: ensure file is within static directory
        if not abs_file_path.startswith(static_abs):
            logger.warning(f"Path traversal attempt: {path}")
            return jsonify({"error": "Not found"}), 404
        
        # Check if file exists and is a file
        if os.path.isfile(abs_file_path):
            logger.info(f"✅ Serving static file: {path}")
            return send_from_directory('static', path)
        
        # File not found - log for debugging
        logger.warning(f"❌ File not found: {abs_file_path} (exists: {os.path.exists(abs_file_path)}, isfile: {os.path.isfile(abs_file_path)})")
        
        # Fall back to index.html for SPA routing
        logger.info(f"Falling back to index.html for SPA route: {path}")
        return send_from_directory('static', 'index.html')
    except Exception as e:
        logger.error(f"Error serving {path}: {str(e)}", exc_info=True)
        return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=False, port=5003)

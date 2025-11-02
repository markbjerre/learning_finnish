from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Finnish Learning API"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/api/word/<word>', methods=['GET'])
def get_word(word):
    """
    Get word translation and details
    Query params: source_lang (default: 'fi'), target_lang (default: 'da')
    """
    source_lang = request.args.get('source_lang', 'fi')
    target_lang = request.args.get('target_lang', 'da')
    
    # TODO: Implement AI-powered word lookup using OpenAI
    # For now, return mock structure
    return jsonify({
        "word": word,
        "translation": f"{word} (oversættelse)",
        "pronunciation": f"/{word}/",
        "partOfSpeech": "substantiv",
        "forms": {
            "nominative": word,
            "genitive": f"{word}n",
            "partitive": f"{word}a",
            "illative": f"{word}an"
        },
        "example": f"Tämä on esimerkki lause \"{word}\".",
        "wordHints": [
            {"word": "Tämä", "translation": "denne/dette"},
            {"word": "esimerkki", "translation": "eksempel"}
        ],
        "memoryAid": "En sjov måde at huske dette ord på...",
        "category": "substantiv"
    }), 200

@app.route('/api/translate', methods=['POST'])
def translate():
    """
    Translate text using AI
    Body: { "text": str, "source_lang": str, "target_lang": str }
    """
    data = request.get_json()
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'fi')
    target_lang = data.get('target_lang', 'da')
    
    # TODO: Implement AI-powered translation
    return jsonify({
        "original": text,
        "translation": f"Translated: {text}",
        "source_lang": source_lang,
        "target_lang": target_lang
    }), 200

if __name__ == '__main__':
    app.run(debug=False)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def index():
    return "Finnish Learning API"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/api/word/<word>', methods=['GET'])
def get_word(word):
    """
    Get word translation and details using AI
    Query params: source_lang (default: 'fi'), target_lang (default: 'da')
    """
    source_lang = request.args.get('source_lang', 'fi')
    target_lang = request.args.get('target_lang', 'da')
    
    try:
        # Create structured prompt for AI
        prompt = f"""You are a Finnish language expert. Analyze the Finnish word "{word}" and provide comprehensive learning information in Danish.

Return a JSON object with this exact structure:
{{
  "word": "{word}",
  "translation": "Danish translation",
  "pronunciation": "IPA or simplified pronunciation",
  "partOfSpeech": "substantiv/verb/adjektiv/etc",
  "forms": {{
    "nominative": "nominative form",
    "genitive": "genitive form", 
    "partitive": "partitive form",
    "illative": "illative form"
  }},
  "example": "A Finnish sentence using the word",
  "wordHints": [
    {{"word": "word1", "translation": "Danish translation"}},
    {{"word": "word2", "translation": "Danish translation"}}
  ],
  "memoryAid": "A creative mnemonic or memory tip in Danish",
  "category": "Part of speech in Danish (substantiv/verb/adjektiv)"
}}

Important:
- All explanations should be in Danish
- Provide accurate Finnish grammatical forms
- Make the example sentence natural and useful
- Include 2-3 word hints for difficult words in the example
- Create a memorable and fun memory aid
- Be accurate with linguistic details"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Finnish language expert who provides detailed word analysis. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        app.logger.info(f"Successfully processed word: {word}")
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
    data = request.get_json()
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'fi')
    target_lang = data.get('target_lang', 'da')
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        lang_names = {
            'fi': 'Finnish',
            'da': 'Danish',
            'en': 'English'
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a professional translator. Translate from {source_name} to {target_name}. Provide only the translation, no explanations."
                },
                {
                    "role": "user", 
                    "content": text
                }
            ],
            temperature=0.3
        )
        
        translation = response.choices[0].message.content.strip()
        app.logger.info(f"Translated from {source_lang} to {target_lang}")
        
        return jsonify({
            "original": text,
            "translation": translation,
            "source_lang": source_lang,
            "target_lang": target_lang
        }), 200
        
    except Exception as e:
        app.logger.error(f"Translation error: {str(e)}")
        return jsonify({
            "error": "Translation failed",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False)

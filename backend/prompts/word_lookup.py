"""
Prompt builders for Finnish language learning API
"""

def build_word_lookup_prompt(word, source_lang='fi', target_lang='da'):
    """
    Build the AI prompt for word lookup and analysis.
    
    Args:
        word: The Finnish word to analyze
        source_lang: Source language (default: 'fi')
        target_lang: Target language (default: 'da')
    
    Returns:
        tuple: (system_prompt, user_prompt)
    """
    
    system_prompt = "You are a Finnish language expert who provides detailed word analysis. Always respond with valid JSON only."
    
    user_prompt = f"""You are a Finnish language expert. Analyze the Finnish word "{word}" and provide comprehensive learning information in Danish.

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
    
    return system_prompt, user_prompt


def build_translation_prompt(text, source_lang='fi', target_lang='da'):
    """
    Build the AI prompt for text translation.
    
    Args:
        text: The text to translate
        source_lang: Source language (default: 'fi')
        target_lang: Target language (default: 'da')
    
    Returns:
        tuple: (system_prompt, user_prompt)
    """
    
    system_prompt = "You are a professional translator. Always respond with valid JSON only."
    
    user_prompt = f"""Translate the following text from {source_lang} to {target_lang}.

Return a JSON object with this structure:
{{
  "original": "{text}",
  "translation": "translated text",
  "source_lang": "{source_lang}",
  "target_lang": "{target_lang}"
}}

Text to translate: "{text}"

Provide an accurate, natural-sounding translation."""
    
    return system_prompt, user_prompt

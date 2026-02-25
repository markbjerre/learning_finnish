"""
LLM-powered Finnish inflection generator.
Called when a new word is added via API or OpenClaw.
"""

import json
import logging
import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models_db import Word, Inflection, VerbForm
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


def _extract_json(content: str) -> str:
    """Strip <think>...</think> reasoning blocks and code fences, return clean JSON string."""
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return content


NOUN_CASES = [
    "nominatiivi", "genetiivi", "partitiivi", "inessiivi", "elatiivi",
    "illatiivi", "adessiivi", "ablatiivi", "allatiivi", "essiivi",
    "translatiivi", "abessiivi",
]


async def generate_and_store_inflections(db: AsyncSession, word: Word) -> dict:
    """
    Generate inflections for a word using the LLM, then store them in the DB.

    Returns dict with counts: {"inflections": N, "verb_forms": N}
    """
    pos = (word.part_of_speech or "noun").lower()

    if not getattr(ai_service, "use_ai", False) or not getattr(ai_service, "client", None):
        logger.info(
            f"No AI API configured, skipping inflection generation for '{word.finnish_word}'"
        )
        return {"inflections": 0, "verb_forms": 0}

    try:
        if pos == "verb":
            return await _generate_verb_forms(db, word)
        else:
            return await _generate_noun_adj_inflections(db, word)
    except Exception as e:
        logger.error(f"Failed to generate inflections for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}


async def _generate_noun_adj_inflections(db: AsyncSession, word: Word) -> dict:
    """Generate noun/adjective case inflections."""
    prompt = f"""Generate all Finnish grammatical case forms for the word: "{word.finnish_word}" ({word.part_of_speech})
Translation: {getattr(word, 'danish_translation', None) or word.english_translation}

Provide singular and plural for these cases:
{', '.join(NOUN_CASES)}

Return ONLY this JSON (no other text):
{{
  "inflections": [
    {{"case_name": "nominatiivi", "singular": "...", "plural": "..."}},
    ...
  ],
  "notes": "any irregularity notes"
}}"""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        content = _extract_json(response.choices[0].message.content or "")

        data = json.loads(content)
        inflections = data.get("inflections", [])

        count = 0
        for infl in inflections:
            db.add(
                Inflection(
                    id=str(uuid.uuid4()),
                    word_id=word.id,
                    case_name=infl.get("case_name", ""),
                    singular=infl.get("singular"),
                    plural=infl.get("plural"),
                    notes=data.get("notes"),
                )
            )
            count += 1

        await db.commit()
        logger.info(f"Generated {count} inflections for '{word.finnish_word}'")
        return {"inflections": count, "verb_forms": 0}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse inflection response for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}


async def _generate_verb_forms(db: AsyncSession, word: Word) -> dict:
    """Generate verb conjugation forms."""
    prompt = f"""Generate Finnish verb conjugation forms for: "{word.finnish_word}"
Translation: {getattr(word, 'danish_translation', None) or word.english_translation}

Provide these forms:
- All persons (minä, sinä, hän, me, te, he) in preesens and imperfekti
- passiivi (preesens and imperfekti)
- konditionaali (minä)
- imperatiivi (sinä)

Return ONLY this JSON (no other text):
{{
  "verb_forms": [
    {{"form_name": "minä", "form_value": "...", "tense": "preesens"}},
    {{"form_name": "minä", "form_value": "...", "tense": "imperfekti"}},
    ...
  ],
  "notes": "verb type and any irregularity notes"
}}"""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        content = _extract_json(response.choices[0].message.content or "")

        data = json.loads(content)
        forms = data.get("verb_forms", [])

        count = 0
        for form in forms:
            db.add(
                VerbForm(
                    id=str(uuid.uuid4()),
                    word_id=word.id,
                    form_name=form.get("form_name", ""),
                    form_value=form.get("form_value", ""),
                    tense=form.get("tense"),
                    notes=data.get("notes"),
                )
            )
            count += 1

        await db.commit()
        logger.info(f"Generated {count} verb forms for '{word.finnish_word}'")
        return {"inflections": 0, "verb_forms": count}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse verb form response for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}

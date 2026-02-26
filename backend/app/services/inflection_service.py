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

NON_INFLECTING = {
    "adverb", "adverbi", "conjunction", "konjunktio",
    "particle", "partikkeli", "interjection", "interjectio",
    "preposition", "prepositio", "postposition", "postpositio",
}


async def normalize_word(input_text: str, source_lang: str | None = None) -> dict:
    """
    Normalize a word submission: detect language, translate to Finnish if needed,
    correct spelling, find the base form (lemma), and identify word type.

    Args:
        input_text: The word as submitted (Finnish, Danish, or English)
        source_lang: Optional hint ("fi", "da", "en"). If None, LLM auto-detects.

    Returns:
        {
            "finnish": "talo",
            "danish": "hus",
            "english": "house",
            "word_type": "noun",
            "detected_lang": "da",
            "was_corrected": false,
            "correction_note": null,
            "valid": true,
            "error": null
        }
    """
    if not getattr(ai_service, "use_ai", False) or not getattr(ai_service, "client", None):
        logger.info("No AI configured, returning input as-is")
        return {
            "finnish": input_text,
            "danish": None,
            "english": None,
            "word_type": "noun",
            "detected_lang": source_lang or "fi",
            "was_corrected": False,
            "correction_note": None,
            "valid": True,
            "error": None,
        }

    lang_hint = f'\nThe user indicated the word is in: {source_lang}' if source_lang else ''

    prompt = f"""A language student submitted this word: "{input_text}"{lang_hint}

Your task:
1. Detect the language (Finnish, Danish, or English)
2. If NOT Finnish, translate it to Finnish
3. If Finnish, check the spelling and find the base/dictionary form (lemma).
   For example: "talossa" → "talo", "juoksin" → "juosta"
4. Provide translations in all three languages (Finnish, Danish, English)
5. Identify the word type (noun, verb, adjective, adverb, pronoun, numeral, conjunction, particle, interjection, preposition, postposition)
6. If the input is not a recognizable word in any of the three languages, set valid=false

Return ONLY this JSON (no other text):
{{
  "finnish": "the Finnish base form",
  "danish": "Danish translation",
  "english": "English translation",
  "word_type": "noun",
  "detected_lang": "fi|da|en",
  "was_corrected": true/false,
  "correction_note": "explanation if corrected, null otherwise",
  "valid": true/false,
  "error": "reason if invalid, null otherwise"
}}"""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Finnish/Danish/English language expert. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )

        content = _extract_json(response.choices[0].message.content or "")
        data = json.loads(content)

        # Ensure all expected keys exist
        return {
            "finnish": data.get("finnish"),
            "danish": data.get("danish"),
            "english": data.get("english"),
            "word_type": data.get("word_type", "noun"),
            "detected_lang": data.get("detected_lang", "fi"),
            "was_corrected": data.get("was_corrected", False),
            "correction_note": data.get("correction_note"),
            "valid": data.get("valid", True),
            "error": data.get("error"),
        }

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to normalize word '{input_text}': {e}")
        return {
            "finnish": input_text,
            "danish": None,
            "english": None,
            "word_type": "noun",
            "detected_lang": source_lang or "fi",
            "was_corrected": False,
            "correction_note": None,
            "valid": True,
            "error": f"Normalization failed: {e}",
        }


async def normalize_word_batch(inputs: list[dict]) -> list[dict]:
    """
    Normalize multiple word submissions in one LLM call.

    Args:
        inputs: [{"text": "hus", "source_lang": "da"}, {"text": "juosta"}, ...]

    Returns: list of normalize_word-style dicts, same order as input.
    """
    if not getattr(ai_service, "use_ai", False) or not getattr(ai_service, "client", None):
        return [
            {
                "finnish": inp.get("text", ""),
                "danish": None,
                "english": None,
                "word_type": "noun",
                "detected_lang": inp.get("source_lang", "fi"),
                "was_corrected": False,
                "correction_note": None,
                "valid": True,
                "error": None,
            }
            for inp in inputs
        ]

    word_list = "\n".join(
        f'{i+1}. "{inp.get("text", "")}"'
        + (f' (language hint: {inp["source_lang"]})' if inp.get("source_lang") else "")
        for i, inp in enumerate(inputs)
    )

    prompt = f"""A language student submitted these words:
{word_list}

For EACH word:
1. Detect the language (Finnish, Danish, or English)
2. If NOT Finnish, translate to Finnish
3. If Finnish, correct spelling and find the base/dictionary form (lemma)
4. Provide translations in Finnish, Danish, and English
5. Identify the word type (noun, verb, adjective, adverb, pronoun, numeral, conjunction, particle, interjection, preposition, postposition)
6. If not recognizable, set valid=false

Return ONLY this JSON (no other text):
[
  {{
    "finnish": "base form",
    "danish": "Danish translation",
    "english": "English translation",
    "word_type": "noun",
    "detected_lang": "fi|da|en",
    "was_corrected": true/false,
    "correction_note": "explanation or null",
    "valid": true/false,
    "error": "reason or null"
  }},
  ...
]
Return exactly {len(inputs)} items in the same order as the input."""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Finnish/Danish/English language expert. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=500 * len(inputs),
        )

        content = _extract_json(response.choices[0].message.content or "")
        results = json.loads(content)

        if not isinstance(results, list) or len(results) != len(inputs):
            raise ValueError(f"Expected {len(inputs)} results, got {len(results) if isinstance(results, list) else 'non-list'}")

        return [
            {
                "finnish": r.get("finnish"),
                "danish": r.get("danish"),
                "english": r.get("english"),
                "word_type": r.get("word_type", "noun"),
                "detected_lang": r.get("detected_lang", "fi"),
                "was_corrected": r.get("was_corrected", False),
                "correction_note": r.get("correction_note"),
                "valid": r.get("valid", True),
                "error": r.get("error"),
            }
            for r in results
        ]

    except Exception as e:
        logger.error(f"Batch normalization failed: {e}, falling back to individual calls")
        results = []
        for inp in inputs:
            r = await normalize_word(inp.get("text", ""), inp.get("source_lang"))
            results.append(r)
        return results


async def generate_and_store_inflections(db: AsyncSession, word: Word) -> dict:
    """
    Generate inflections for a word using the LLM, then store them in the DB.

    Returns dict with counts: {"inflections": N, "verb_forms": N}
    """
    pos = (word.part_of_speech or "noun").lower()

    if pos in NON_INFLECTING:
        logger.info(
            f"Skipping inflection generation for non-inflecting word type '{pos}': '{word.finnish_word}'"
        )
        return {"inflections": 0, "verb_forms": 0}

    if not getattr(ai_service, "use_ai", False) or not getattr(ai_service, "client", None):
        logger.info(
            f"No AI API configured, skipping inflection generation for '{word.finnish_word}'"
        )
        return {"inflections": 0, "verb_forms": 0}

    try:
        if pos in ("verb", "verbi"):
            return await _generate_verb_forms(db, word)
        elif pos in ("adjective", "adjektiivi"):
            return await _generate_adjective_inflections(db, word)
        else:
            return await _generate_noun_inflections(db, word)
    except Exception as e:
        logger.error(f"Failed to generate inflections for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}


async def _generate_noun_inflections(db: AsyncSession, word: Word) -> dict:
    """Generate noun/pronoun/numeral case inflections."""
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
                    degree=None,
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


async def _generate_adjective_inflections(db: AsyncSession, word: Word) -> dict:
    """Generate adjective inflections: base + comparative + superlative, all cases."""
    prompt = f"""Generate all Finnish grammatical case forms for the adjective: "{word.finnish_word}"
Translation: {getattr(word, 'danish_translation', None) or word.english_translation}

Provide singular and plural for these cases:
{', '.join(NOUN_CASES)}

Generate THREE sets of inflections:
1. "positive" — the base form (e.g. nopea)
2. "comparative" — the comparative form (e.g. nopeampi)
3. "superlative" — the superlative form (e.g. nopein)

Return ONLY this JSON (no other text):
{{
  "positive": [
    {{"case_name": "nominatiivi", "singular": "nopea", "plural": "nopeat"}},
    ...
  ],
  "comparative": [
    {{"case_name": "nominatiivi", "singular": "nopeampi", "plural": "nopeammat"}},
    ...
  ],
  "superlative": [
    {{"case_name": "nominatiivi", "singular": "nopein", "plural": "nopeimmat"}},
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
            max_tokens=4000,
        )

        content = _extract_json(response.choices[0].message.content or "")

        data = json.loads(content)
        notes = data.get("notes")

        count = 0
        for degree in ("positive", "comparative", "superlative"):
            inflections = data.get(degree, [])
            # Map "positive" to None in DB (base form)
            db_degree = None if degree == "positive" else degree
            for infl in inflections:
                db.add(
                    Inflection(
                        id=str(uuid.uuid4()),
                        word_id=word.id,
                        case_name=infl.get("case_name", ""),
                        degree=db_degree,
                        singular=infl.get("singular"),
                        plural=infl.get("plural"),
                        notes=notes,
                    )
                )
                count += 1

        await db.commit()
        logger.info(f"Generated {count} adjective inflections for '{word.finnish_word}'")
        return {"inflections": count, "verb_forms": 0}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse adjective inflection response for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}


async def _generate_verb_forms(db: AsyncSession, word: Word) -> dict:
    """Generate verb conjugation forms including infinitives and participles."""
    prompt = f"""Generate Finnish verb conjugation forms for: "{word.finnish_word}"
Translation: {getattr(word, 'danish_translation', None) or word.english_translation}

Provide these forms:

CONJUGATIONS:
- All persons (minä, sinä, hän, me, te, he) in preesens and imperfekti
- passiivi (preesens and imperfekti)
- konditionaali (minä)
- imperatiivi (sinä)

INFINITIVES:
- 1st infinitive short (basic dictionary form, e.g. "juoda")
- 1st infinitive long (e.g. "juodakseen")
- 2nd infinitive inessive (e.g. "juodessa")
- 3rd infinitive illative (e.g. "juomaan")
- 3rd infinitive inessive (e.g. "juomassa")
- 3rd infinitive elative (e.g. "juomasta")
- 3rd infinitive adessive (e.g. "juomalla")
- 3rd infinitive abessive (e.g. "juomatta")

PARTICIPLES:
- present active participle (e.g. "juova")
- present passive participle (e.g. "juotava")
- past active participle (e.g. "juonut")
- past passive participle (e.g. "juotu")
- agent participle (e.g. "juoma")

Return ONLY this JSON (no other text):
{{
  "verb_forms": [
    {{"form_name": "minä", "form_value": "...", "tense": "preesens"}},
    {{"form_name": "minä", "form_value": "...", "tense": "imperfekti"}},
    {{"form_name": "1st infinitive short", "form_value": "...", "tense": null}},
    {{"form_name": "present active participle", "form_value": "...", "tense": null}},
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
            max_tokens=4000,
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


async def generate_batch_inflections(db: AsyncSession, words: list[Word]) -> dict:
    """
    Generate inflections for multiple words in batched LLM calls.
    Groups words by type: nouns, adjectives, verbs (one call per group).
    Non-inflecting types are skipped.

    Returns: {"inflections": total, "verb_forms": total, "skipped": N}
    """
    if not getattr(ai_service, "use_ai", False) or not getattr(ai_service, "client", None):
        logger.info("No AI API configured, skipping batch inflection generation")
        return {"inflections": 0, "verb_forms": 0, "skipped": len(words)}

    nouns = []
    adjectives = []
    verbs = []
    skipped = 0

    for w in words:
        pos = (w.part_of_speech or "noun").lower()
        if pos in NON_INFLECTING:
            skipped += 1
        elif pos in ("verb", "verbi"):
            verbs.append(w)
        elif pos in ("adjective", "adjektiivi"):
            adjectives.append(w)
        else:
            nouns.append(w)

    total_infl = 0
    total_verb = 0

    if nouns:
        result = await _batch_noun_inflections(db, nouns)
        total_infl += result["inflections"]
    if adjectives:
        result = await _batch_adjective_inflections(db, adjectives)
        total_infl += result["inflections"]
    if verbs:
        result = await _batch_verb_forms(db, verbs)
        total_verb += result["verb_forms"]

    logger.info(
        f"Batch generated: {total_infl} inflections, {total_verb} verb forms, {skipped} skipped"
    )
    return {"inflections": total_infl, "verb_forms": total_verb, "skipped": skipped}


async def _batch_noun_inflections(db: AsyncSession, words: list[Word]) -> dict:
    """Generate case inflections for multiple nouns in one LLM call."""
    word_list = "\n".join(
        f'- "{w.finnish_word}" ({w.part_of_speech}, id={w.id}): {getattr(w, "danish_translation", None) or w.english_translation}'
        for w in words
    )

    prompt = f"""Generate all Finnish grammatical case forms for these words:
{word_list}

For EACH word, provide singular and plural for these cases:
{', '.join(NOUN_CASES)}

Return ONLY this JSON (no other text):
{{
  "words": {{
    "<word_id>": {{
      "inflections": [
        {{"case_name": "nominatiivi", "singular": "...", "plural": "..."}},
        ...
      ],
      "notes": "any irregularity notes"
    }},
    ...
  }}
}}"""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000 * len(words),
        )

        content = _extract_json(response.choices[0].message.content or "")
        data = json.loads(content)
        words_data = data.get("words", {})

        count = 0
        for w in words:
            w_data = words_data.get(w.id, {})
            for infl in w_data.get("inflections", []):
                db.add(Inflection(
                    id=str(uuid.uuid4()),
                    word_id=w.id,
                    case_name=infl.get("case_name", ""),
                    degree=None,
                    singular=infl.get("singular"),
                    plural=infl.get("plural"),
                    notes=w_data.get("notes"),
                ))
                count += 1

        await db.commit()
        logger.info(f"Batch generated {count} noun inflections for {len(words)} words")
        return {"inflections": count}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Batch noun inflection failed: {e}, falling back to individual calls")
        count = 0
        for w in words:
            r = await _generate_noun_inflections(db, w)
            count += r["inflections"]
        return {"inflections": count}


async def _batch_adjective_inflections(db: AsyncSession, words: list[Word]) -> dict:
    """Generate case inflections (positive/comparative/superlative) for multiple adjectives in one LLM call."""
    word_list = "\n".join(
        f'- "{w.finnish_word}" (id={w.id}): {getattr(w, "danish_translation", None) or w.english_translation}'
        for w in words
    )

    prompt = f"""Generate all Finnish grammatical case forms for these adjectives:
{word_list}

For EACH adjective, provide singular and plural for these cases:
{', '.join(NOUN_CASES)}

Generate THREE sets per adjective: "positive" (base), "comparative", "superlative".

Return ONLY this JSON (no other text):
{{
  "words": {{
    "<word_id>": {{
      "positive": [{{"case_name": "nominatiivi", "singular": "...", "plural": "..."}}, ...],
      "comparative": [{{"case_name": "nominatiivi", "singular": "...", "plural": "..."}}, ...],
      "superlative": [{{"case_name": "nominatiivi", "singular": "...", "plural": "..."}}, ...],
      "notes": "any irregularity notes"
    }},
    ...
  }}
}}"""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=4000 * len(words),
        )

        content = _extract_json(response.choices[0].message.content or "")
        data = json.loads(content)
        words_data = data.get("words", {})

        count = 0
        for w in words:
            w_data = words_data.get(w.id, {})
            notes = w_data.get("notes")
            for degree in ("positive", "comparative", "superlative"):
                db_degree = None if degree == "positive" else degree
                for infl in w_data.get(degree, []):
                    db.add(Inflection(
                        id=str(uuid.uuid4()),
                        word_id=w.id,
                        case_name=infl.get("case_name", ""),
                        degree=db_degree,
                        singular=infl.get("singular"),
                        plural=infl.get("plural"),
                        notes=notes,
                    ))
                    count += 1

        await db.commit()
        logger.info(f"Batch generated {count} adjective inflections for {len(words)} words")
        return {"inflections": count}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Batch adjective inflection failed: {e}, falling back to individual calls")
        count = 0
        for w in words:
            r = await _generate_adjective_inflections(db, w)
            count += r["inflections"]
        return {"inflections": count}


async def _batch_verb_forms(db: AsyncSession, words: list[Word]) -> dict:
    """Generate verb conjugations, infinitives and participles for multiple verbs in one LLM call."""
    word_list = "\n".join(
        f'- "{w.finnish_word}" (id={w.id}): {getattr(w, "danish_translation", None) or w.english_translation}'
        for w in words
    )

    prompt = f"""Generate Finnish verb conjugation forms for these verbs:
{word_list}

For EACH verb, provide:

CONJUGATIONS:
- All persons (minä, sinä, hän, me, te, he) in preesens and imperfekti
- passiivi (preesens and imperfekti)
- konditionaali (minä)
- imperatiivi (sinä)

INFINITIVES:
- 1st infinitive short, 1st infinitive long
- 2nd infinitive inessive
- 3rd infinitive illative, inessive, elative, adessive, abessive

PARTICIPLES:
- present active participle, present passive participle
- past active participle, past passive participle
- agent participle

Return ONLY this JSON (no other text):
{{
  "words": {{
    "<word_id>": {{
      "verb_forms": [
        {{"form_name": "minä", "form_value": "...", "tense": "preesens"}},
        {{"form_name": "1st infinitive short", "form_value": "...", "tense": null}},
        ...
      ],
      "notes": "verb type and any irregularity notes"
    }},
    ...
  }}
}}"""

    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=4000 * len(words),
        )

        content = _extract_json(response.choices[0].message.content or "")
        data = json.loads(content)
        words_data = data.get("words", {})

        count = 0
        for w in words:
            w_data = words_data.get(w.id, {})
            for form in w_data.get("verb_forms", []):
                db.add(VerbForm(
                    id=str(uuid.uuid4()),
                    word_id=w.id,
                    form_name=form.get("form_name", ""),
                    form_value=form.get("form_value", ""),
                    tense=form.get("tense"),
                    notes=w_data.get("notes"),
                ))
                count += 1

        await db.commit()
        logger.info(f"Batch generated {count} verb forms for {len(words)} words")
        return {"verb_forms": count}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Batch verb form generation failed: {e}, falling back to individual calls")
        count = 0
        for w in words:
            r = await _generate_verb_forms(db, w)
            count += r["verb_forms"]
        return {"verb_forms": count}

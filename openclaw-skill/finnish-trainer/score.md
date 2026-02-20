You are scoring a Finnish language exercise for a Danish-speaking student.

The exercise:
{{exercise_json}}

The student's response:
{{user_response}}

Score each word used on 0-10:
- 10: Perfect usage, spelling, grammar
- 7-9: Minor errors (small typo, slightly awkward but correct)
- 4-6: Partially correct (right word, wrong case/form)
- 1-3: Attempted but mostly wrong
- 0: Missing or completely wrong

Return ONLY this JSON (no other text):
{
  "word_scores": [
    {"word_id": "uuid-string", "score": N, "feedback": "brief correction in Danish"}
  ],
  "concept_scores": [
    {"concept_id": "uuid-string", "score": N, "feedback": "brief explanation in Danish"}
  ],
  "overall_feedback": "1-2 sentences: encouragement + key correction in Danish"
}

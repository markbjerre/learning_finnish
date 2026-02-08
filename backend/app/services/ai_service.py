"""AI service for generating word definitions and examples using OpenAI API"""

import json
import logging
from typing import Optional, Dict, Any, List
from app.config import settings
from app.models import GrammaticalForm, ExampleSentence

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered word analysis and generation"""

    def __init__(self):
        """Initialize AI service"""
        self.use_openai = bool(settings.openai_api_key)
        if self.use_openai:
            try:
                import openai
                self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.warning("OpenAI library not installed, falling back to mock data")
                self.use_openai = False

    async def get_word_definition(self, finnish_word: str) -> Optional[str]:
        """
        Get AI-generated definition for a Finnish word

        Args:
            finnish_word: The Finnish word to define

        Returns:
            AI-generated definition or None if failed
        """
        if self.use_openai:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Finnish language expert. Provide clear, concise definitions of Finnish words in English.",
                        },
                        {
                            "role": "user",
                            "content": f"Define the Finnish word '{finnish_word}' in English. Provide a clear explanation suitable for language learners.",
                        },
                    ],
                    temperature=0.7,
                    max_tokens=150,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error getting AI definition for '{finnish_word}': {e}")
                return self._get_mock_definition(finnish_word)
        else:
            return self._get_mock_definition(finnish_word)

    async def get_grammatical_forms(
        self, finnish_word: str
    ) -> Optional[List[GrammaticalForm]]:
        """
        Get grammatical forms of a Finnish word (nominative, genitive, partitive, etc.)

        Args:
            finnish_word: The Finnish word

        Returns:
            List of grammatical forms or None if failed
        """
        if self.use_openai:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Finnish grammar expert. Return grammatical forms as a JSON array.",
                        },
                        {
                            "role": "user",
                            "content": f"""For the Finnish word '{finnish_word}', provide the main grammatical cases in JSON format:
[{{"case": "nominative", "finnish": "...", "english": "..."}}, {{"case": "genitive", "finnish": "...", "english": "..."}}]
Return only valid JSON, no other text.""",
                        },
                    ],
                    temperature=0.3,
                    max_tokens=200,
                )

                try:
                    forms_data = json.loads(response.choices[0].message.content)
                    return [GrammaticalForm(**form) for form in forms_data]
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse grammatical forms JSON for '{finnish_word}'")
                    return self._get_mock_grammatical_forms(finnish_word)
            except Exception as e:
                logger.error(f"Error getting grammatical forms for '{finnish_word}': {e}")
                return self._get_mock_grammatical_forms(finnish_word)
        else:
            return self._get_mock_grammatical_forms(finnish_word)

    async def get_example_sentences(
        self, finnish_word: str
    ) -> Optional[List[ExampleSentence]]:
        """
        Get example sentences for a Finnish word with English translations

        Args:
            finnish_word: The Finnish word

        Returns:
            List of example sentences or None if failed
        """
        if self.use_openai:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Finnish language expert. Provide example sentences with translations as JSON.",
                        },
                        {
                            "role": "user",
                            "content": f"""Create 3 example sentences using the Finnish word '{finnish_word}' in JSON format:
[{{"finnish": "...", "english": "..."}}, {{"finnish": "...", "english": "..."}}]
Return only valid JSON, no other text.""",
                        },
                    ],
                    temperature=0.7,
                    max_tokens=300,
                )

                try:
                    sentences_data = json.loads(response.choices[0].message.content)
                    return [ExampleSentence(**sent) for sent in sentences_data]
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse example sentences JSON for '{finnish_word}'")
                    return self._get_mock_examples(finnish_word)
            except Exception as e:
                logger.error(f"Error getting example sentences for '{finnish_word}': {e}")
                return self._get_mock_examples(finnish_word)
        else:
            return self._get_mock_examples(finnish_word)

    # Mock data methods for fallback
    @staticmethod
    def _get_mock_definition(finnish_word: str) -> str:
        """Get mock definition for testing"""
        mock_definitions = {
            "kissa": "A small domesticated carnivorous mammal with soft fur, whiskers, and retractable claws.",
            "koulu": "An institution for educating children and young people.",
            "kirja": "A set of written sheets bound together, containing words and sentences.",
            "ystävä": "A person with whom one has a bond of mutual affection.",
            "kauneus": "The quality of being pleasing to look at; an attractive quality.",
            "mies": "An adult human male.",
            "nainen": "An adult human female.",
            "talo": "A building for human habitation, especially a single-family dwelling.",
            "vesi": "A clear liquid that forms rain, rivers, and oceans; essential for life.",
            "puu": "A woody plant with a stem or trunk that supports branches and leaves.",
        }
        return mock_definitions.get(
            finnish_word.lower(),
            f"A Finnish word meaning something related to {finnish_word}. (Mock definition for testing)"
        )

    @staticmethod
    def _get_mock_grammatical_forms(finnish_word: str) -> List[GrammaticalForm]:
        """Get mock grammatical forms for testing"""
        mock_forms = {
            "kissa": [
                GrammaticalForm(case="nominative", finnish="kissa", english="cat"),
                GrammaticalForm(case="genitive", finnish="kissan", english="of the cat"),
                GrammaticalForm(case="partitive", finnish="kissaa", english="cat (partitive)"),
            ],
            "kirja": [
                GrammaticalForm(case="nominative", finnish="kirja", english="book"),
                GrammaticalForm(case="genitive", finnish="kirjan", english="of the book"),
                GrammaticalForm(case="partitive", finnish="kirjaa", english="book (partitive)"),
            ],
            "vesi": [
                GrammaticalForm(case="nominative", finnish="vesi", english="water"),
                GrammaticalForm(case="genitive", finnish="veden", english="of the water"),
                GrammaticalForm(case="partitive", finnish="vettä", english="water (partitive)"),
            ],
        }

        default_forms = [
            GrammaticalForm(case="nominative", finnish=finnish_word, english=finnish_word),
            GrammaticalForm(
                case="genitive",
                finnish=f"{finnish_word}n",
                english=f"of the {finnish_word}"
            ),
            GrammaticalForm(
                case="partitive",
                finnish=f"{finnish_word}a",
                english=f"{finnish_word} (partitive)"
            ),
        ]

        return mock_forms.get(finnish_word.lower(), default_forms)

    @staticmethod
    def _get_mock_examples(finnish_word: str) -> List[ExampleSentence]:
        """Get mock example sentences for testing"""
        mock_examples = {
            "kissa": [
                ExampleSentence(
                    finnish="Minulla on kissa nimeltä Mirri.",
                    english="I have a cat named Mirri."
                ),
                ExampleSentence(
                    finnish="Kissa istuu ikkunalla.",
                    english="The cat sits by the window."
                ),
                ExampleSentence(
                    finnish="Kissat ovat söpöjä eläimiä.",
                    english="Cats are cute animals."
                ),
            ],
            "kirja": [
                ExampleSentence(
                    finnish="Luen mielellään kirjoja.",
                    english="I like to read books."
                ),
                ExampleSentence(
                    finnish="Tämä kirja on hyvin mielenkiintoinen.",
                    english="This book is very interesting."
                ),
                ExampleSentence(
                    finnish="Hän kirjoitti kolme kirjaa.",
                    english="She wrote three books."
                ),
            ],
            "vesi": [
                ExampleSentence(
                    finnish="Juon juuri nyt lasia vettä.",
                    english="I'm drinking a glass of water right now."
                ),
                ExampleSentence(
                    finnish="Vesi on välttämätöntä elämälle.",
                    english="Water is essential for life."
                ),
                ExampleSentence(
                    finnish="Meeri uimaan vedessä.",
                    english="Mary swims in the water."
                ),
            ],
        }

        default_example = ExampleSentence(
            finnish=f"Sana '{finnish_word}' on hyödyllinen.",
            english=f"The word '{finnish_word}' is useful."
        )

        return mock_examples.get(finnish_word.lower(), [default_example])


# Create singleton instance
ai_service = AIService()

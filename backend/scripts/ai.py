import deepl
from langdetect import detect
import google.generativeai as genai


class LLMCaller:
    def __init__(self):
        MODEL = "gemini-1.5-flash"
        self.api_key = "SECRET_KEY"
        genai.configure(api_key= self.api_key)
        self.model = genai.GenerativeModel(MODEL)

        AUTH_KEY = "SECRET_KEY"

        self.translator = deepl.Translator(AUTH_KEY)


    def translate_to_english(self, text):
        result = self.translator.translate_text(text, target_lang="EN-US")
        return result.text

    def call_llm(self, text):
        if detect(text) != "en":
            text = self.translate_to_english(text)

        prompt = f"""I have this text: {text} (end of text). Analyze the sentiment and emotions in the text and Generate 6 unique and evocative umbrella terms that capture the nuanced feelins expressed.
    Format your response EXACTLY like this, with all on one line:
    term1 : definition1;term2 : definition2;term3 : definition3;term4 : definition4;term5 : definition5;term6 : definition6
    Rules:
    1. Each term should be a single unique word
    2. Use English and foreign terms about 50% of the time each, with non-English wordswhen they capture a complex emotion
    3. Focus on rare or poetic words (like 'ephemeral' or 'ethereal'), can be from any language
    4. Definitions must be brief (5-10 words) but evocative
    5. No basic emotions like 'happy' or 'sad'
    6. All text should be lowercase
    7. No blank lines between terms
    8. No additional text or formatting
    """
        response = self.model.generate_content(prompt)
        return response.text


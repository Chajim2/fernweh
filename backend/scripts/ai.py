import deepl
from pydantic import BaseModel, Field, TypeAdapter
from langdetect import detect
import prompts
from google import genai
from dotenv import load_dotenv
import os
import numpy as np

# Load environment variables
load_dotenv()

MODEL = "gemini-2.0-flash"
EMBEDING_MODEL = "gemini-embedding-001"
EMBEDING_SIZE = 512


class Chunk(BaseModel):
    text: str = Field(description="One atomic part of the text to vector.\
                       All pronouns should be replaced with more specific terms")

chunk_list_type = TypeAdapter(list[Chunk])

class LLMCaller:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(MODEL)
        self.deepl_auth_key = os.getenv('DEEPL_API_KEY')
        if not self.deepl_auth_key:
            raise ValueError("DEEPL_API_KEY not found in environment variables")
        self.translator = deepl.Translator(self.deepl_auth_key)

    def translate_to_english(self, text):
        result = self.translator.translate_text(text, target_lang="EN-US")
        return result.text

    def call_llm(self, text):
        if detect(text) != "en":
            text = self.translate_to_english(text)
        
        response = self.model.generate_content(prompts.get_umbrella_terms(text))
        return response.text


    def get_pieces_to_vector(self, text: str) -> list[str]:
        response = self.client.models.generate_content(
            model = MODEL,
            content = prompts.get_chunks(text),
            config = {
                "response_mime_type" : "application/json",
                "response_json_schema" : chunk_list_type.json_schema()
            }
        )

        return response.text

    def get_embedding(text: str) -> np.ndarray:
        return

    #additional functions meant for toki (rip) that arent in use at the moment might delete later
    def update_user_summary(self, new_entry, summary):
        if detect(new_entry) != "en":
            new_entry = self.translate_to_english(new_entry)
        response = self.model.generate_content(prompts.get_update_user_summary_prompt(new_entry, summary))
        return response.text

    def schedule_day(self, daily_notes, summary, fixed_tasks_json, wake_time, sleep_time, activities, lock_meter):
        if detect(daily_notes) != "en":
            daily_notes = self.translate_to_english(daily_notes)
        
        response = self.model.generate_content(prompts.get_schedule_day_prompt(daily_notes, summary, fixed_tasks_json, wake_time, sleep_time, activities, lock_meter))  
        return response.text

        
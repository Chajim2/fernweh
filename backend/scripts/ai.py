import deepl
from langdetect import detect
import scripts.prompts as prompts
import google.genai as genai
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

#MODEL = "gemini-2.5-flash-lite"
MODEL = "gemini-3.flash-preview"
EMBEDING_MODEL = "gemini-embedding-001"
EMBEDING_SIZE = 512


class Chunk(BaseModel):
    text: str = Field("One atomic part of the orginal text with pronouns replaced\
                       by more specific wors")


class LLMCaller:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=self.api_key)
        
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
        
        response = self.client.models.\
            generate_content(model = MODEL,
                             contents=prompts.get_umbrella_terms(text),
                             )

        return response.text


    def get_pieces_to_vector(self, text: str) -> list[str]:
        response = self.client.models.generate_content(
            model = MODEL,
            contents = prompts.get_chunks(text),
            config=genai.types.GenerateContentConfig(
                response_mime_type= "application/json",
                response_schema= list[Chunk]
            )
        )

        return response.text

    def get_embeddings(self, list_of_chunks: list[str]) -> list[float]:
        response = self.client.models.embed_content(
            model=EMBEDING_MODEL,
            contents=list_of_chunks,
            config=genai.types.EmbedContentConfig(output_dimensionality=768,
                                                  task_type='SEMANTIC_SIMILARITY'),
        )
        
        return response.embeddings

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

        
import requests
import deepl
from langdetect import detect

def translate_to_english(text): 
    auth_key = "b72efb14-f1f3-49a4-a213-2f1a6044483b:fx"  # Replace with your key
    translator = deepl.Translator(auth_key)

    result = translator.translate_text(text, target_lang="EN-US")
    return result.text

def get_emotions(text):
    if detect(text) != "en":
        text = translate_to_english(text)
    headers = {"Authorization": "Bearer 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"}
    payload = { 
        "inputs": text
        }
    

    models = ["google/gemma-2-27b-it", "google/gemma-2-9b-it", "mistralai/Mistral-7B-Instruct-v0.3",
              "google/gemma-2-70b-it","deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"]
    out = []
    for model in models:
        if out != []:
            break
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        query = {
            "inputs": f"""I have this text: {text} (end of text). Analyze the sentiment and emotions in the text and  Generate 6 unique and evocative umbrella terms that capture the nuanced feelins expressed.
Format your response EXACTLY like this, with one term per line:
term1 : definition1
term2 : definition2
term3 : definition3
term4 : definition4
term5 : definition5
term6 : definition6

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
}

        response = requests.post(API_URL, headers=headers, json=query)
        text = response.json()[0]['generated_text'][len(query["inputs"]) + 1:].split("\n")
        for i in text:
            if ":" in i: 
                emotion, definition = i.split(":", 1)  # Split on first colon only
                out.append([emotion.strip(), definition.strip()])
    return out


def analyze_emotions(text):
    API_URL = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
    headers = {"Authorization": "Bearer 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"}
    payload = { 
        "inputs": text
        }
    response = requests.post(API_URL, headers=headers, json=payload)
    emotions = []
    for xd in response.json():
        for i in xd[:10]:
            if 'label' in i:
                emotions.extend([i['label'], i['score']])
    

   


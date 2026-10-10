import ollama

from app.config import settings

def generate_response(prompt: str):
    response = ollama.chat(
        model = settings.LLM_MODEL,
        messages = [
            {
                "role":"user",
                "content": prompt   
            }
        ]
    )
    return response["message"]["content"]
from groq import Groq

from app.core.config import settings


client = Groq(api_key=settings.groq_api_key)


def call_groq(prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
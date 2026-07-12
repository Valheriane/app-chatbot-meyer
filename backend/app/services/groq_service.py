from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)


def call_groq(prompt: str, temperature: float = 0.2) -> str:
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )

    if not response or not response.choices:
        raise ValueError("Réponse vide de l'API Groq.")

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise ValueError("Le modèle a renvoyé une réponse vide.")

    return content
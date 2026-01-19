import aiohttp

API_URL = "https://amari-formic-helene.ngrok-free.dev/v1/chat/completions"

SYSTEM_PROMPT = """
Ты — эксперт по анализу спутниковых систем. 
Твоя задача: дать **конкретные, понятные и краткие рекомендации инженеру**, исходя из предоставленных данных или логов. 
Правила:
Отвечай только текстом рекомендации, без повторения исходного лога.
Не фантазируй, не добавляй лишних слов, не описывай контекст и не придумывай сценарии.
Если входной текст — простой вопрос, напиши ответ кратко и по фактам.
Если текст содержит ошибки, логи или технические данные — анализируй все данные целиком и дай **только полезное действие или проверку** для инженера.
Не дели текст на предложения, анализируй блок целиком.
"""

MAX_TOKENS = 200  # можно увеличить

async def ai_answer(user_text: str) -> str:
    payload = {
        "model": "llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": MAX_TOKENS
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload, timeout=30) as resp:
                resp.raise_for_status()
                data = await resp.json()

        # choices[0]["message"]["content"]
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"[Ошибка ИИ]: {e}"

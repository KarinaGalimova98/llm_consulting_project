import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
    }

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Always answer in Russian."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"OpenRouter returned error: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"OpenRouter network error: {str(exc)}") from exc

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Invalid OpenRouter response format") from exc
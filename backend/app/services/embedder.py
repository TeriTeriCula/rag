from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, EMBED_MODEL

_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await _client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


async def embed_query(text: str) -> list[float]:
    result = await embed_texts([text])
    return result[0]

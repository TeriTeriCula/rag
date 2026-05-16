from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, LLM_MODEL, SIMILARITY_THRESHOLD

_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

NO_CONTEXT_REPLY = (
    "I couldn't find relevant information in the available documents to answer your question."
)


def _build_system_prompt(chunks: list[dict]) -> str:
    if not chunks:
        return (
            "You are a helpful assistant. The knowledge base contains no relevant documents "
            "for the user's question. Politely explain that the answer is not available in "
            "the provided documents."
        )
    context_blocks = "\n\n".join(
        f"[Source: {c['filename']}, chunk {c['chunk_index']}]\n{c['text']}" for c in chunks
    )
    return (
        "You are a helpful assistant. Answer the user's question using ONLY the context below. "
        "If the answer is not found in the context, say so explicitly. "
        "Always cite sources by filename.\n\n"
        f"Context:\n{context_blocks}"
    )


def _build_messages(system: str, history: list[dict], query: str) -> list[dict]:
    messages = [{"role": "system", "content": system}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": query})
    return messages


async def generate(query: str, chunks: list[dict], history: list[dict]) -> dict:
    system = _build_system_prompt(chunks)
    messages = _build_messages(system, history, query)
    response = await _client.chat.completions.create(
        model=LLM_MODEL, messages=messages, stream=False
    )
    answer = response.choices[0].message.content or ""
    return {"answer": answer}


async def generate_stream(query: str, chunks: list[dict], history: list[dict]):
    system = _build_system_prompt(chunks)
    messages = _build_messages(system, history, query)
    stream = await _client.chat.completions.create(
        model=LLM_MODEL, messages=messages, stream=True
    )
    async for event in stream:
        delta = event.choices[0].delta.content if event.choices else None
        if delta:
            yield delta

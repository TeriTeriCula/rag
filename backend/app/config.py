import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
CHROMA_PATH: str = os.environ.get("CHROMA_PATH", "./chroma_data")
LLM_MODEL: str = os.environ.get("OPENAI_LLM_MODEL", "gpt-4o-mini")
EMBED_MODEL: str = os.environ.get("OPENAI_EMBED_MODEL", "text-embedding-3-small")
COLLECTION_NAME: str = "rag_documents"
TOP_K_DEFAULT: int = 5
CHUNK_SIZE: int = 512
CHUNK_OVERLAP: int = 64
SIMILARITY_THRESHOLD: float = 0.3

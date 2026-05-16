from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE * 4,  # ~4 chars/token approximation
    chunk_overlap=CHUNK_OVERLAP * 4,
    length_function=len,
)


def chunk_pages(pages: list[tuple[str, int]]) -> list[dict]:
    """Return list of {text, page_number, chunk_index}."""
    chunks = []
    idx = 0
    for text, page_num in pages:
        for piece in _splitter.split_text(text):
            chunks.append({"text": piece, "page_number": page_num, "chunk_index": idx})
            idx += 1
    return chunks

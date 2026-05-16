from pathlib import Path
import fitz  # PyMuPDF
import docx


def parse_pdf(data: bytes) -> list[tuple[str, int]]:
    """Return list of (text, page_number) per page."""
    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append((text, i + 1))
    return pages


def parse_txt(data: bytes) -> list[tuple[str, int]]:
    text = data.decode("utf-8", errors="replace").strip()
    return [(text, 1)] if text else []


def parse_docx(data: bytes) -> list[tuple[str, int]]:
    import io
    doc = docx.Document(io.BytesIO(data))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [(text, 1)] if text else []


def parse(filename: str, data: bytes) -> list[tuple[str, int]]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(data)
    if ext == ".txt":
        return parse_txt(data)
    if ext == ".docx":
        return parse_docx(data)
    raise ValueError(f"Unsupported file type: {ext}")

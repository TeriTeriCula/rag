import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

_BOILERPLATE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form"]
_TIMEOUT = 15


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are supported")


def fetch_html(url: str) -> str:
    try:
        response = requests.get(
            url,
            timeout=_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"},
        )
    except requests.exceptions.Timeout:
        raise ValueError(f"Could not reach URL: request timed out after {_TIMEOUT}s")
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Could not reach URL: {exc}")

    if not response.ok:
        raise ValueError(f"URL returned HTTP {response.status_code}")

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        if "application/pdf" in content_type:
            raise ValueError(
                "URL does not point to an HTML page. "
                "To index a PDF, please upload the file directly."
            )
        raise ValueError(
            f"URL returned unsupported content type: {content_type}. Only HTML pages are supported."
        )

    return response.text


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(_BOILERPLATE_TAGS):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def scrape(url: str) -> str:
    validate_url(url)
    html = fetch_html(url)
    text = extract_text(html)
    if not text:
        raise ValueError("No extractable text found at this URL")
    return text

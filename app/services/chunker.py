import re
from typing import Generator
from app.config import settings

try:
    import nltk
    nltk.download("punkt", quiet=True)
    from nltk.tokenize import sent_tokenize
except Exception:
    pass

def fixed_size_chunks(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    """Split text into overlapping fixed-character windows."""
    size = chunk_size or settings.DEFAULT_CHUNK_SIZE
    ov = overlap or settings.DEFAULT_CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - ov
    return [c for c in chunks if c]

def sentence_chunks(text: str, max_sentences: int = 5) -> list[str]:
    """Group sentences into chunks of max_sentences each."""
    sentences = sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        group = " ".join(sentences[i:i + max_sentences])
        if group.strip():
            chunks.append(group.strip())
    return chunks

def paragraph_chunks(text: str) -> list[str]:
    """Split by blank lines (paragraphs)."""
    raw = re.split(r'\n\s*\n', text)
    return [p.strip() for p in raw if p.strip() and len(p.strip()) > 50]

def chunk_text(text: str, strategy: str = "fixed") -> list[str]:
    if strategy == "sentence":
        return sentence_chunks(text)
    elif strategy == "paragraph":
        return paragraph_chunks(text)
    else:
        return fixed_size_chunks(text)

def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract plain text from uploaded file."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "txt":
        return content.decode("utf-8", errors="ignore")
    elif ext == "pdf":
        import io
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext in ("md", "markdown"):
        return content.decode("utf-8", errors="ignore")
    else:
        return content.decode("utf-8", errors="ignore")
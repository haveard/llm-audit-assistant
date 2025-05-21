# Split, chunk, clean

from typing import List, Dict, Tuple, Optional
import re

def clean_content(text: str) -> str:
    # Remove headers/footers (simple heuristic)
    lines = text.splitlines()
    cleaned = [l for l in lines if not re.match(r'^(Page \d+|Confidential|Header|Footer)', l)]
    return "\n".join(cleaned)

def chunk_text(text: str, max_length: int = 1000) -> List[str]:
    # Simple chunking by sentences, then grouping
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) > max_length:
            chunks.append(current.strip())
            current = sent
        else:
            current += " " + sent
    if current:
        chunks.append(current.strip())
    return chunks

def preprocess_document(text: str, metadata: Optional[dict] = None, redaction_patterns: List[str] = []) -> List[Dict]:
    text = clean_content(text)
    if redaction_patterns:
        for pat in redaction_patterns:
            text = re.sub(pat, "[REDACTED]", text)
    chunks = chunk_text(text)
    # Attach metadata to each chunk
    return [{"text": c, "metadata": metadata or {}} for c in chunks]

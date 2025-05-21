# Document preprocessing module: Handles text cleaning, chunking, and preparation for RAG
# 
# This module takes raw document text (after extraction from PDFs, DOCXs, etc.) and
# prepares it for storage in the vector database by:
#   1. Cleaning up headers, footers, and other non-content text
#   2. Splitting content into appropriate sized chunks for embedding
#   3. Optionally applying redactions to sensitive information
#   4. Attaching relevant metadata to each chunk

import re
from typing import List, Dict, Optional


def clean_content(text: str) -> str:
    """
    Remove common document artifacts like headers and footers.
    
    The function uses simple pattern matching to filter out lines that typically appear
    in document headers/footers but don't contribute useful content for RAG systems.
    
    Args:
        text: Raw document text
        
    Returns:
        Cleaned document text with headers/footers removed
    """
    # Remove headers/footers (simple heuristic)
    lines = text.splitlines()
    cleaned = [l for l in lines if not re.match(r'^(Page \d+|Confidential|Header|Footer)', l)]
    return "\n".join(cleaned)


def chunk_text(text: str, max_length: int = 1000) -> List[str]:
    """
    Split document text into semantically meaningful chunks of appropriate size.
    
    This is a critical RAG processing step that breaks documents into chunks that:
    1. Are small enough to fit in the vector embedding context window
    2. Preserve semantic coherence by splitting on sentence boundaries where possible
    3. Keep related content together for better retrieval accuracy
    
    Args:
        text: Cleaned document text
        max_length: Maximum chunk size in characters (default: 1000)
        
    Returns:
        List of text chunks ready for embedding
    """
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
    """
    Main preprocessing pipeline that prepares document text for RAG indexing.
    
    This function orchestrates the entire preprocessing workflow:
    1. Cleans the document text
    2. Applies any redaction patterns to protect sensitive information
    3. Chunks the text into appropriate segments
    4. Attaches metadata to each chunk
    
    The resulting chunks with metadata are ready to be sent to the vector store
    via the RAG pipeline's add_documents method.
    
    Args:
        text: Raw document text
        metadata: Dictionary of document metadata (filename, date, etc.)
        redaction_patterns: List of regex patterns to redact from text
        
    Returns:
        List of dictionaries containing chunks with attached metadata
    """
    text = clean_content(text)
    if redaction_patterns:
        for pat in redaction_patterns:
            text = re.sub(pat, "[REDACTED]", text)
    chunks = chunk_text(text)
    # Attach metadata to each chunk
    return [{"text": c, "metadata": metadata or {}} for c in chunks]

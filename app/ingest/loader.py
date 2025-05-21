# Document Loader Module: Extracts text and metadata from various file formats
#
# This module provides functionality to load and extract text content from different
# document formats (PDF, DOCX, TXT) along with their metadata. It serves as the first
# step in the document ingestion pipeline before preprocessing and chunking.
#
# The extracted text is passed to the preprocessor module which handles cleaning,
# chunking, and preparing the text for embedding and storage in the vector database.

import datetime
import os
from typing import Tuple

from PyPDF2 import PdfReader
from docx import Document


def extract_metadata(file_path: str) -> dict:
    """
    Extract file metadata from the filesystem.
    
    Collects standard file information that's useful for document tracking and filtering:
    - filename: Original file name
    - filetype: File extension (e.g., .pdf, .docx)
    - size: File size in bytes
    - date: Last modification date in ISO format
    
    This metadata is attached to document chunks in the vector store to enable
    filtering and tracking the source of retrieved chunks.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary containing file metadata
    """
    stat = os.stat(file_path)
    return {
        "filename": os.path.basename(file_path),
        "filetype": os.path.splitext(file_path)[1].lower(),
        "size": stat.st_size,
        "date": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def load_pdf(file_path: str) -> Tuple[str, dict]:
    """
    Extract text and metadata from PDF files.
    
    Uses PyPDF2 to extract text content from PDF documents by iterating through
    all pages and combining their text. PDF-specific metadata might be extracted
    in the future (author, title, etc.).
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (extracted text, metadata dictionary)
    """
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    meta = extract_metadata(file_path)
    return text, meta


def load_docx(file_path: str) -> Tuple[str, dict]:
    """
    Extract text and metadata from Word documents.
    
    Uses python-docx to extract text from paragraphs in the Word document.
    More complex Word features like tables and headers/footers could be
    supported in future versions.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Tuple of (extracted text, metadata dictionary)
    """
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    meta = extract_metadata(file_path)
    return text, meta


def load_txt(file_path: str) -> Tuple[str, dict]:
    """
    Extract text and metadata from plain text files.
    
    Handles text files with robust encoding detection. It first attempts UTF-8
    encoding and falls back to Latin-1 if UTF-8 fails. This ensures maximum
    compatibility with various text file encodings.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple of (extracted text, metadata dictionary)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        # Fallback to Latin-1 encoding if UTF-8 fails
        with open(file_path, "r", encoding="latin-1") as f:
            text = f.read()
    meta = extract_metadata(file_path)
    return text, meta


def load_document(file_path: str) -> Tuple[str, dict]:
    """
    Main document loading function that delegates to specific loaders based on file type.
    
    This function serves as the entry point for document loading in the application.
    It determines the file type from the extension and calls the appropriate loader.
    
    Called from the /upload API endpoint after a file is uploaded to MinIO and needs
    to be processed.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Tuple of (extracted text, metadata dictionary)
        
    Raises:
        ValueError: If the file doesn't exist or has an unsupported extension
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext == ".txt":
        return load_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported types: .pdf, .docx, .txt")

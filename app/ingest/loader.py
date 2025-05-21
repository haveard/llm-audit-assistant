# Load PDFs, DOCX, TXT

import datetime
import os
from typing import Tuple

from PyPDF2 import PdfReader
from docx import Document


def extract_metadata(file_path: str) -> dict:
    stat = os.stat(file_path)
    return {
        "filename": os.path.basename(file_path),
        "filetype": os.path.splitext(file_path)[1].lower(),
        "size": stat.st_size,
        "date": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def load_pdf(file_path: str) -> Tuple[str, dict]:
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    meta = extract_metadata(file_path)
    return text, meta


def load_docx(file_path: str) -> Tuple[str, dict]:
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    meta = extract_metadata(file_path)
    return text, meta


def load_txt(file_path: str) -> Tuple[str, dict]:
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

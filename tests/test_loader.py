"""
Test document loading functions
"""
import os
import pytest
import tempfile
from unittest.mock import patch, mock_open

from app.ingest.loader import load_document, load_txt, extract_metadata


def test_extract_metadata():
    """Test metadata extraction function"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        tmp.write(b"test content")
        tmp.flush()
        
        # Test metadata extraction
        meta = extract_metadata(tmp.name)
        
        # Verify metadata fields
        assert meta["filename"] == os.path.basename(tmp.name)
        assert meta["filetype"] == ".txt"
        assert meta["size"] > 0
        assert meta["date"] is not None


def test_load_txt_utf8():
    """Test loading a UTF-8 text file"""
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        content = "Hello, world! 😊"
        tmp.write(content.encode('utf-8'))
        tmp.flush()
        
        # Test loading
        text, meta = load_txt(tmp.name)
        
        # Verify content and metadata
        assert text == content
        assert meta["filetype"] == ".txt"


def test_load_txt_latin1_fallback():
    """Test loading with Latin-1 fallback"""
    # Mock file open to simulate UTF-8 failure
    utf8_error = UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'invalid utf-8')
    
    with patch('builtins.open', side_effect=[utf8_error, mock_open(read_data="fallback content").return_value]):
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            # Test loading with patched open
            text, meta = load_txt(tmp.name)
            
            # Verify fallback content
            assert text == "fallback content"


def test_load_document_unsupported_filetype():
    """Test load_document with unsupported file type"""
    with tempfile.NamedTemporaryFile(suffix='.xyz') as tmp:
        # Should raise ValueError for unsupported file type
        with pytest.raises(ValueError, match=r"Unsupported file type"):
            load_document(tmp.name)


def test_load_document_file_not_found():
    """Test load_document with non-existent file"""
    # Should raise ValueError for file not found
    with pytest.raises(ValueError, match=r"File not found"):
        load_document("/path/to/nonexistent/file.txt")


# Skip actual PDF and DOCX tests if running in CI environment
@pytest.mark.skipif(os.environ.get('CI') == 'true', reason="Skip in CI environment")
def test_load_document_integration():
    """Integration test with real temp files"""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        tmp.write(b"test content for document loader")
        tmp.flush()
        
        # Test the main load_document function
        text, meta = load_document(tmp.name)
        
        # Verify content and metadata
        assert "test content for document loader" in text
        assert meta["filename"] == os.path.basename(tmp.name)
        assert meta["filetype"] == ".txt"

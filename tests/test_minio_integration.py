"""
Integration tests for MinIO functionality
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.api.routes import get_minio_client

# Skip these tests if running in CI without environment variables set up
pytestmark = pytest.mark.skipif(
    os.environ.get("MINIO_ENDPOINT") is None,
    reason="MinIO environment variables not set"
)

class TestMinioIntegration:
    """Integration tests for MinIO functionality"""
    
    def test_singleton_pattern(self):
        """Test that get_minio_client returns the same instance each time"""
        # Reset singleton for testing
        from app.api.routes import _minio_client
        with patch('app.api.routes._minio_client', None):
            # Get client twice
            client1 = get_minio_client()
            client2 = get_minio_client()
            
            # Should be the same instance
            assert client1 is client2
    
    def test_bucket_creation(self):
        """Test bucket creation on initialization"""
        with patch('app.api.routes._minio_client', None):
            # Mock Minio client
            mock_minio = MagicMock(spec=Minio)
            mock_minio.bucket_exists.return_value = False
            
            with patch('app.api.routes.Minio', return_value=mock_minio):
                # Call get_minio_client
                client = get_minio_client()
                
                # Verify bucket_exists and make_bucket were called
                mock_minio.bucket_exists.assert_called_once()
                mock_minio.make_bucket.assert_called_once()
    
    def test_existing_bucket(self):
        """Test behavior with existing bucket"""
        with patch('app.api.routes._minio_client', None):
            # Mock Minio client
            mock_minio = MagicMock(spec=Minio)
            mock_minio.bucket_exists.return_value = True
            
            with patch('app.api.routes.Minio', return_value=mock_minio):
                # Call get_minio_client
                client = get_minio_client()
                
                # Verify bucket_exists was called but make_bucket was not
                mock_minio.bucket_exists.assert_called_once()
                mock_minio.make_bucket.assert_not_called()
    
    def test_minio_error_handling(self):
        """Test MinIO error handling"""
        with patch('app.api.routes._minio_client', None):
            # Mock Minio client that raises S3Error
            mock_minio = MagicMock(spec=Minio)
            mock_minio.bucket_exists.side_effect = S3Error(
                code="AccessDenied", 
                message="Access Denied",
                resource="/", 
                request_id="test", 
                host_id="test",
                response=MagicMock()  # Use a mock object for response
            )
            
            with patch('app.api.routes.Minio', return_value=mock_minio):
                # Call get_minio_client should propagate the error
                with pytest.raises(S3Error):
                    client = get_minio_client()

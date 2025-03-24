import io
import os
import uuid
from typing import Optional, Tuple, BinaryIO, Dict, Any, Union
from werkzeug.datastructures import FileStorage
from minio import Minio
from minio.error import S3Error

class MinioManager:
    """
    Class to manage Minio S3 client instance and operations
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MinioManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Dict[str, Any] = None):
        if self._initialized:
            return
            
        self.config = config or {}
        self.client = None
        self.bucket_daos = self.config.get('bucket_daos', 'bucket-daos')
        self._initialized = True
        
        if config:
            self.initialize()
            
    def initialize(self, config: Dict[str, Any] = None):
        """
        Initialize the Minio client
        
        Args:
            config: Configuration dictionary with endpoint, access_key, secret_key, etc.
                   If None, uses the config from initialization
        """
        if config:
            self.config.update(config)
            
        # Create a Minio client
        self.client = Minio(
            endpoint=self.config.get('endpoint', 'localhost:9000'),
            access_key=self.config.get('access_key', 'minio'),
            secret_key=self.config.get('secret_key', 'minio123'),
            secure=self.config.get('secure', False),
            region=self.config.get('region', 'us-east-1')
        )
        
        # Create buckets if they don't exist
        self.ensure_buckets()
        
        return self.client
    
    def from_flask_config(self, app_config):
        """
        Initialize from Flask app config
        
        Args:
            app_config: Flask app config object
        """
        config = {
            'endpoint': app_config.get('MINIO_ENDPOINT', 'localhost:9000'),
            'access_key': app_config.get('MINIO_ACCESS_KEY', 'minio'),
            'secret_key': app_config.get('MINIO_SECRET_KEY', 'minio123'),
            'secure': app_config.get('MINIO_SECURE', False),
            'region': app_config.get('MINIO_REGION', 'us-east-1'),
            'bucket_daos': app_config.get('MINIO_BUCKET_DAOS', 'bucket-daos')
        }
        self.bucket_daos = config['bucket_daos']
        return self.initialize(config)
    
    def ensure_buckets(self):
        """Create required buckets if they don't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_daos):
                self.client.make_bucket(self.bucket_daos)
                print(f"Bucket '{self.bucket_daos}' created successfully")
            else:
                print(f"Bucket '{self.bucket_daos}' already exists")
        except S3Error as e:
            print(f"Error checking/creating bucket: {e}")
    
    def generate_file_path(self, dao_id: str, file_type: str, filename: Optional[str] = None) -> str:
        """
        Generate a file path for storage in Minio
        
        Args:
            dao_id: The ID of the DAO
            file_type: Type of file (profile_picture, banner_picture, etc.)
            filename: Optional filename (will be used if provided)
            
        Returns:
            A path string in the format /bucket_daos/dao_id/file_type.ext
        """
        if not filename:
            # Generate a random filename if none is provided
            return f"{dao_id}/{file_type}"
        
        # If filename is provided, use its extension
        _, ext = os.path.splitext(filename)
        return f"{dao_id}/{file_type}{ext}"
    
    def upload_file(self, 
                    dao_id: str, 
                    file_type: str, 
                    file_data: FileStorage) -> Tuple[bool, str]:
        """
        Upload a file to the Minio bucket
        
        Args:
            dao_id: The ID of the DAO
            file_type: Type of file (profile_picture, banner_picture, etc.)
            file_data: The file data to upload
            
        Returns:
            Tuple of (success, path or error message)
        """
        try:
            # Generate path
            filename = file_data.filename
            file_path = self.generate_file_path(dao_id, file_type, filename)
            
            # Get content type
            content_type = file_data.content_type or 'application/octet-stream'
            
            # Upload the file
            file_size = file_data.content_length or 0
            file_data.seek(0)  # Ensure we're at the start of the file
            
            self.client.put_object(
                self.bucket_daos,
                file_path,
                file_data,
                file_size,
                content_type=content_type
            )
            
            return True, file_path
        except Exception as e:
            print(f"Error uploading file to Minio: {e}")
            return False, str(e)
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Delete a file from the Minio bucket
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Delete the object
            self.client.remove_object(self.bucket_daos, file_path)
            
            return True, "File deleted successfully"
        except Exception as e:
            print(f"Error deleting file from Minio: {e}")
            return False, str(e)
    
    def get_file_url(self, file_path: str, expires: int = 3600) -> Tuple[bool, str]:
        """
        Get a presigned URL for a file in the Minio bucket
        
        Args:
            file_path: Path to the file
            expires: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Tuple of (success, URL or error message)
        """
        try:
            # Generate presigned URL
            url = self.client.presigned_get_object(
                self.bucket_daos,
                file_path,
                expires=expires
            )
            
            return True, url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return False, str(e)


# Create a singleton instance
minio_manager = MinioManager()


# For backward compatibility with the old MinioHelper interface
class MinioHelper:
    """
    Helper class for Minio S3 operations (for backwards compatibility)
    Using the singleton MinioManager instance
    """
    
    @staticmethod
    def get_minio_client():
        """Get the Minio client from the global manager"""
        return minio_manager.client
    
    @staticmethod
    def generate_file_path(dao_id: str, file_type: str, filename: Optional[str] = None) -> str:
        """Delegate to MinioManager"""
        return minio_manager.generate_file_path(dao_id, file_type, filename)
    
    @classmethod
    def upload_file(cls, dao_id: str, file_type: str, file_data: FileStorage) -> Tuple[bool, str]:
        """Delegate to MinioManager"""
        return minio_manager.upload_file(dao_id, file_type, file_data)
    
    @classmethod
    def delete_file(cls, file_path: str) -> Tuple[bool, str]:
        """Delegate to MinioManager"""
        return minio_manager.delete_file(file_path)
    
    @classmethod
    def get_file_url(cls, file_path: str, expires: int = 3600) -> Tuple[bool, str]:
        """Delegate to MinioManager"""
        return minio_manager.get_file_url(file_path, expires) 
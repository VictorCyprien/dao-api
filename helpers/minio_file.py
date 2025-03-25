import io
import os
import datetime
import base64
from typing import Optional, Tuple, BinaryIO, Dict, Any, Union

from minio import Minio
from minio.error import S3Error

from api.config import config

from helpers.redis_file import RedisToken


redis_client = RedisToken()



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
    
    def __init__(self):
        if self._initialized:
            return
        # Create a Minio client
        self.client = Minio(
            endpoint=config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=config.MINIO_SECURE,
            region=config.MINIO_REGION,
        )
        
        # Create buckets if they don't exist
        self.bucket_daos = config.MINIO_BUCKET_DAOS
        self.ensure_buckets()
        self._initialized = True
        
    
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
    
    
    def base64_to_binary_io(self, base64_string: str) -> Tuple[BinaryIO, int]:
        """
        Convert a base64 string to a BinaryIO object
        
        Args:
            base64_string: The base64 encoded string
            
        Returns:
            Tuple of (BinaryIO object, content length)
        """
        # If the base64 string includes the data URL prefix, remove it
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
            
        # Decode the base64 string to bytes
        image_data = base64.b64decode(base64_string)
        
        # Create a BytesIO object from the decoded data
        binary_io = io.BytesIO(image_data)
        
        # Get the content length
        content_length = len(image_data)
        
        return binary_io, content_length
    
    
    def upload_file(self, dao_id: str, file_type: str, file_data: Dict[str, Any]) -> str:
        """
        Upload a file to the Minio bucket
        
        Args:
            dao_id: The ID of the DAO
            file_type: Type of file (profile_picture, banner_picture, etc.)
            file_data: A dictionary with file data
            
        Returns:
            The path of the uploaded file
        """
        try:
            # Generate path
            filename = file_data["filename"]
            file_path = self.generate_file_path(dao_id, file_type, filename)
            
            # Get content type
            content_type = file_data["content_type"] or 'application/octet-stream'

            # Convert base64 to binary io
            binary_io, content_length = self.base64_to_binary_io(file_data["stream"])
            
            self.client.put_object(
                bucket_name="daos",
                object_name=file_path,
                data=binary_io,
                length=content_length,
                content_type=content_type
            )
            
            return file_path
        except Exception as e:
            print(f"Error uploading file to Minio: {e}")
            return None
    
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
                expires=datetime.timedelta(seconds=expires)
            )
            
            return True, url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return False, str(e)

    def get_cached_file_url(self, file_path: str, expires: int = 3600) -> Tuple[bool, str]:
        """
        Get a presigned URL for a file in the Minio bucket with Redis caching
        
        Args:
            file_path: Path to the file
            expires: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Tuple of (success, URL or error message)
        """
        try:
            # Create a unique cache key for this file path
            cache_key = f"minio:url:{file_path}"
            
            # Try to get the URL from Redis cache
            cached_url = redis_client.get_token(cache_key)
            
            if cached_url:
                # Return the cached URL if it exists
                return True, cached_url
            
            # If no cached URL exists, generate a new presigned URL
            success, url = self.get_file_url(file_path, expires)
            
            if success:
                # Cache the URL in Redis with the same expiration time
                redis_client.set_token(cache_key, url, expires)
            
            return success, url
        except Exception as e:
            print(f"Error in get_cached_file_url: {e}")
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
    def upload_file(cls, dao_id: str, file_type: str, file_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Delegate to MinioManager
        Supports data dictionaries
        """
        return minio_manager.upload_file(dao_id, file_type, file_data)
    
    @classmethod
    def delete_file(cls, file_path: str) -> Tuple[bool, str]:
        """Delegate to MinioManager"""
        return minio_manager.delete_file(file_path)
    
    @classmethod
    def get_file_url(cls, file_path: str, expires: int = 3600) -> Tuple[bool, str]:
        """Delegate to MinioManager"""
        return minio_manager.get_file_url(file_path, expires) 
        
    @classmethod
    def get_cached_file_url(cls, file_path: str, expires: int = 3600) -> str:
        """
        Get a presigned URL for a file with Redis caching
        
        Args:
            file_path: Path to the file
            expires: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            URL or error message
        """
        return minio_manager.get_cached_file_url(file_path, expires)[1]
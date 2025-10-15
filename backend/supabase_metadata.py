"""
Supabase Database Client and Browser Metadata Insertion Module.

This module provides functionality to store browser metadata from API requests
into the Supabase database. It handles connection management, data validation,
and insertion operations for the browser_meta table.
"""

import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import json

try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
except ImportError as e:
    raise ImportError(
        "supabase package is required. Install with: pip install supabase"
    ) from e

from .config import SupabaseConfig, DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)


class SupabaseMetadataClient:
    """
    Supabase client for storing browser metadata.
    
    Provides connection management and data insertion for browser metadata
    received via API requests.
    """
    
    def __init__(self, use_service_role: bool = True):
        """
        Initialize the Supabase metadata client.
        
        Args:
            use_service_role: Whether to use service role key (admin) or anon key
        """
        self.use_service_role = use_service_role
        self._client: Optional[Client] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Connect to Supabase database.
        
        Returns:
            bool: True if connection successful
        """
        try:
            url = SupabaseConfig.get_url()
            
            if self.use_service_role:
                key = SupabaseConfig.get_service_role_key()
                logger.info("Connecting to Supabase with service role")
            else:
                key = SupabaseConfig.get_anon_key()
                logger.info("Connecting to Supabase with anon key")
            
            # Create client with options
            options = ClientOptions(
                auto_refresh_token=True,
                persist_session=True
            )
            
            self._client = create_client(url, key, options)
            
            # Test connection
            if self.test_connection():
                self._connected = True
                logger.info("Successfully connected to Supabase")
                return True
            else:
                logger.error("Connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            self._connected = False
            return False
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._client is not None
    
    def test_connection(self) -> bool:
        """
        Test database connection by performing a simple query.
        
        Returns:
            bool: True if connection test successful
        """
        try:
            if not self._client:
                logger.error("Client not initialized")
                return False
            
            # Test with a simple query to browser_meta table
            response = (
                self._client
                .table(DatabaseConfig.BROWSER_META_TABLE)
                .select("id")
                .limit(1)
                .execute()
            )
            
            logger.info("Database connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from Supabase."""
        if self._client:
            self._client = None
            self._connected = False
            logger.info("Disconnected from Supabase")
    
    def _clean_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean metadata for database insertion.
        
        Args:
            data: Raw metadata dictionary
            
        Returns:
            Cleaned metadata dictionary
        """
        cleaned = {}
        
        for key, value in data.items():
            # Convert datetime objects to ISO strings
            if isinstance(value, datetime):
                cleaned[key] = value.isoformat()
            # Convert None to null for JSON
            elif value is None:
                cleaned[key] = None
            # Ensure JSON serializable
            else:
                try:
                    json.dumps(value)
                    cleaned[key] = value
                except (TypeError, ValueError):
                    # Convert non-serializable objects to string
                    cleaned[key] = str(value)
        
        return cleaned
    
    def validate_request_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate incoming request data structure.
        
        Args:
            data: Request data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        for field in DatabaseConfig.REQUIRED_FIELDS:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate model field
        model = data.get("model", "").lower()
        if model not in DatabaseConfig.SUPPORTED_MODELS:
            return False, f"Unsupported model: {model}. Supported: {DatabaseConfig.SUPPORTED_MODELS}"
        
        # Validate timestamp format
        timestamp = data.get("timestamp")
        if timestamp:
            try:
                # Try to parse timestamp
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False, "Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        # Validate metadata_data is a dictionary
        metadata_data = data.get("metadata_data")
        if not isinstance(metadata_data, dict):
            return False, "metadata_data must be a dictionary object"
        
        return True, ""
    
    def insert_browser_metadata(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert browser metadata into the database.
        
        Args:
            request_data: Dictionary containing model, timestamp, and metadata_data
            
        Returns:
            Database response or None if failed
        """
        try:
            if not self.is_connected:
                logger.error("Not connected to database")
                return None
            
            # Validate request data
            is_valid, error_msg = self.validate_request_data(request_data)
            if not is_valid:
                logger.error(f"Invalid request data: {error_msg}")
                return None
            
            # Clean metadata for JSON storage
            cleaned_metadata = self._clean_metadata(request_data["metadata_data"])
            
            # Prepare record for insertion
            record = {
                "model": request_data["model"].lower(),
                "timestamp": request_data["timestamp"],
                "meta_data": cleaned_metadata  # JSONB column
            }
            
            # Insert into database
            response = (
                self.client
                .table(DatabaseConfig.BROWSER_META_TABLE)
                .insert(record)
                .execute()
            )
            
            logger.info(f"Successfully inserted browser metadata for model: {record['model']}")
            logger.debug(f"Database response: {response.data}")
            
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to insert browser metadata: {str(e)}")
            return None
    
    def get_recent_metadata(self, limit: int = 10, model: Optional[str] = None) -> Optional[list]:
        """
        Retrieve recent metadata entries.
        
        Args:
            limit: Maximum number of records to return
            model: Filter by model type (optional)
            
        Returns:
            List of metadata records or None if failed
        """
        try:
            if not self.is_connected:
                logger.error("Not connected to database")
                return None
            
            query = (
                self.client
                .table(DatabaseConfig.BROWSER_META_TABLE)
                .select("id, created_at, model, timestamp, meta_data")
                .order("created_at", desc=True)
                .limit(limit)
            )
            
            if model:
                query = query.eq("model", model.lower())
            
            response = query.execute()
            
            logger.info(f"Retrieved {len(response.data)} metadata records")
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve metadata: {str(e)}")
            return None


# Convenience functions
def create_metadata_client(use_service_role: bool = True) -> SupabaseMetadataClient:
    """
    Create and connect a metadata client instance.
    
    Args:
        use_service_role: Whether to use service role key for admin operations
        
    Returns:
        Connected SupabaseMetadataClient instance
    """
    client = SupabaseMetadataClient(use_service_role=use_service_role)
    if client.connect():
        return client
    else:
        raise RuntimeError("Failed to connect to Supabase database")


def insert_metadata(request_data: Dict[str, Any], use_service_role: bool = True) -> bool:
    """
    Quick function to insert metadata with automatic connection management.
    
    Args:
        request_data: Dictionary with model, timestamp, and metadata_data
        use_service_role: Whether to use service role key
        
    Returns:
        True if insertion successful, False otherwise
    """
    try:
        with create_metadata_client(use_service_role) as client:
            result = client.insert_browser_metadata(request_data)
            return result is not None
    except Exception as e:
        logger.error(f"Failed to insert metadata: {str(e)}")
        return False


# Context manager support
class SupabaseMetadataClient(SupabaseMetadataClient):
    def __enter__(self):
        """Context manager entry."""
        if not self.connect():
            raise RuntimeError("Failed to connect to database")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
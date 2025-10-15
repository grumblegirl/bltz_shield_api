"""
Configuration settings for Supabase client and database operations.
BLTZ Shield API - Browser Metadata Storage
"""
import os
from typing import Optional


class SupabaseConfig:
    """Configuration class for Supabase connection parameters."""
    
    # Supabase connection details (use environment variables in production)
    SUPABASE_URL: str = "https://bypyjoeijaflpxpernam.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cHlqb2VpamFmbHB4cGVybmFtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE3MzUwODksImV4cCI6MjA2NzMxMTA4OX0.fJiLcKNOpCXBk5HN8BmgTdJvIYI2lQp3sqT9b67HKYo"
    SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cHlqb2VpamFmbHB4cGVybmFtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTczNTA4OSwiZXhwIjoyMDY3MzExMDg5fQ.rWCrSEeWIgZSkOsZlCw6WouRnsDKHHdxsPV97UZ7z64"
    
    @classmethod
    def get_url(cls) -> str:
        """Get Supabase URL from environment or default."""
        return os.getenv("SUPABASE_URL", cls.SUPABASE_URL)
    
    @classmethod
    def get_anon_key(cls) -> str:
        """Get Supabase anonymous key from environment or default."""
        return os.getenv("SUPABASE_ANON_KEY", cls.SUPABASE_ANON_KEY)
    
    @classmethod
    def get_service_role_key(cls) -> str:
        """Get Supabase service role key from environment or default."""
        return os.getenv("SERVICE_ROLE_KEY", cls.SERVICE_ROLE_KEY)


class DatabaseConfig:
    """Configuration for database operations."""
    
    # Table name for browser metadata
    BROWSER_META_TABLE = "browser_meta"
    
    # Required fields for metadata requests
    REQUIRED_FIELDS = ["model", "timestamp", "metadata_data"]
    
    # Supported model types
    SUPPORTED_MODELS = ["gpt", "claude", "gemini", "llama"]
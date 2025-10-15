#!/usr/bin/env python3
"""
BLTZ Shield API Business Logic
Contains all the core business logic and endpoint handlers
"""

import json
import logging
from datetime import datetime
from typing import Dict, Tuple, Any, Optional

# Import Supabase metadata functionality
try:
    from .supabase_metadata import create_metadata_client, insert_metadata, insert_conversation
    from .config import DatabaseConfig
    SUPABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Supabase functionality not available: {e}")
    SUPABASE_AVAILABLE = False

# Configuration
HARDCODED_API_KEY = 'bltz_shield_2025_secure_key'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bltz_shield_api')


class APILogic:
    """Business logic for BLTZ Shield API endpoints"""
    
    def __init__(self):
        self.api_key = HARDCODED_API_KEY
    
    def validate_api_key(self, headers: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate X-API-Key header and return the API key"""
        # Try different header key formats (WSGI, HTTP, direct)
        api_key = (headers.get('X-API-Key') or 
                   headers.get('x-api-key') or 
                   headers.get('X-Api-Key') or
                   headers.get('HTTP_X_API_KEY'))
        
        if not api_key:
            logger.warning("Missing X-API-Key header in request")
            logger.warning(f"Available headers: {list(headers.keys())}")
            return False, None
            
        if api_key != self.api_key:
            logger.warning(f"Invalid API key provided: {api_key}")
            return False, None
            
        logger.info("API key validation successful")
        return True, api_key
    
    def log_request_details(self, method: str, path: str, headers: Dict[str, Any], body: str = None):
        """Log request details for debugging"""
        logger.info(f"Request method: {method}")
        logger.info(f"Request path: {path}")
        logger.info(f"Request headers: {headers}")
        
        if body:
            logger.info(f"Request body: {body}")
    
    def parse_request_body(self, body: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Parse request body and return (json_data, error_response)
        Returns (data, None) on success, (None, error_response) on failure
        """
        if not body:
            return {}, None
            
        try:
            json_data = json.loads(body)
            return json_data, None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return None, {
                "result": "error",
                "message": "Invalid JSON format"
            }
    
    def handle_metadata_endpoint(self, json_data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Handle requests to /metadata endpoint with new schema"""
        logger.info(f"Processing /metadata endpoint with full request body: {json.dumps(json_data)}")
        required_fields = ["provider", "timestamp", "meta_data", "user", "license"]
        missing_fields = [field for field in required_fields if field not in json_data]
        if missing_fields:
            return {
                "result": "error",
                "message": f"Missing required fields: {missing_fields}",
                "timestamp": datetime.now().isoformat()
            }
        # Validate meta_data is a dictionary
        meta_data = json_data.get("meta_data")
        if not isinstance(meta_data, dict):
            return {
                "result": "error",
                "message": "meta_data must be a dictionary object",
                "timestamp": datetime.now().isoformat()
            }
        logger.info(f"Meta_data contains {len(meta_data)} fields for provider: {json_data.get('provider')}")
        # Store in Supabase database if available
        database_stored = False
        database_error = None
        organization_id = None
        if SUPABASE_AVAILABLE:
            try:
                database_stored = insert_metadata(json_data, api_key, use_service_role=True)
                if database_stored:
                    logger.info("Successfully stored metadata in Supabase database")
                else:
                    logger.error("Failed to store metadata in database")
                    database_error = "Database insertion failed"
            except Exception as e:
                logger.error(f"Database insertion error: {str(e)}")
                database_error = f"Database error: {str(e)}"
        # Prepare response
        response_data = {
            "result": "success",
            "message": "Metadata request processed successfully",
            "timestamp": datetime.now().isoformat(),
            "metadata_summary": {
                "provider": json_data.get("provider"),
                "timestamp": json_data.get("timestamp"),
                "fields_count": len(meta_data),
                "user": json_data.get("user"),
                "license": json_data.get("license"),
                "database_stored": database_stored
            }
        }
        if database_error:
            response_data["database_warning"] = database_error
        return response_data
    
    def handle_conversation_endpoint(self, json_data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Handle requests to /conversation endpoint"""
        logger.info(f"Processing /conversation endpoint with full request body: {json.dumps(json_data)}")
        required_fields = ["provider", "timestamp", "meta_data", "model", "user", "input"]
        missing_fields = [field for field in required_fields if field not in json_data]
        if missing_fields:
            return {
                "result": "error",
                "message": f"Missing required fields: {missing_fields}",
                "timestamp": datetime.now().isoformat()
            }
        # Validate meta_data is a dictionary
        meta_data = json_data.get("meta_data")
        if not isinstance(meta_data, dict):
            return {
                "result": "error",
                "message": "meta_data must be a dictionary object",
                "timestamp": datetime.now().isoformat()
            }
        logger.info(f"Conversation data - Provider: {json_data.get('provider')}, Model: {json_data.get('model')}")
        
        # Store in Supabase database if available
        database_stored = False
        database_error = None
        if SUPABASE_AVAILABLE:
            try:
                database_stored = insert_conversation(json_data, api_key, use_service_role=True)
                if database_stored:
                    logger.info("Successfully stored conversation data in Supabase database")
                else:
                    logger.error("Failed to store conversation data in database")
                    database_error = "Database insertion failed"
            except Exception as e:
                logger.error(f"Database insertion error: {str(e)}")
                database_error = f"Database error: {str(e)}"
        else:
            database_error = "Supabase not available"
        
        # Prepare response
        response_data = {
            "result": "success", 
            "message": "Conversation request processed successfully",
            "timestamp": datetime.now().isoformat(),
            "conversation_summary": {
                "provider": json_data.get("provider"),
                "model": json_data.get("model"),
                "timestamp": json_data.get("timestamp"),
                "user": json_data.get("user"),
                "input_length": len(json_data.get("input", "")),
                "meta_fields_count": len(meta_data),
                "database_stored": database_stored
            }
        }
        if database_error:
            response_data["database_warning"] = database_error
        return response_data
    
    def create_error_response(self, status_code: int, message: str) -> Tuple[int, Dict[str, Any]]:
        """Create standardized error response"""
        return status_code, {
            "result": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_success_response(self, data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Create standardized success response"""
        return 200, data
    
    def process_request(self, method: str, path: str, headers: Dict[str, Any], body: str = None) -> Tuple[int, Dict[str, Any]]:
        """
        Main request processing logic
        Returns (status_code, response_data)
        """
        try:
            # Log request details
            self.log_request_details(method, path, headers, body)
            
            # Only accept POST requests
            if method != 'POST':
                return self.create_error_response(405, f"Method {method} not allowed")
            
            # Validate API key
            is_valid, api_key = self.validate_api_key(headers)
            if not is_valid:
                return self.create_error_response(401, "Invalid or missing API key")
            
            # Parse request body
            json_data, parse_error = self.parse_request_body(body)
            if parse_error:
                return 400, parse_error
            
            # Route to appropriate endpoint
            if path == '/metadata' or path == '/api/metadata':
                response_data = self.handle_metadata_endpoint(json_data, api_key)
                return self.create_success_response(response_data)
            elif path == '/conversation' or path == '/api/conversation':
                response_data = self.handle_conversation_endpoint(json_data, api_key)
                return self.create_success_response(response_data)
            else:
                return self.create_error_response(404, f"Endpoint not found: {path}")
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return self.create_error_response(500, "Internal server error")


# Global instance for use in serverless functions
api_logic = APILogic()


def handle_request(method: str, path: str, headers: Dict[str, Any], body: str = None) -> Tuple[int, Dict[str, Any]]:
    """
    Main entry point for handling API requests
    Returns (status_code, response_data)
    """
    return api_logic.process_request(method, path, headers, body)
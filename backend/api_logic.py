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
        
        # Log origin/referrer information
        origin = headers.get('Origin') or headers.get('origin') or headers.get('ORIGIN')
        referrer = headers.get('Referer') or headers.get('referer') or headers.get('REFERER')
        user_agent = headers.get('User-Agent') or headers.get('user-agent') or headers.get('USER-AGENT')
        client_ip = headers.get('REAL_CLIENT_IP') or headers.get('CLIENT_IP') or headers.get('X-Forwarded-For', 'Unknown')
        server_name = headers.get('SERVER_NAME', 'Unknown')
        
        logger.info(f"Request origin: {origin or 'Not provided'}")
        logger.info(f"Request referrer: {referrer or 'Not provided'}")
        logger.info(f"Request user-agent: {user_agent or 'Not provided'}")
        logger.info(f"Client IP: {client_ip}")
        logger.info(f"Server: {server_name}")
        
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
    
    def handle_metadata_endpoint(self, json_data: Dict[str, Any], api_key: str, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle requests to /metadata endpoint with new schema"""
        origin = headers.get('Origin', 'Unknown') if headers else 'Unknown'
        client_ip = headers.get('REAL_CLIENT_IP', 'Unknown') if headers else 'Unknown'
        logger.info(f"Processing /metadata endpoint from origin: {origin}, IP: {client_ip}")
        logger.info(f"Metadata request body: {json.dumps(json_data)}")
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
        
        # Append API client origin information to meta_data for database storage
        # This captures where the API request itself came from (e.g., Chrome extension origin)
        if headers:
            logger.info(f"Available headers for origin extraction: {list(headers.keys())}")
            json_data["meta_data"]["_api_client_origin"] = headers.get('Origin', 'Not provided')
            json_data["meta_data"]["_api_client_referrer"] = headers.get('Referer', 'Not provided') 
            json_data["meta_data"]["_api_client_user_agent"] = headers.get('User-Agent', 'Not provided')
            json_data["meta_data"]["_api_client_ip"] = headers.get('REAL_CLIENT_IP') or headers.get('CLIENT_IP', 'Unknown')
            logger.info(f"Captured origin info: Origin={headers.get('Origin')}, Referer={headers.get('Referer')}, IP={headers.get('REAL_CLIENT_IP') or headers.get('CLIENT_IP')}")
        else:
            logger.warning("No headers provided to metadata endpoint")
        
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
            "result": "success"
        }
        if database_error:
            response_data["database_warning"] = database_error
        return response_data
    
    def handle_conversation_endpoint(self, json_data: Dict[str, Any], api_key: str, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle requests to /conversation endpoint"""
        origin = headers.get('Origin', 'Unknown') if headers else 'Unknown'
        client_ip = headers.get('REAL_CLIENT_IP', 'Unknown') if headers else 'Unknown'
        logger.info(f"Processing /conversation endpoint from origin: {origin}, IP: {client_ip}")
        logger.info(f"Conversation request body: {json.dumps(json_data)}")
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
        
        # Append API client origin information to meta_data for database storage
        # This captures where the API request itself came from (e.g., Chrome extension origin)
        if headers:
            logger.info(f"Available headers for origin extraction: {list(headers.keys())}")
            json_data["meta_data"]["_api_client_origin"] = headers.get('Origin', 'Not provided')
            json_data["meta_data"]["_api_client_referrer"] = headers.get('Referer', 'Not provided') 
            json_data["meta_data"]["_api_client_user_agent"] = headers.get('User-Agent', 'Not provided')
            json_data["meta_data"]["_api_client_ip"] = headers.get('REAL_CLIENT_IP') or headers.get('CLIENT_IP', 'Unknown')
            logger.info(f"Captured origin info: Origin={headers.get('Origin')}, Referer={headers.get('Referer')}, IP={headers.get('REAL_CLIENT_IP') or headers.get('CLIENT_IP')}")
        else:
            logger.warning("No headers provided to conversation endpoint")
        
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
            "result": "success"
        }
        if database_error:
            response_data["database_warning"] = database_error
        return response_data
    
    def handle_armor_wheel_catch_mouse_endpoint(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests to /armor_wheel_catch_mouse endpoint"""
        logger.info(f"Processing /armor_wheel_catch_mouse endpoint")
        
        # Get xid from headers
        xid = headers.get('xid') or headers.get('Xid') or headers.get('XID')
        if not xid:
            return {
                "result": "error",
                "message": "Missing xid header",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"Looking up extension_id: {xid}")
        
        # Query database for matching extension_id
        if not SUPABASE_AVAILABLE:
            return {
                "result": "error", 
                "message": "Database not available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Create metadata client for database operations
            client = create_metadata_client(use_service_role=True)
            if not client or not client.connect():
                return {
                    "result": "error",
                    "message": "Failed to connect to database", 
                    "timestamp": datetime.now().isoformat()
                }
            
            # Query browser_extension_id table for matching extension_id
            extension_result = client._client.table('browser_extension_id').select('organization_id').eq('extension_id', xid).execute()
            
            if not extension_result.data:
                logger.warning(f"No matching extension_id found for: {xid}")
                return {
                    "result": "error",
                    "message": "Extension ID not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            organization_id = extension_result.data[0]['organization_id']
            logger.info(f"Found organization_id: {organization_id} for extension_id: {xid}")
            
            # Query api_key table for the organization
            api_key_result = client._client.table('api_key').select('api_key').eq('organization_id', organization_id).execute()
            
            if not api_key_result.data:
                logger.warning(f"No API key found for organization_id: {organization_id}")
                return {
                    "result": "error", 
                    "message": "API key not found for organization",
                    "timestamp": datetime.now().isoformat()
                }
            
            api_key_value = api_key_result.data[0]['api_key']
            logger.info(f"Successfully retrieved API key for organization_id: {organization_id}")
            
            return {
                "x": api_key_value
            }
            
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            return {
                "result": "error",
                "message": f"Database error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
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

            # Special handling for armor_wheel_catch_mouse endpoint (no API key required)
            if path == '/armor_wheel_catch_mouse' or path == '/api/armor_wheel_catch_mouse':
                response_data = self.handle_armor_wheel_catch_mouse_endpoint(headers)
                return self.create_success_response(response_data)

            # Validate API key for other endpoints
            is_valid, api_key = self.validate_api_key(headers)
            if not is_valid:
                return self.create_error_response(401, "Invalid or missing API key")

            # Parse request body
            json_data, parse_error = self.parse_request_body(body)
            if parse_error:
                return 400, parse_error            # Route to appropriate endpoint
            if path == '/metadata' or path == '/api/metadata':
                response_data = self.handle_metadata_endpoint(json_data, api_key, headers)
                return self.create_success_response(response_data)
            elif path == '/conversation' or path == '/api/conversation':
                response_data = self.handle_conversation_endpoint(json_data, api_key, headers)
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
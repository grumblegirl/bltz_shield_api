from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add current directory to Python path to import backend modules  
sys.path.insert(0, os.path.dirname(__file__))

try:
    from backend.api_logic import handle_request
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def _send_response(self, status_code: int, data: dict):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
        
        json_response = json.dumps(data)
        self.wfile.write(json_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._send_response(200, {})
    
    def do_GET(self):
        """Handle GET requests"""
        api_info = {
            "name": "BLTZ Shield API",
            "version": "1.0.0",
            "status": "running",
            "backend_available": BACKEND_AVAILABLE,
            "endpoints": [
                {
                    "path": "/api/metadata",
                    "method": "POST",
                    "description": "Process metadata requests"
                }
            ],
            "authentication": "X-API-Key header required",
            "api_key": "bltz_shield_2025_secure_key"
        }
        self._send_response(200, api_info)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if not BACKEND_AVAILABLE:
                self._send_response(500, {
                    "result": "error", 
                    "message": "Backend logic not available"
                })
                return
                
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
            
            # Convert headers to dict
            headers_dict = dict(self.headers)
            
            # Process request using backend business logic
            status_code, response_data = handle_request('POST', '/metadata', headers_dict, body)
            
            # Send response
            self._send_response(status_code, response_data)
            
        except Exception as e:
            error_response = {
                "result": "error",
                "message": f"Server error: {str(e)}"
            }
            self._send_response(500, error_response)
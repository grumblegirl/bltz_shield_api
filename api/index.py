"""
BLTZ Shield API - Vercel HTTP Handler
Main entry point for Vercel deployment using BaseHTTPRequestHandler pattern
"""

import json
import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add parent directory to path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.api_logic import handle_request


class handler(BaseHTTPRequestHandler):
    """Main API handler for all endpoints"""
    
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
            "endpoints": [
                {
                    "path": "/metadata",
                    "method": "POST",
                    "description": "Process metadata requests"
                }
            ],
            "authentication": "X-API-Key header required",
            "api_key": "bltz_shield_2025_secure_key"
        }
        self._send_response(200, api_info)
    
    def do_POST(self):
        """Handle POST requests - route to backend logic"""
        try:
            # Parse the URL - handle both /metadata and /api/* paths
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # Normalize paths for backend processing
            if path.startswith('/api/'):
                # Strip /api prefix for backend logic
                path = path[4:]
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
            
            # Convert headers to dict
            headers_dict = dict(self.headers)
            
            # Process request using backend business logic
            status_code, response_data = handle_request('POST', path, headers_dict, body)
            
            # Send response
            self._send_response(status_code, response_data)
            
        except Exception as e:
            # Handle any unexpected errors
            error_response = {
                "result": "error",
                "message": "Internal server error"
            }
            self._send_response(500, error_response)

# For local development
if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8080), handler)
    print("🛡️  BLTZ Shield API Server")
    print("=" * 40)
    print("Server running on http://localhost:8080")
    print("Available endpoints:")
    print("  • GET  /          - API info")
    print("  • POST /metadata  - Metadata endpoint")
    print("🔑 API Key: bltz_shield_2025_secure_key")
    print("Press Ctrl+C to stop...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
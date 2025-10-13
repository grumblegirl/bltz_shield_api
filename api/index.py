"""
BLTZ Shield API - Vercel WSGI Application
Main entry point for Vercel deployment using WSGI pattern
"""

import json
import sys
import os

# Add parent directory to path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.api_logic import handle_request


def add_cors_headers(headers):
    """Add CORS headers for cross-origin requests"""
    cors_headers = [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type, X-API-Key'),
        ('Access-Control-Max-Age', '86400'),
    ]
    return headers + cors_headers


def application(environ, start_response):
    """WSGI application for Vercel"""
    try:
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        
        # Handle CORS preflight - return 200 OK with no body
        if method == 'OPTIONS':
            status = '200 OK'
            headers = add_cors_headers([('Content-Length', '0')])
            start_response(status, headers)
            return [b'']
        
        # Handle GET requests
        if method == 'GET':
            if path == '/' or path == '/api' or path == '':
                response_data = json.dumps({
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
                })
                status = '200 OK'
                headers = add_cors_headers([
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(response_data))),
                ])
                start_response(status, headers)
                return [response_data.encode()]
            else:
                # 404 for other GET requests
                error_response = {"error": "Not Found"}
                response_data = json.dumps(error_response)
                status = '404 Not Found'
                headers = add_cors_headers([
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(response_data))),
                ])
                start_response(status, headers)
                return [response_data.encode()]
        
        # Handle POST requests
        elif method == 'POST':
            try:
                # Read request body
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                if content_length > 0:
                    post_data = environ['wsgi.input'].read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                else:
                    data = {}
                
                # Convert environ headers to dict format expected by backend
                headers_dict = {}
                for key, value in environ.items():
                    if key.startswith('HTTP_'):
                        # Convert HTTP_X_API_KEY to X-API-Key
                        header_name = key[5:].replace('_', '-').title()
                        headers_dict[header_name] = value
                
                # Route to appropriate handler based on path
                if path in ['/metadata', '/api/metadata']:
                    # Use business logic from backend
                    status_code, response_data = handle_request('POST', '/metadata', headers_dict, json.dumps(data) if data else "")
                else:
                    status_code = 404
                    response_data = {"result": "error", "message": f"Endpoint not found: {path}"}
                
                # Send successful response
                response_json = json.dumps(response_data)
                status = f'{status_code} {"OK" if status_code == 200 else "Error"}'
                headers = add_cors_headers([
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(response_json))),
                ])
                start_response(status, headers)
                return [response_json.encode()]
                
            except json.JSONDecodeError:
                # Handle JSON parsing errors
                error_response = {"result": "error", "message": "Invalid JSON"}
                response_data = json.dumps(error_response)
                status = '400 Bad Request'
                headers = add_cors_headers([
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(response_data))),
                ])
                start_response(status, headers)
                return [response_data.encode()]
                
            except Exception as e:
                # Handle other errors
                error_response = {"result": "error", "message": str(e)}
                response_data = json.dumps(error_response)
                status = '500 Internal Server Error'
                headers = add_cors_headers([
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(response_data))),
                ])
                start_response(status, headers)
                return [response_data.encode()]
        
        # Handle unsupported methods
        else:
            error_response = {"result": "error", "message": "Method Not Allowed"}
            response_data = json.dumps(error_response)
            status = '405 Method Not Allowed'
            headers = add_cors_headers([
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_data))),
            ])
            start_response(status, headers)
            return [response_data.encode()]
    
    except Exception as e:
        # Catch any unexpected errors at the top level
        error_response = {"result": "error", "message": f"Application error: {str(e)}"}
        response_data = json.dumps(error_response)
        status = '500 Internal Server Error'
        headers = add_cors_headers([
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_data))),
        ])
        start_response(status, headers)
        return [response_data.encode()]


# Export the WSGI application as 'app' for Vercel
app = application

# For local development
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 8080, application)
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
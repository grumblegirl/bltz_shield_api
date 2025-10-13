from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "name": "BLTZ Shield API", 
            "status": "working",
            "message": "Vercel Python execution confirmed!",
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response).encode())
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simple test without complex imports
        response = {"result": "success", "message": "POST working", "test": "confirmed"}
        self.wfile.write(json.dumps(response).encode())
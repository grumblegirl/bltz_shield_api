# BLTZ Shield API

A simple HTTP API server built with Python's built-in `http.server` module.

## Features

- HTTP API server with JSON POST endpoint support
- API key authentication via `X-API-Key` header
- Request/response logging
- `/metadata` endpoint for processing metadata requests
- CORS support for web clients

## Quick Start

### 1. Start the Server

```bash
# 🚀 Recommended: Use the launcher script
python3 run_local_server.py

# 🔧 Alternative: Run directly from backend directory
cd backend && python3 server.py
```

The server will start on `http://localhost:8080` with:
- **🌐 Landing page**: `http://localhost:8080/` (HTML documentation)
- **📋 API info**: `http://localhost:8080/api` (JSON status)
- **📝 Metadata endpoint**: `http://localhost:8080/metadata` (POST)

The server will start on `http://localhost:8080`

### 2. API Key

The server uses a hardcoded API key for authentication:
```
bltz_shield_2025_secure_key
```

### 3. Test the API

You can test the API using curl:

```bash
# Valid request to /metadata endpoint
curl -X POST http://localhost:8080/metadata \
  -H "X-API-Key: bltz_shield_2025_secure_key" \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "user": "example"}'
```

Expected successful response:
```json
{
  "result": "success",
  "message": "Metadata request processed successfully",
  "timestamp": "2025-10-12T...",
  "received_data": {"test": "data", "user": "example"}
}
```

## API Endpoints

### POST /metadata

Processes metadata requests.

**Headers:**
- `X-API-Key`: Required API key for authentication
- `Content-Type`: application/json

**Request Body:**
- JSON object with any structure

**Response:**
- `200 OK`: Request processed successfully
- `400 Bad Request`: Invalid JSON format
- `401 Unauthorized`: Invalid or missing API key
- `404 Not Found`: Unknown endpoint
- `500 Internal Server Error`: Server error

## Testing

### Option 1: Using curl

```bash
# Test valid request
curl -X POST http://localhost:8080/metadata \
  -H "X-API-Key: bltz_shield_2025_secure_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello API"}'

# Test invalid API key
curl -X POST http://localhost:8080/metadata \
  -H "X-API-Key: wrong_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello API"}'



### Option 2: Using Python test client (requires requests library)

```bash
# Install requests if you want to use the test client
pip install requests

# Run the test client
python3 test_client.py
```

## Configuration

You can modify these settings in `server.py`:

- `HOST`: Server host (default: 'localhost')
- `PORT`: Server port (default: 8080)
- `HARDCODED_API_KEY`: API key for authentication

## Logging

The server logs all requests and responses with timestamps. Check the console output to see:
- Request methods and paths
- Request headers and bodies
- API key validation results
- Response data

## Adding New Endpoints

To add a new endpoint:

1. Add a new handler method in the `APIHandler` class:
```python
def _handle_your_endpoint(self, json_data):
    logger.info(f"Processing /your-endpoint with data: {json_data}")
    # Your logic here
    self._send_json_response(200, {"result": "success"})
```

2. Add the route in the `do_POST` method:
```python
elif path == '/your-endpoint':
    self._handle_your_endpoint(json_data)
```

## Response Format

All responses follow this format:
```json
{
  "result": "success|error",
  "message": "Description of the result",
  // Additional fields as needed
}
```
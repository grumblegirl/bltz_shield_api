# BLTZ Shield API

🛡️ A secure HTTP API server with JSON endpoints, API key authentication, and Supabase database integration for browser metadata storage.

## Features

- ✅ **WSGI Application** - Uses proper WSGI pattern for Vercel compatibility
- ✅ **API Key Authentication** - X-API-Key header validation  
- ✅ **JSON Endpoints** - RESTful API with JSON request/response
- ✅ **Supabase Database** - Browser metadata storage with JSONB support
- ✅ **Schema Validation** - Request data validation and sanitization
- ✅ **CORS Support** - Cross-origin requests enabled
- ✅ **Error Handling** - Comprehensive error responses
- ✅ **Local Development** - Built-in development server
- ✅ **Business Logic Separation** - Clean architecture with backend modules

## Quick Start

### Local Development

```bash
# Start the local server
cd api && python index.py

# Server runs on http://localhost:8080
```

### Test the API

```bash
# Test API info
curl http://localhost:8080/

# Test metadata endpoint
curl -X POST http://localhost:8080/metadata \
  -H "X-API-Key: bltz_shield_2025_secure_key" \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "message": "Hello API!"}'
```

## API Endpoints

### GET /
Returns API information and status.

**Response:**
```json
{
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
```

### POST /metadata
Store browser metadata in Supabase database with comprehensive validation.

**Headers:**
- `X-API-Key: bltz_shield_2025_secure_key` (required)
- `Content-Type: application/json`

**Request Body Schema:**
```json
{
  "model": "gpt",                    // Required: "gpt"|"claude"|"gemini"|"llama"
  "timestamp": "2025-01-27T12:00:00Z",  // Required: ISO 8601 format
  "metadata_data": {                 // Required: Browser metadata object
    "user_agent": "Mozilla/5.0...",
    "screen_width": 1920,
    "screen_height": 1080,
    "language": "en-US",
    "timezone": "America/New_York",
    // ... up to 53 metadata fields supported
  }
}
```

**Response:**
```json
{
  "result": "success",
  "message": "Metadata request processed successfully",
  "timestamp": "2025-01-27T17:30:00.123456",
  "metadata_summary": {
    "model": "gpt",
    "timestamp": "2025-01-27T12:00:00Z", 
    "fields_count": 53,
    "database_stored": true
  }
}
```

**Supported Models:**
- `gpt` - OpenAI GPT models
- `claude` - Anthropic Claude models
- `gemini` - Google Gemini models
- `llama` - Meta LLaMA models

## Project Structure

```
bltz_shield_api/
├── api/
│   └── index.py          # 🚀 WSGI application (main entry point)
├── backend/
│   ├── __init__.py       # 📦 Python package
│   └── api_logic.py      # 🧠 Business logic
├── doc/                  # 📚 Documentation
├── test/                 # 🧪 Test files
├── vercel.json          # ⚙️ Vercel deployment config
├── requirements.txt     # 📋 Dependencies
└── README.md           # 📖 This file
```

## Vercel Deployment

The API is ready for Vercel deployment with proper WSGI configuration.

```bash
# Deploy to Vercel
vercel

# The API will be available at:
# https://your-project.vercel.app/
```

## Authentication

All API endpoints require authentication via the `X-API-Key` header:

```
X-API-Key: bltz_shield_2025_secure_key
```

## Response Format

All API responses follow this standardized format:

```json
{
  "result": "success|error",
  "message": "Human-readable description",
  "timestamp": "ISO 8601 timestamp"
}
```

## Development

### Adding New Endpoints

1. Add handler function in `backend/api_logic.py`
2. Add route in `api/index.py` WSGI application
3. Test locally with `python api/index.py`

### Architecture

- **WSGI Application**: `api/index.py` - Main entry point for Vercel
- **Business Logic**: `backend/api_logic.py` - Shared logic for all endpoints  
- **Local Development**: Built-in wsgiref server for testing
- **Production**: Vercel serverless functions with Python runtime

## License

MIT License
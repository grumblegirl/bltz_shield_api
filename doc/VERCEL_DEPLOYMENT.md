# BLTZ Shield API - Vercel Deployment Guide

## 📁 Project Structure

```
bltz_shield_api/
├── index.py                    # 🌐 Root landing page (HTML)
├── api/
│   ├── index.py               # 🚀 Main API entry point (/api/)
│   └── metadata.py            # 📝 Dedicated /api/metadata endpoint  
├── backend/
│   ├── __init__.py           # 📦 Python package file
│   ├── api_logic.py          # 🧠 Business logic (shared between local & Vercel)
│   └── server.py             # 💻 Local development server
├── doc/
│   ├── README.md             # 📚 Main documentation
│   └── VERCEL_DEPLOYMENT.md  # 🚀 Deployment guide
├── test/
│   └── test_client.py        # 🧪 Test client (requires requests)
├── run_local_server.py       # ▶️  Server launcher script
├── vercel.json               # ⚙️  Vercel configuration  
└── requirements.txt          # 📋 Python dependencies
```

## 🚀 Vercel Deployment

### 1. Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli) installed
- Git repository (optional but recommended)

### 2. Deploy to Vercel

```bash
# Navigate to project directory
cd /Users/awatson/code/bltz_shield_api

# Deploy to Vercel
vercel

# Follow the prompts:
# - Set up and deploy? [Y/n] Y
# - Which scope? (select your account)
# - Link to existing project? [y/N] N
# - Project name: bltz-shield-api
# - Directory: ./
# - Override settings? [y/N] N
```

### 3. Vercel URLs

After deployment, your API will be available at:

- **🌐 Landing page**: `https://your-project.vercel.app/` (HTML documentation)
- **📋 API info**: `https://your-project.vercel.app/api` (JSON status)  
- **📝 Metadata endpoint**: `https://your-project.vercel.app/metadata` (POST)
- **📝 API metadata**: `https://your-project.vercel.app/api/metadata` (POST)

## 🧪 Testing Deployed API

### Test with curl:

```bash
# Replace YOUR_VERCEL_URL with your actual Vercel deployment URL
export VERCEL_URL="https://your-project.vercel.app"

# Test landing page (GET - returns HTML)
curl $VERCEL_URL/

# Test API info (GET - returns JSON)
curl $VERCEL_URL/api

# Test metadata endpoint (POST)
curl -X POST $VERCEL_URL/metadata \
  -H "X-API-Key: bltz_shield_2025_secure_key" \
  -H "Content-Type: application/json" \
  -d '{"test": "vercel", "message": "Hello from Vercel!"}'

# Test API metadata endpoint (POST - alternative route)
curl -X POST $VERCEL_URL/api/metadata \
  -H "X-API-Key: bltz_shield_2025_secure_key" \
  -H "Content-Type: application/json" \
  -d '{"environment": "vercel", "deployed": true}'
```

## 🔧 Local Development

For local testing (same business logic as Vercel):

```bash
# Start local server (recommended method)
python3 run_local_server.py

# Alternative: Run directly from backend directory  
cd backend && python3 server.py

# Test locally
curl -X POST http://localhost:8080/metadata \
  -H "X-API-Key: bltz_shield_2025_secure_key" \
  -H "Content-Type: application/json" \
  -d '{"local": "test"}'
```

## 📋 Key Features

✅ **Serverless Functions**: Each endpoint is a separate serverless function  
✅ **Shared Business Logic**: `api_logic.py` contains all business logic  
✅ **Multiple Entry Points**: `index.py` for root, `api/metadata.py` for dedicated endpoint  
✅ **CORS Support**: Cross-origin requests enabled  
✅ **API Key Authentication**: X-API-Key header validation  
✅ **Comprehensive Logging**: Request/response logging  
✅ **Error Handling**: Standardized error responses  

## 🔄 Adding New Endpoints

### Method 1: Add to index.py routes
Update the business logic in `api_logic.py` and add new routes to `vercel.json`.

### Method 2: Create dedicated endpoint files
1. Create new file: `api/your-endpoint.py`
2. Copy the structure from `api/metadata.py`
3. Update the endpoint logic
4. Vercel will automatically detect the new endpoint

## 🌍 Environment Variables (Optional)

If you want to use environment variables instead of hardcoded values:

```bash
# Set in Vercel dashboard or CLI
vercel env add API_KEY
# Enter: bltz_shield_2025_secure_key

# Update api_logic.py to use:
# import os
# HARDCODED_API_KEY = os.environ.get('API_KEY', 'fallback_key')
```

## 📊 Monitoring

- **Vercel Dashboard**: Monitor function invocations, errors, and performance
- **Logs**: View real-time logs in Vercel dashboard
- **Analytics**: Built-in analytics for request patterns

## 🔒 Security Notes

- API key is currently hardcoded for simplicity
- All requests are logged (be careful with sensitive data)
- CORS is enabled for all origins (consider restricting in production)
- Consider using Vercel's environment variables for secrets

## 🚨 Troubleshooting

### Common Issues:

1. **Import errors**: Ensure `api_logic.py` is in the root directory
2. **CORS issues**: Check headers in browser developer tools
3. **Function timeout**: Vercel has execution time limits
4. **Path issues**: Check `vercel.json` routes configuration

### Debugging:

```bash
# Check Vercel logs
vercel logs

# Local debugging
python3 server.py
# Then test locally before deploying
```
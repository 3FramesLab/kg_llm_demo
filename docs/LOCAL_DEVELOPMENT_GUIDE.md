# Local Development Guide

Complete guide for running DQ-POC locally without Docker.

---

## Prerequisites

### Required Software

1. **Python 3.9+**
   ```bash
   python --version
   # Should show: Python 3.9.x or higher
   ```

2. **Node.js 18+**
   ```bash
   node --version
   # Should show: v18.x.x or higher

   npm --version
   # Should show: 9.x.x or higher
   ```

3. **Redis (for FalkorDB)** - Optional but recommended
   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Mac: `brew install redis`
   - Linux: `sudo apt-get install redis-server`

---

## Setup Steps

### Step 1: Clone and Navigate to Project

```bash
cd D:/learning/dq-poc
```

### Step 2: Backend Setup (Python/FastAPI)

#### 2.1 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate

# You should see (venv) in your prompt
```

#### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your settings
notepad .env  # Windows
# or
nano .env     # Mac/Linux
```

**Minimum required in `.env`:**
```env
# FalkorDB (if running locally)
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# OpenAI (optional but recommended for LLM features)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

#### 2.4 Start Backend Server

```bash
# Make sure you're in the project root with venv activated
python -m kg_builder.main

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Backend is now running at:** http://localhost:8000

**Test it:**
```bash
# Open new terminal
curl http://localhost:8000/api/v1/health

# Or visit in browser:
# http://localhost:8000/docs
```

---

### Step 3: Frontend Setup (React)

Open a **NEW terminal** (keep backend running in first terminal)

#### 3.1 Navigate to Web App Directory

```bash
cd D:/learning/dq-poc/web-app
```

#### 3.2 Install Node Dependencies

```bash
npm install

# This will take 2-3 minutes
# You should see: added XXX packages
```

#### 3.3 Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env
notepad .env  # Windows
# or
nano .env     # Mac/Linux
```

**Set API URL in `.env`:**
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

#### 3.4 Start Frontend Development Server

```bash
npm start

# You should see:
# Compiled successfully!
# webpack compiled with 1 warning
#
# You can now view dq-poc-web in the browser.
#
#   Local:            http://localhost:3000
#   On Your Network:  http://192.168.x.x:3000
```

**Frontend is now running at:** http://localhost:3000

**Browser will automatically open** to http://localhost:3000

---

## Verify Everything is Working

### 1. Check Backend Health

Open browser to: http://localhost:8000/api/v1/health

Should see:
```json
{
  "status": "healthy",
  "falkordb_connected": false,
  "graphiti_available": true,
  "llm_enabled": true
}
```

**Note:** `falkordb_connected: false` is OK if you don't have Redis/FalkorDB running locally.

### 2. Check Frontend

Browser should show the Dashboard page with:
- System Health panel
- LLM Status panel
- Statistics cards

### 3. Navigate Through Pages

Click through all pages in the sidebar:
- ✅ Dashboard
- ✅ Schemas
- ✅ Knowledge Graph
- ✅ Reconciliation
- ✅ Natural Language
- ✅ Execution

---

## Optional: Run FalkorDB Locally

If you want full graph database functionality:

### Option A: Docker (Easiest)

```bash
# Just run FalkorDB container
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest

# Verify it's running
docker ps | grep falkordb
```

### Option B: Redis + FalkorDB Module (Advanced)

1. Install Redis
2. Download FalkorDB module
3. Load module in Redis

**For development, Docker option is recommended.**

---

## Development Workflow

### Terminal Setup

You'll need **2 terminals** running simultaneously:

```
Terminal 1 (Backend):
D:/learning/dq-poc> .\venv\Scripts\activate
(venv) D:/learning/dq-poc> python -m kg_builder.main
INFO: Uvicorn running on http://0.0.0.0:8000

Terminal 2 (Frontend):
D:/learning/dq-poc/web-app> npm start
Compiled successfully!
Local: http://localhost:3000
```

### Making Changes

**Backend Changes:**
1. Edit Python files
2. Save file
3. Server auto-reloads (if using `--reload` flag)
4. Refresh browser

**Frontend Changes:**
1. Edit React files
2. Save file
3. Browser auto-refreshes (hot reload)
4. See changes instantly

---

## Common Commands

### Backend

```bash
# Start backend
cd D:/learning/dq-poc
.\venv\Scripts\activate
python -m kg_builder.main

# Run tests
pytest tests/ -v

# Check Python version
python --version

# Deactivate virtual environment
deactivate
```

### Frontend

```bash
# Start frontend
cd D:/learning/dq-poc/web-app
npm start

# Build for production
npm run build

# Run tests
npm test

# Check Node version
node --version
```

---

## Troubleshooting

### Backend Issues

#### Port 8000 Already in Use

```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

#### Module Not Found Error

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install <package-name>
```

#### FalkorDB Connection Failed

This is OK for local development. The app will use Graphiti (file-based) as fallback.

To fix:
```bash
# Run FalkorDB in Docker
docker run -d -p 6379:6379 falkordb/falkordb:latest
```

### Frontend Issues

#### Port 3000 Already in Use

Edit `package.json` and add:
```json
"scripts": {
  "start": "PORT=3001 react-scripts start"
}
```

Or kill the process:
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

#### Cannot Find Module

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Or
npm cache clean --force
npm install
```

#### CORS Errors

Make sure:
1. Backend is running on port 8000
2. Frontend `.env` has: `REACT_APP_API_URL=http://localhost:8000/api/v1`
3. Restart both servers

### OpenAI API Key Issues

If you don't have an OpenAI API key:

1. LLM features will be disabled (OK for testing)
2. You can still use:
   - Basic schema parsing
   - Pattern-based rule generation
   - Graph visualization
   - SQL export

To enable LLM features:
1. Get API key from: https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-your-key`
3. Restart backend server

---

## File Locations

### Backend Configuration
- **Main config:** `D:/learning/dq-poc/.env`
- **Python code:** `D:/learning/dq-poc/kg_builder/`
- **Schemas:** `D:/learning/dq-poc/schemas/`
- **Data storage:** `D:/learning/dq-poc/data/`

### Frontend Configuration
- **Web config:** `D:/learning/dq-poc/web-app/.env`
- **React code:** `D:/learning/dq-poc/web-app/src/`
- **Build output:** `D:/learning/dq-poc/web-app/build/`

---

## Quick Reference

### Start Everything

```bash
# Terminal 1: Backend
cd D:/learning/dq-poc
.\venv\Scripts\activate
python -m kg_builder.main

# Terminal 2: Frontend (new terminal)
cd D:/learning/dq-poc/web-app
npm start
```

### Stop Everything

```bash
# In each terminal, press:
Ctrl + C

# Then deactivate Python virtual environment:
deactivate
```

### Access Points

- **Web App:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Production Build (Local Testing)

### Build Frontend for Production

```bash
cd web-app
npm run build

# Creates optimized build in web-app/build/
```

### Serve Production Build Locally

```bash
# Install serve globally
npm install -g serve

# Serve the build
serve -s build -l 3000

# Access at: http://localhost:3000
```

---

## Environment Variables Reference

### Backend (.env in project root)

```env
# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_PASSWORD=

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Features
ENABLE_LLM_EXTRACTION=true
ENABLE_LLM_ANALYSIS=true

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Logging
LOG_LEVEL=INFO

# Reconciliation
RECON_MIN_CONFIDENCE=0.7
RECON_ENABLE_LLM=true
```

### Frontend (.env in web-app/)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## Tips for Local Development

### 1. Use Multiple Monitors
- Left monitor: Code editor
- Right monitor: Browser with app open

### 2. Browser DevTools
- Press F12 to open DevTools
- **Console tab:** See errors and logs
- **Network tab:** See API requests
- **React DevTools:** Install extension for React debugging

### 3. Code Editor Extensions
**VS Code Extensions (Recommended):**
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- ESLint
- Prettier
- Auto Rename Tag

### 4. Git Workflow
```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes, then commit
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/my-new-feature
```

### 5. Hot Reload
- Frontend: Changes reflect immediately
- Backend: Restart server to see changes (or use `--reload` flag)

---

## Next Steps After Setup

1. **Explore the Dashboard**
   - http://localhost:3000

2. **Try Creating a Knowledge Graph**
   - Go to "Knowledge Graph" page
   - Select schemas
   - Click "Generate"

3. **Test API Directly**
   - http://localhost:8000/docs
   - Try out endpoints

4. **Read the Documentation**
   - `HOW_TO_USE.md` - Usage guide
   - `WEB_APP_GUIDE.md` - Web app details
   - `LLM_PROMPTS_REFERENCE.md` - LLM prompts

---

## Need Help?

### Check Logs

**Backend logs:**
```bash
# In backend terminal, you'll see logs like:
INFO:     127.0.0.1:54321 - "GET /api/v1/health HTTP/1.1" 200 OK
```

**Frontend logs:**
```bash
# In frontend terminal:
Compiling...
Compiled successfully!
```

**Browser console:**
- Press F12
- Check Console tab for errors

### Common Issues

1. **"Module not found"** → Reinstall dependencies
2. **"Port already in use"** → Kill the process or use different port
3. **"CORS error"** → Check API URL in frontend .env
4. **"Connection refused"** → Make sure backend is running
5. **Blank page** → Check browser console for errors

---

## Summary

**To run locally:**

1. **Backend:**
   ```bash
   cd D:/learning/dq-poc
   .\venv\Scripts\activate
   python -m kg_builder.main
   ```

2. **Frontend:**
   ```bash
   cd D:/learning/dq-poc/web-app
   npm start
   ```

3. **Access:** http://localhost:3000

**That's it!** 🚀

You now have a fully functional local development environment.

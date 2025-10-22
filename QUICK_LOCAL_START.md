# Quick Local Start Guide

**Get DQ-POC running locally in 5 minutes!**

---

## Prerequisites

- ✅ Python 3.9+
- ✅ Node.js 18+
- ✅ npm

Check versions:
```bash
python --version
node --version
npm --version
```

---

## Step 1: Backend Setup (2 minutes)

```bash
# 1. Navigate to project
cd D:/learning/dq-poc

# 2. Create & activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
.\venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.example .env

# 5. Start backend
python -m kg_builder.main
```

**Backend running at:** http://localhost:8000 ✅

Leave this terminal running!

---

## Step 2: Frontend Setup (3 minutes)

**Open a NEW terminal** (keep backend running)

```bash
# 1. Navigate to web app
cd D:/learning/dq-poc/web-app

# 2. Install dependencies
npm install

# 3. Copy environment file
cp .env.example .env

# 4. Start frontend
npm start
```

**Browser will auto-open at:** http://localhost:3000 ✅

---

## You're Done! 🎉

You should now see:

- **Terminal 1:** Backend running on port 8000
- **Terminal 2:** Frontend running on port 3000
- **Browser:** Dashboard page at http://localhost:3000

---

## Test It Works

1. **Dashboard** should show system health ✅
2. Click **"Schemas"** to see available schemas ✅
3. Click **"Knowledge Graph"** to generate a KG ✅

---

## Stop Everything

Press `Ctrl + C` in both terminals

---

## Troubleshooting

### Port Already in Use?

**Backend (8000):**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000):**
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

### Module Not Found?

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd web-app
npm install
```

### Still Having Issues?

See **LOCAL_DEVELOPMENT_GUIDE.md** for detailed troubleshooting.

---

## What's Next?

1. **Add OpenAI API Key** (optional, for LLM features):
   ```env
   # Edit .env in project root
   OPENAI_API_KEY=sk-your-api-key-here
   ```

2. **Run FalkorDB** (optional, for full graph features):
   ```bash
   docker run -d -p 6379:6379 falkordb/falkordb:latest
   ```

3. **Start Building:**
   - Generate Knowledge Graphs
   - Create Reconciliation Rules
   - Define Natural Language Relationships
   - Execute Reconciliations

---

## Access Points

| Service | URL |
|---------|-----|
| **Web App** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |

---

## Quick Commands

### Daily Startup

```bash
# Terminal 1:
cd D:/learning/dq-poc
.\venv\Scripts\activate
python -m kg_builder.main

# Terminal 2:
cd D:/learning/dq-poc/web-app
npm start
```

### Daily Shutdown

Press `Ctrl + C` in both terminals

---

**Happy Coding! 🚀**

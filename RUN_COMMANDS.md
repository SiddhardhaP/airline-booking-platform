# 🚀 Complete Command List - Copy & Paste Ready

## ✅ Docker is Already Running - Skip to Step 2

---

## Step 1: Verify Database (Quick Check)

```powershell
# Check if database container is running
docker ps

# If not running, start it:
docker-compose up -d

# Check database logs (optional)c
docker logs pgvector_db
```

---

## Step 2: Backend Setup (Terminal 1)

Open **PowerShell** or **Command Prompt** and run these commands **one by one**:

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt

# If pgvector installation fails, install it separately:
# pip install pgvector

# Create .env file with required configuration
@"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/airline_booking
GEMINI_API_KEY=your_gemini_api_key_here
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
AMADEUS_BASE_URL=https://test.api.amadeus.com
BACKEND_URL=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8

# Run database migrations (creates all tables)
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

**✅ Keep this terminal open!** The server will run here.

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## Step 3: Frontend Setup (Terminal 2)

Open a **NEW PowerShell** or **Command Prompt** window and run:

```powershell
# Navigate to frontend directory
cd frontend

# Install all Node.js dependencies
npm install

# Create .env file
"VITE_API_URL=http://localhost:8000" | Out-File -FilePath .env -Encoding utf8

# Start frontend development server
npm run dev
```

**✅ Keep this terminal open!** The frontend will run here.

**Expected Output:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
```

---

## Step 4: Access the Application

Open your browser and go to:

- **Frontend Application**: http://localhost:5173
- **Backend API Documentation**: http://localhost:8000/docs
- **Backend Health Check**: http://localhost:8000/health

---

## ⚠️ Important: Update Your API Keys

**Before using the chat feature**, edit `backend/.env` and replace:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

With your actual Gemini API key from: https://makersuite.google.com/app/apikey

**Note**: Amadeus API keys are optional. If not provided, the system will use mock flight data.

---

## 🧪 Quick Test Commands

### Test Backend Health
```powershell
curl http://localhost:8000/health
```

### Test Database Connection
```powershell
docker exec -it pgvector_db psql -U postgres -d airline_booking -c "SELECT 1;"
```

### Test Frontend
Just open: http://localhost:5173

---

## 🛑 How to Stop Everything

### Stop Frontend
- Press `Ctrl+C` in Terminal 2 (frontend)

### Stop Backend
- Press `Ctrl+C` in Terminal 1 (backend)

### Stop Database
```powershell
docker-compose down
```

---

## 📋 Complete Command Summary (All at Once)

### Terminal 1 - Backend:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
@"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/airline_booking
GEMINI_API_KEY=your_gemini_api_key_here
BACKEND_URL=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend:
```powershell
cd frontend
npm install
"VITE_API_URL=http://localhost:8000" | Out-File -FilePath .env -Encoding utf8
npm run dev
```

---

## ✅ Success Checklist

After running all commands, verify:

- [ ] Backend terminal shows: `Uvicorn running on http://127.0.0.1:8000`
- [ ] Frontend terminal shows: `Local: http://localhost:5173/`
- [ ] Browser opens http://localhost:5173 successfully
- [ ] Can access http://localhost:8000/docs (API documentation)
- [ ] Chat interface loads and responds (after adding Gemini API key)

---

## 🎯 Next Steps

1. **Add your Gemini API key** to `backend/.env` for chat functionality
2. **Test the chat**: Go to http://localhost:5173 and try searching for flights
3. **Explore API docs**: Visit http://localhost:8000/docs to see all available endpoints

---

**You're all set! 🚀**


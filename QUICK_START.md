# CBB Analytics - Quick Start Guide

Follow these steps to get the full stack running locally.

## ⚡ Quick Start (5 minutes)

### Step 1: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Ingest data from CSVs
python manage.py ingest_data --season 2026

# Start Django server (keep this running)
python manage.py runserver
```

✅ Backend should now be running on **http://localhost:8000**

### Step 2: Frontend Setup (New Terminal)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.local.example .env.local

# Start Next.js dev server
npm run dev
```

✅ Frontend should now be running on **http://localhost:3000**

### Step 3: Verify

1. Open http://localhost:3000 in your browser
2. Click "View Rankings"
3. You should see 365 teams loaded from your CSVs!

---

## 🎯 Common Commands

### Backend

```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# Re-ingest data (if CSVs updated)
python manage.py ingest_data --season 2026 --force

# Access Django admin
# Navigate to http://localhost:8000/admin
# Login with superuser credentials

# Run migrations (after model changes)
python manage.py makemigrations
python manage.py migrate
```

### Frontend

```powershell
cd frontend

# Development
npm run dev

# Build for production
npm run build
npm start

# Type checking
npx tsc --noEmit
```

---

## 🗂️ Data Files

The ingestion command looks for CSVs in these locations:

```
CBB Analytical Dashboard/
├── KenPom Data/
│   └── kenpom_tableau.csv       # Required
├── Bart Torvik/
│   └── torvik_tableau.csv       # Required
└── CBB Analytics/
    └── cbb_analytics_tableau.csv  # Optional
```

**Update data:**
1. Run your scraper scripts to refresh CSVs
2. Re-run: `python manage.py ingest_data --season 2026 --force`
3. Refresh your browser

---

## 🧪 Testing the Stack

### Test Backend API

```powershell
# Test seasons endpoint
curl http://localhost:8000/api/seasons/

# Test rankings
curl http://localhost:8000/api/rankings/?season=2026

# Test team profile
curl http://localhost:8000/api/teams/michigan/profile/?season=2026
```

Or visit in browser:
- http://localhost:8000/api/seasons/
- http://localhost:8000/api/rankings/
- http://localhost:8000/admin/

### Test Frontend Pages

- Home: http://localhost:3000
- Rankings: http://localhost:3000/rankings
- Team (example): http://localhost:3000/team/michigan
- Matchup: http://localhost:3000/matchup
- Glossary: http://localhost:3000/glossary
- About: http://localhost:3000/about

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "No module named django"**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "Table doesn't exist"**
```powershell
# Run migrations
python manage.py migrate
```

**Error: "CSV file not found"**
- Verify CSV files exist in correct folders
- Check file names match exactly: `kenpom_tableau.csv`, `torvik_tableau.csv`
- Use `--kenpom` and `--torvik` flags to specify custom paths

### Frontend errors

**Error: "Network Error" / API not responding**
- Ensure Django backend is running on http://localhost:8000
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000/api`
- Verify CORS settings in Django `config/settings.py`

**Error: "Cannot find module"**
```powershell
# Delete node_modules and reinstall
rm -r node_modules
npm install
```

**Error: "Port 3000 already in use"**
```powershell
# Use a different port
npm run dev -- -p 3001
```

### CORS Issues

If you see CORS errors in browser console:

1. Check `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
]
```

2. Restart Django server

---

## 📋 Next Steps

1. ✅ Verify both servers are running
2. ✅ Browse to http://localhost:3000/rankings
3. ✅ Click on a team to view profile
4. ✅ Try the matchup tool
5. 🚧 Implement visualizations (see IMPLEMENTATION_CHECKLIST.md)
6. 🚧 Deploy to production

---

## 🚀 Ready for Production?

See deployment guides:
- Backend: [`backend/README.md`](backend/README.md#production-deployment)
- Frontend: [`frontend/README.md`](frontend/README.md#deployment)
- Or check [`DEPLOYMENT.md`](DEPLOYMENT.md)

---

Need help? Check the full documentation in `PROJECT_README.md` or each component's README.

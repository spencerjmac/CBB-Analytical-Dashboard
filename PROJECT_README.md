# 🏀 College Basketball Analytics Dashboard - Refactored

A production-ready web application for college basketball analytics with a Django backend and Next.js frontend.

## 📊 Overview

This project transforms raw college basketball statistics from KenPom, Bart Torvik, and CBB Analytics into an interactive, KenPom/Torvik-style analytics dashboard with custom visualizations and metrics.

**Architecture:**
- **Backend:** Django 5.0 + Django REST Framework (API + data ingestion)
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Database:** SQLite (dev) / PostgreSQL (production)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "CBB Analytical Dashboard"
```

2. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Ingest data
python manage.py ingest_data --season 2026

# Start server
python manage.py runserver
```

Backend runs on `http://localhost:8000`

3. **Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local

# Start development server
npm run dev
```

Frontend runs on `http://localhost:3000`

## 📁 Project Structure

```
CBB Analytical Dashboard/
├── backend/                 # Django + DRF backend
│   ├── config/             # Django settings
│   ├── core/               # Core models
│   ├── api/                # DRF API endpoints
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Pages (App Router)
│   │   ├── components/    # React components
│   │   ├── lib/           # API client
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
│
├── KenPom Data/           # KenPom CSV source
├── Bart Torvik/           # Torvik CSV source
├── CBB Analytics/         # CBB Analytics CSV source
├── College Logos/         # Team logos
│
└── IMPLEMENTATION_CHECKLIST.md  # Detailed progress tracker
```

## 🎯 Features

### Implemented ✅

- **Team Rankings** - Sortable/filterable table for 365 D1 teams
- **Team Profiles** - Detailed pages with tabs (Overview, Four Factors, Splits, Resume)
- **Matchup Tool** - Head-to-head comparison with win probabilities
- **Glossary** - Comprehensive metric definitions
- **About** - Data sources and methodology
- **REST API** - Complete backend API with DRF
- **Data Ingestion** - Automated CSV → database pipeline

### In Progress 🚧

- Trapezoid of Excellence visualization
- Efficiency Landscape heatmap
- Kill Shot graphic
- Crystal Ball predictor

See [`IMPLEMENTATION_CHECKLIST.md`](IMPLEMENTATION_CHECKLIST.md) for complete status.

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api/`

### Core Endpoints

```
GET  /api/seasons/                                    # List seasons
GET  /api/conferences/                                # List conferences
GET  /api/rankings/?season=2026&sort=adj_em&dir=desc # Team rankings
GET  /api/teams/{slug}/                               # Team detail
GET  /api/teams/{slug}/stats/?season=2026            # Team season stats
GET  /api/teams/{slug}/profile/?season=2026          # Team profile
GET  /api/matchup/?teamA=michigan&teamB=duke         # Matchup analysis
```

Full API documentation in [`backend/README.md`](backend/README.md).

## 🗄️ Database Schema

**Core Models:**
- `Season` - Basketball seasons (2025-26, etc.)
- `Conference` - NCAA conferences (B10, ACC, etc.)
- `Team` - D1 teams (slug, name, logo)
- `TeamSeasonStats` - Main stats table (40+ fields)
  - Efficiency metrics (AdjEM, AdjO, AdjD, Tempo)
  - Four Factors (eFG%, TOV%, ORB%, FTR)
  - Shooting splits (2P%, 3P%)
  - Resume metrics (WAB, SOR, Barthag, Luck, SOS)
  - Precomputed margins

See [`backend/core/models.py`](backend/core/models.py) for full schema.

## 📊 Data Sources

- **KenPom** - Adjusted efficiency metrics, tempo, luck, SOS
- **Bart Torvik** - Four Factors, shooting splits, advanced metrics
- **CBB Analytics** - Additional ratings (planned)

All data sourced from publicly available statistics. Not affiliated with or endorsed by the above sites.

## 🚢 Deployment

### Backend (Django)

**Option 1: Render** (Recommended)
1. Create Web Service from GitHub
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

**Option 2: Fly.io**
```bash
flyctl launch
flyctl deploy
```

**Option 3: DigitalOcean App Platform**
1. Connect GitHub repo
2. Add Managed Database
3. Deploy

See [`backend/README.md`](backend/README.md) for details.

### Frontend (Next.js)

**Vercel** (Recommended)
1. Connect GitHub repo
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Deploy

See [`frontend/README.md`](frontend/README.md) for details.

## 🛠️ Development

### Backend Commands

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Ingest data
python manage.py ingest_data --season 2026

# Run tests
python manage.py test

# Django shell
python manage.py shell
```

### Frontend Commands

```bash
# Development server
npm run dev

# Build for production
npm run build

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

## 📚 Documentation

- [`backend/README.md`](backend/README.md) - Backend setup, API docs, deployment
- [`frontend/README.md`](frontend/README.md) - Frontend setup, pages, deployment
- [`IMPLEMENTATION_CHECKLIST.md`](IMPLEMENTATION_CHECKLIST.md) - Detailed progress tracker

## 🔮 Roadmap

**Phase 1: MVP** (Current)
- [x] Core pages (rankings, team, matchup)
- [x] REST API with all endpoints
- [x] Data ingestion pipeline
- [ ] Trapezoid of Excellence visualization
- [ ] Deploy to production

**Phase 2: Visualizations**
- [ ] Efficiency Landscape
- [ ] Kill Shot graphic
- [ ] Crystal Ball predictor

**Phase 3: Enhancements**
- [ ] Historical data (multiple seasons)
- [ ] Advanced filtering
- [ ] Data export (CSV/JSON)
- [ ] Mobile optimization
- [ ] Dark mode

## 🐛 Troubleshooting

**Backend won't start:**
- Check virtual environment is activated
- Run `pip install -r requirements.txt`
- Verify `DEBUG=True` in `.env`
- Run migrations: `python manage.py migrate`

**Frontend API errors:**
- Ensure backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings in Django `settings.py`

**Data ingestion fails:**
- Check CSV file paths exist
- Verify season year matches CSV data
- Check Django admin for `DataIngestionRun` logs

## 📝 License

[Specify your license here]

## 👤 Author

[Your name/organization]

---

**Last Updated:** February 11, 2026

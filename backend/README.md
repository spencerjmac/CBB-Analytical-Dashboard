# CBB Analytics - Django Backend

Django + Django REST Framework backend for College Basketball Analytics application.

## 🏗️ Architecture

- **Django 5.0** - Web framework
- **Django REST Framework** - API layer
- **SQLite** (dev) / **PostgreSQL** (production) - Database
- **Pandas** - Data ingestion from CSVs

## 📊 Database Schema

### Core Models

**Season** - Basketball seasons (e.g., 2025-26)
- year, display_name, is_current

**Conference** - NCAA conferences
- code (B10, ACC), name

**Team** - D1 basketball teams (365 teams)
- slug, name, aliases, logo_url

**TeamSeasonStats** - Main stats table
- Relations: team, season, conference
- Core metrics: adj_em, adj_o, adj_d, adj_tempo
- Four Factors: eFG%, TOV%, ORB%, FTR (offense + defense)
- Shooting splits: 2P%, 3P%, 3P rate
- Resume: WAB, SOR, Barthag, Luck, SOS
- Precomputed margins

**DataIngestionRun** - Audit log for data imports

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
```

### Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (for Django admin)
python manage.py createsuperuser

# Ingest data from CSVs
python manage.py ingest_data --season 2026
```

### Run Development Server

```bash
python manage.py runserver

# Server runs on http://localhost:8000
# API available at http://localhost:8000/api/
# Admin at http://localhost:8000/admin/
```

## 📡 API Endpoints

### Seasons
```
GET /api/seasons/
```

Returns list of all available seasons.

### Rankings
```
GET /api/rankings/?season=2026&sort=adj_em&dir=desc&conference=B10&search=mich
```

Query params:
- `season` - Season year (default: current)
- `sort` - Field to sort by (default: rank)
- `dir` - `asc` or `desc` (default: asc)
- `conference` - Conference code filter
- `search` - Team name search

### Teams
```
GET /api/teams/
GET /api/teams/{slug}/
GET /api/teams/{slug}/stats/?season=2026
GET /api/teams/{slug}/profile/?season=2026
```

### Matchup
```
GET /api/matchup/?season=2026&teamA=michigan&teamB=duke&site=neutral
```

Query params:
- `season` - Season year
- `teamA` - Team A slug
- `teamB` - Team B slug
- `site` - `neutral`, `home`, or `away`

Returns win probability, predicted margin, and key edges.

## 🔧 Management Commands

### ingest_data

Loads data from CSV files into database.

```bash
python manage.py ingest_data --season 2026 [--force]

# Custom paths
python manage.py ingest_data --season 2026 \
  --kenpom /path/to/kenpom.csv \
  --torvik /path/to/torvik.csv
```

Options:
- `--season` - Season year (required)
- `--kenpom` - Custom KenPom CSV path
- `--torvik` - Custom Torvik CSV path
- `--force` - Force re-import even if data exists

## 🗄️ Django Admin

Access Django admin panel at `http://localhost:8000/admin/`

Features:
- View/edit seasons, conferences, teams
- Browse team stats
- Monitor data ingestion runs
- Filter and search

## 🚢 Production Deployment

### Environment Variables

```env
DEBUG=False
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=postgres://user:pass@host:5432/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### PostgreSQL Setup

Update `config/settings.py`:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

### Deployment Options

**Render** (Recommended)
1. Create new Web Service
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn config.wsgi:application`
5. Add environment variables
6. Add PostgreSQL database

**Fly.io**
```bash
flyctl launch
flyctl deploy
```

**DigitalOcean App Platform**
1. Create new app from GitHub
2. Set build/run commands
3. Add PostgreSQL database

## 📁 Project Structure

```
backend/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                # Core models
│   ├── models.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── ingest_data.py
├── api/                 # DRF API
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── .env
```

## 🔍 Troubleshooting

**CORS errors:**
- Check `CORS_ALLOWED_ORIGINS` in `.env`
- Ensure frontend URL is included

**Data not loading:**
- Check CSV paths in `ingest_data` command
- Verify season year matches CSV data
- Check Django admin for ingestion logs

**Database errors:**
- Run `python manage.py migrate`
- Check DATABASE_URL in `.env`

## 🛠️ Development

### Run tests
```bash
python manage.py test
```

### Create new migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Shell access
```bash
python manage.py shell
```

## 📝 License

See root LICENSE file.

# 🏀 CBB Analytics - Implementation Checklist

This document tracks the refactoring from a static Next.js app to a production-ready Django + Next.js architecture.

## ✅ COMPLETED

### Backend (Django + DRF)

- [x] Django project scaffolding
  - [x] `config/settings.py` with REST Framework + CORS
  - [x] `config/urls.py` routing
  - [x] Environment variable support (`.env`)
- [x] Core Django models
  - [x] `Season` - Basketball seasons
  - [x] `Conference` - NCAA conferences
  - [x] `Team` - D1 teams with slugs
  - [x] `TeamSeasonStats` - Main stats table (40+ fields)
  - [x] `DataIngestionRun` - Audit log
- [x] Django Admin
  - [x] Admin interfaces for all models
  - [x] Search, filtering, readonly fields
- [x] DRF API endpoints
  - [x] `/api/seasons/` - List seasons
  - [x] `/api/conferences/` - List conferences
  - [x] `/api/rankings/` - Sortable/filterable rankings
  - [x] `/api/teams/{slug}/` - Team detail
  - [x] `/api/teams/{slug}/stats/` - Team stats for season
  - [x] `/api/teams/{slug}/profile/` - Full profile with history
  - [x] `/api/matchup/` - Head-to-head analysis
- [x] Data ingestion
  - [x] `manage.py ingest_data` command
  - [x] CSV parsing (KenPom + Torvik)
  - [x] Team name normalization
  - [x] Conference mapping
  - [x] Error handling and logging
- [x] Documentation
  - [x] `backend/README.md` with setup instructions
  - [x] API endpoint documentation
  - [x] Deployment guide (Render/Fly.io/DigitalOcean)

### Frontend (Next.js)

- [x] Next.js 14 App Router setup
  - [x] TypeScript configuration
  - [x] Tailwind CSS setup
  - [x] Environment variables
- [x] TypeScript types
  - [x] API response interfaces
  - [x] Complete type coverage
- [x] API client
  - [x] Axios-based client (`src/lib/api.ts`)
  - [x] All API methods implemented
  - [x] Error handling
- [x] Core pages
  - [x] Home page with feature cards
  - [x] `/rankings` - Sortable table with filters
  - [x] `/team/[slug]` - Team profile with tabs
  - [x] `/matchup` - Matchup tool with win probability
  - [x] `/glossary` - Metrics definitions
  - [x] `/about` - Data sources and methodology
- [x] Navigation
  - [x] Responsive header
  - [x] Active route highlighting
- [x] UI Components
  - [x] Loading states (spinner)
  - [x] Error messages
  - [x] Sortable table headers
  - [x] Tab navigation
- [x] Documentation
  - [x] `frontend/README.md` with setup
  - [x] API client usage examples
  - [x] Deployment guide (Vercel)

## 🚧 IN PROGRESS

- [ ] Visualizations
  - [ ] Trapezoid of Excellence (scatter + polygon overlay)
  - [ ] Efficiency Landscape (heatmap/contours)
  - [ ] Kill Shot graphic (team page + standalone)
  - [ ] Crystal Ball predictor (championship checklist)

## 📋 TODO (MVP)

### Visualizations

- [ ] **Trapezoid of Excellence**
  - [ ] Port Tableau trapezoid polygon coordinates
  - [ ] ECharts scatter plot (Tempo vs AdjEM)
  - [ ] Overlay trapezoid boundaries
  - [ ] Highlight teams inside/outside
  - [ ] Click point → navigate to team page
  - [ ] Season filter
  - [ ] Backend: Add `/api/viz/trapezoid/` endpoint
  
- [ ] **Efficiency Landscape**
  - [ ] Define X/Y fields from Tableau
  - [ ] Backend: Precompute heatmap grid
  - [ ] Frontend: ECharts heatmap or contour plot
  - [ ] Color scale (red = bad, green = good)
  - [ ] Hover tooltips
  
- [ ] **Kill Shot Graphic**
  - [ ] Extract thresholds from Tableau
  - [ ] Backend: Precompute flags per team
  - [ ] Frontend: Visual layout matching Tableau
  - [ ] Embed on team profile page
  - [ ] Standalone `/viz/kill-shot` page
  
- [ ] **Crystal Ball**
  - [ ] Define championship profile rules
  - [ ] Backend: `/api/viz/crystal-ball/` with team evaluation
  - [ ] Frontend: Checklist UI (✓/✗ for each criterion)
  - [ ] Embed on team profile
  - [ ] Standalone `/viz/crystal-ball` page

### Data Enhancements

- [ ] Logo resolution
  - [ ] Map team slugs to `/College Logos/output/logos/*.png`
  - [ ] Update ingestion to set `logo_url`
  - [ ] Serve logos from Django static files or frontend public folder
  
- [ ] Conference data
  - [ ] Create comprehensive conference mapping
  - [ ] Full conference names (not just codes)
  - [ ] Conference logos (optional)
  
- [ ] Historical data
  - [ ] Ingest multiple seasons (2020-2026)
  - [ ] Season switcher in UI
  - [ ] Historical trends on team pages

### Performance

- [ ] Backend caching
  - [ ] Cache rankings response (5 min TTL)
  - [ ] Cache team stats (5 min TTL)
  - [ ] Redis integration (production)
  
- [ ] Frontend optimization
  - [ ] Next.js Image component for logos
  - [ ] Static page generation where possible
  - [ ] Client-side data caching (React Query)

### Testing

- [ ] Backend tests
  - [ ] Model tests (save/validation)
  - [ ] API endpoint tests
  - [ ] Ingestion command tests
  
- [ ] Frontend tests
  - [ ] Component tests (Jest + React Testing Library)
  - [ ] API client tests
  - [ ] E2E tests (Playwright)

## 🚀 PRODUCTION DEPLOYMENT

### Backend (Django)

- [ ] PostgreSQL migration
  - [ ] Update `DATABASES` in settings
  - [ ] Run migrations on production DB
  
- [ ] Environment hardening
  - [ ] Set `DEBUG=False`
  - [ ] Generate strong `SECRET_KEY`
  - [ ] Configure `ALLOWED_HOSTS`
  - [ ] Set up HTTPS
  
- [ ] Deploy to hosting
  - [ ] **Option 1: Render**
    - [ ] Create Web Service
    - [ ] Add PostgreSQL database
    - [ ] Set environment variables
    - [ ] Deploy
  - [ ] **Option 2: Fly.io**
    - [ ] `flyctl launch`
    - [ ] Add PostgreSQL
    - [ ] Deploy
  - [ ] **Option 3: DigitalOcean App Platform**
    - [ ] Connect GitHub
    - [ ] Add Managed Database
    - [ ] Deploy
  
- [ ] Static files
  - [ ] `python manage.py collectstatic`
  - [ ] Serve via CDN (optional: AWS S3 + CloudFront)
  
- [ ] Automated ingestion
  - [ ] Set up daily cron job
  - [ ] Monitor ingestion logs

### Frontend (Next.js)

- [ ] **Deploy to Vercel**
  - [ ] Connect GitHub repo
  - [ ] Set `NEXT_PUBLIC_API_URL`
  - [ ] Deploy
  - [ ] Custom domain (optional)
  
- [ ] Performance
  - [ ] Enable Next.js Image Optimization
  - [ ] Set up Vercel Analytics
  - [ ] Monitor Core Web Vitals
  
- [ ] SEO
  - [ ] Metadata for all pages
  - [ ] OpenGraph tags
  - [ ] Sitemap generation

## 📈 POST-MVP ENHANCEMENTS

### Features

- [ ] User accounts (optional)
  - [ ] Django authentication
  - [ ] Save favorite teams
  - [ ] Custom dashboards
  
- [ ] Advanced filtering
  - [ ] Date range selector
  - [ ] Multi-conference filter
  - [ ] Custom metric thresholds
  
- [ ] Data export
  - [ ] Export rankings as CSV
  - [ ] Export team stats as JSON
  - [ ] API pagination for large datasets
  
- [ ] Mobile optimization
  - [ ] Responsive tables
  - [ ] Touch-friendly visualizations
  - [ ] Mobile navigation
  
- [ ] Dark mode
  - [ ] Tailwind dark mode classes
  - [ ] User preference toggle
  - [ ] Persist preference

### Analytics

- [ ] Usage tracking
  - [ ] Google Analytics 4
  - [ ] Track popular teams/pages
  
- [ ] Performance monitoring
  - [ ] Sentry for error tracking
  - [ ] Backend logging (Loguru)
  - [ ] Database query optimization

### Documentation

- [ ] User guide
  - [ ] How to use the dashboard
  - [ ] Interpretation of metrics
  
- [ ] Developer docs
  - [ ] API reference (OpenAPI/Swagger)
  - [ ] Contributing guide
  - [ ] Code of conduct

## ✅ SUCCESS CRITERIA

- [x] Backend API serves all core endpoints
- [x] Frontend fetches data from API (no static JSON)
- [x] Rankings page fully functional
- [x] Team profile page fully functional
- [x] Matchup tool functional
- [ ] At least 1 visualization implemented
- [ ] Data successfully ingested from CSVs
- [ ] Documentation complete for local setup
- [ ] Deployment guide tested

## 🎯 CURRENT PRIORITY

1. ✅ Complete MVP pages (rankings, team, matchup) - DONE
2. 🚧 Implement Trapezoid of Excellence - NEXT
3. Test full workflow: ingest data → API → frontend
4. Deploy to staging (Render + Vercel)
5. Add remaining visualizations

---

**Last Updated:** 2026-02-11

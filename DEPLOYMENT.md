# 🚀 Deployment Guide - CBB Analytics

Complete guide for deploying your Django + Next.js app to production.

## 📋 Pre-Deployment Checklist

- [ ] Backend tests passing
- [ ] Frontend builds without errors
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] Static files configured
- [ ] CORS settings correct
- [ ] API endpoints tested
- [ ] Data ingestion working

---

## 🗄️ Backend Deployment (Django)

### Option 1: Render (Recommended)

**Why Render?**
- Free PostgreSQL database
- Auto-deploys from GitHub
- Free SSL certificates
- Simple environment variable management

#### Steps:

1. **Prepare Repository**

```powershell
# Make sure backend/requirements.txt is up to date
cd backend
pip freeze > requirements.txt

# Add Render-specific files if needed
```

2. **Create Render Account**
- Go to https://render.com
- Sign up / log in with GitHub

3. **Create PostgreSQL Database**
- Click "New +" → "PostgreSQL"
- Name: `cbb-analytics-db`
- Region: Choose closest to users
- Plan: Free (or paid for production)
- Click "Create Database"
- **Copy the Internal Database URL** (starts with `postgres://`)

4. **Create Web Service**
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Root Directory: `backend`
- Build Command:
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```
- Start Command:
```bash
gunicorn config.wsgi:application
```

5. **Set Environment Variables**

In Render dashboard → Environment:

```env
PYTHON_VERSION=3.11.0
DEBUG=False
SECRET_KEY=<generate-random-50-char-string>
DATABASE_URL=<paste-internal-database-url>
ALLOWED_HOSTS=your-app.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

Generate secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

6. **Deploy**
- Click "Create Web Service"
- Wait for build (5-10 minutes first time)
- Your API will be live at `https://your-app.onrender.com`

7. **Create Superuser**

Once deployed, use Render Shell:
- Go to your service → "Shell"
```bash
python manage.py createsuperuser
```

8. **Ingest Data**

Run one-time ingestion:
```bash
python manage.py ingest_data --season 2026
```

**Setup Daily Auto-Ingestion:**
- Add a Render Cron Job
- Schedule: `0 6 * * *` (6 AM daily)
- Command: `python manage.py ingest_data --season 2026`

---

### Option 2: Fly.io

**Why Fly.io?**
- Fast global deployments
- Free tier includes Postgres
- Great CLI experience

#### Steps:

1. **Install Fly CLI**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

2. **Login**
```powershell
fly auth login
```

3. **Launch App**
```powershell
cd backend
fly launch
```

Follow prompts:
- App name: `cbb-analytics-backend`
- Region: Choose closest
- Postgres: Yes (select free tier)
- Deploy now: No (we need to configure first)

4. **Configure**

Edit `fly.toml`:
```toml
[env]
  PORT = "8000"

[deploy]
  release_command = "python manage.py migrate && python manage.py collectstatic --noinput"
```

Set secrets:
```powershell
fly secrets set SECRET_KEY="your-secret-key"
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS="cbb-analytics-backend.fly.dev"
```

5. **Deploy**
```powershell
fly deploy
```

6. **Access Shell**
```powershell
fly ssh console
python manage.py createsuperuser
python manage.py ingest_data --season 2026
```

---

### Option 3: DigitalOcean App Platform

1. **Create App**
- Go to DigitalOcean → Apps
- Create App from GitHub
- Select repository

2. **Configure Backend**
- Type: Web Service
- Build Command: `pip install -r requirements.txt`
- Run Command: `gunicorn config.wsgi:application`

3. **Add Database**
- Add PostgreSQL component
- Link to app

4. **Environment Variables**
Set in App Platform dashboard

5. **Deploy**

---

## 🎨 Frontend Deployment (Next.js)

### Option 1: Vercel (Recommended)

**Why Vercel?**
- Made by Next.js creators
- Zero-config deployments
- Free SSL, CDN, automatic HTTPS
- Excellent performance

#### Steps:

1. **Prepare Repository**

```powershell
cd frontend

# Test production build locally
npm run build
npm start
```

Fix any build errors before deploying.

2. **Create Vercel Account**
- Go to https://vercel.com
- Sign up with GitHub

3. **Import Project**
- Click "Add New..." → "Project"
- Import your GitHub repository
- Root Directory: Leave empty or set to `frontend` if monorepo

4. **Configure Build Settings**

Vercel should auto-detect Next.js:
- Framework Preset: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

If using monorepo:
- Root Directory: `frontend`

5. **Set Environment Variables**

In Vercel dashboard → Settings → Environment Variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
```

**Important:** Use your deployed backend URL, not localhost!

6. **Deploy**
- Click "Deploy"
- Wait 2-3 minutes
- Your site is live at `https://your-project.vercel.app`

7. **Custom Domain (Optional)**
- Go to Settings → Domains
- Add your custom domain
- Update DNS records as instructed

8. **Automatic Deployments**

Every push to `main` branch auto-deploys!
- Pull requests get preview URLs
- Production deploys on merge

---

### Option 2: Netlify

1. **Connect GitHub**
- Go to https://netlify.com
- Import repository

2. **Build Settings**
```
Build command: npm run build
Publish directory: .next
```

3. **Environment Variables**
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
```

4. **Deploy**

---

### Option 3: Self-Hosted (Docker)

**Dockerfile:**
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://your-backend.com/api
```

Build and run:
```bash
docker compose up --build
```

---

## 🔐 Security Checklist

### Backend

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] `ALLOWED_HOSTS` set correctly
- [ ] HTTPS enabled (SSL certificate)
- [ ] CORS restricted to frontend domain only
- [ ] Database credentials secure (not in git)
- [ ] Admin panel has strong password
- [ ] Rate limiting enabled (optional: django-ratelimit)

### Frontend

- [ ] No API keys in client-side code
- [ ] HTTPS enabled
- [ ] Environment variables use `NEXT_PUBLIC_` prefix
- [ ] CSP headers configured (optional)

---

## 📊 Post-Deployment

### 1. Verify Deployment

**Backend:**
```bash
curl https://your-backend.onrender.com/api/seasons/
```

**Frontend:**
Visit: https://your-frontend.vercel.app

### 2. Setup Monitoring

**Backend (Render):**
- Dashboard shows logs, metrics, restarts

**Frontend (Vercel):**
- Vercel Analytics auto-enabled
- Monitor Core Web Vitals

### 3. Setup Automated Data Updates

**Option A: Render Cron Job**
- Schedule: `0 6 * * *` (daily at 6 AM)
- Command: `python manage.py ingest_data --season 2026`

**Option B: GitHub Actions**
```yaml
name: Daily Data Ingestion
on:
  schedule:
    - cron: '0 6 * * *'
jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Ingestion
        run: |
          curl -X POST https://your-backend.com/api/trigger-ingestion/
```

### 4. Setup Error Tracking

**Sentry (Optional):**
```bash
pip install sentry-sdk
```

In `settings.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          # Render auto-deploys on push
          
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          # Vercel auto-deploys on push
```

---

## 🐛 Troubleshooting

### Backend Issues

**"Application error" on Render**
- Check Logs in Render dashboard
- Verify `DATABASE_URL` is set
- Run migrations: `python manage.py migrate`

**"Static files not found"**
```bash
python manage.py collectstatic --noinput
```

**Database connection fails**
- Use Internal Database URL (not External)
- Check `DATABASE_URL` format

### Frontend Issues

**"API calls failing"**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS in Django backend
- Test API directly: `curl https://backend.com/api/seasons/`

**Build fails on Vercel**
- Check build logs
- Test locally: `npm run build`
- Verify all dependencies in `package.json`

---

## 📈 Scaling

### Backend

**Render:**
- Upgrade to Starter plan ($7/mo)
- Add Redis for caching
- Enable auto-scaling

**Database:**
- Upgrade PostgreSQL tier
- Add connection pooling (PgBouncer)
- Create read replicas

### Frontend

**Vercel:**
- Free tier handles most traffic
- Pro plan for teams ($20/mo/user)
- Enterprise for custom requirements

**CDN:**
- Vercel includes global CDN
- Add custom edge caching rules

---

## ✅ Deployment Complete!

Your app should now be live:
- **Frontend:** https://your-app.vercel.app
- **Backend API:** https://your-backend.onrender.com/api
- **Admin:** https://your-backend.onrender.com/admin

**Next steps:**
1. Set up custom domain
2. Enable monitoring/analytics
3. Schedule data updates
4. Share with users!

---

Questions? Check component READMEs or open an issue.

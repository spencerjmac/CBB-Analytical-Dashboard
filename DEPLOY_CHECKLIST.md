# 🚀 Quick Deploy Checklist

Use this checklist before your first deployment to ensure everything works.

## ✅ Pre-Deployment

### 1. Install Dependencies
```bash
cd web
npm install
```
- [ ] No errors during npm install
- [ ] `node_modules` folder created

### 2. Prepare Data Files

```bash
# Check CSV files exist
ls "../KenPom Data/kenpom_tableau.csv"
ls "../Bart Torvik/torvik_tableau.csv"  
ls "../CBB Analytics/cbb_analytics_tableau_cleaned.csv"
```
- [ ] All 3 CSV files exist and have data
- [ ] CSV files are from current season (2025-26)

### 3. Build Data Pipeline

```bash
cd ../scripts
npx tsx build-data.ts
```
- [ ] Script runs without errors
- [ ] `web/public/data/teams.json` is created
- [ ] teams.json contains 365 teams (check file size > 500KB)
- [ ] Spot-check: Michigan, Duke, Kansas in the file

### 4. Copy Team Logos

```bash
# From project root
cp "College Logos/output/logos"/* "web/public/logos/"
```
- [ ] 365 PNG files copied to `web/public/logos/`
- [ ] Filenames match team slugs (e.g., `michigan.png`)
- [ ] default.svg exists as fallback

### 5. Expand Team Name Map

Edit `scripts/team-name-map.json`:
- [ ] Add all 365 teams (currently has ~20)
- [ ] Use team names from CSVs
- [ ] Create slugs (lowercase, hyphens)
- [ ] Add common aliases

**Quick way to generate:**
```bash
# Extract team names from CSVs
cd "../Bart Torvik"
python -c "import pandas as pd; df = pd.read_csv('torvik_tableau.csv'); print(df['team_name'].unique())"
```

## ✅ Local Testing

### 6. Start Dev Server

```bash
cd web
npm run dev
```
- [ ] Server starts on http://localhost:3000
- [ ] No compilation errors
- [ ] No missing module errors

### 7. Test Home Page
Visit: http://localhost:3000
- [ ] Page loads without errors
- [ ] Navigation bar displays
- [ ] Feature cards render
- [ ] Footer shows data sources

### 8. Test Rankings
Visit: http://localhost:3000/rankings
- [ ] Table displays 365 teams
- [ ] Search works (try "Michigan")
- [ ] Conference filter works
- [ ] Sorting works (click headers)
- [ ] Team logos display (or default.svg)

### 9. Test Team Pages
Visit: http://localhost:3000/team/michigan
- [ ] Page loads
- [ ] Team header shows logo, name, record
- [ ] All 5 tabs work
- [ ] Stats display correctly
- [ ] Back button works

Try 5 random teams:
- [ ] http://localhost:3000/team/duke
- [ ] http://localhost:3000/team/kansas
- [ ] http://localhost:3000/team/gonzaga
- [ ] http://localhost:3000/team/kentucky
- [ ] http://localhost:3000/team/north-carolina

### 10. Test Matchup Tool
Visit: http://localhost:3000/matchup
- [ ] Page loads
- [ ] Team selectors work (search + select)
- [ ] Can select 2 different teams
- [ ] Location toggle works (neutral/home/away)
- [ ] Analysis displays correctly
- [ ] Four Factor edges calculate

### 11. Test Glossary
Visit: http://localhost:3000/glossary
- [ ] Page loads
- [ ] 20+ metrics display
- [ ] LaTeX formulas render (no raw \\text{})
- [ ] Search works
- [ ] Category filter works

### 12. Test About
Visit: http://localhost:3000/about
- [ ] Page loads
- [ ] Last Updated shows correct date
- [ ] Team count shows 365
- [ ] All sections render

### 13. Test Visualizations
Visit: http://localhost:3000/viz/trapezoid
- [ ] Chart renders
- [ ] 365 teams plotted
- [ ] Trapezoid polygon displays
- [ ] Tooltip shows on hover
- [ ] Click navigates to team page

### 14. Test Error Pages
- [ ] http://localhost:3000/not-a-page → Shows 404
- [ ] http://localhost:3000/team/fake-team → Team not found

### 15. Test Mobile
- [ ] Resize browser to mobile width
- [ ] Navigation still works
- [ ] Tables scroll horizontally
- [ ] All pages render

## ✅ Production Build

### 16. Build for Production

```bash
npm run build
```
- [ ] Build completes without errors
- [ ] No TypeScript errors
- [ ] No missing dependencies
- [ ] `.next` folder created

### 17. Test Production Build Locally

```bash
npm start
```
- [ ] Server starts on http://localhost:3000
- [ ] All pages load
- [ ] No console errors

## ✅ Deploy to Vercel

### 18. Connect to Vercel
- [ ] GitHub repo pushed
- [ ] Connected to Vercel account
- [ ] Imported project

### 19. Configure Vercel
- [ ] Root directory: `web`
- [ ] Build command: `npm run build`
- [ ] Output directory: `.next`
- [ ] Node version: 18.x or 20.x

### 20. Deploy
- [ ] First deploy completes
- [ ] No build errors
- [ ] Site is live

### 21. Verify Production
Visit your Vercel URL:
- [ ] Home page loads
- [ ] Rankings work (365 teams)
- [ ] Team pages work
- [ ] Matchup tool works
- [ ] Glossary formulas render
- [ ] Trapezoid displays
- [ ] Mobile responsive

## 🎉 Post-Deployment

### 22. Set Up Auto-Deploy
- [ ] Connect GitHub branch to Vercel
- [ ] Enable auto-deploy on push
- [ ] Test: Make small change, push, verify auto-deploy

### 23. Monitor
- [ ] Check Vercel analytics
- [ ] Check for runtime errors
- [ ] Verify data freshness

### 24. Share
- [ ] Add custom domain (optional)
- [ ] Share URL with users
- [ ] Gather feedback

---

## 🔄 Daily Update Workflow

Once deployed, update data daily:

```bash
# 1. Scrape fresh data (Python)
cd "KenPom Data" && python main.py && python export_to_tableau.py
cd "../Bart Torvik" && python export_to_tableau.py
cd "../CBB Analytics" && python scrape_cbb_analytics_clean.py

# 2. Rebuild web data
cd ../scripts && npx tsx build-data.ts

# 3. Commit and push (triggers auto-deploy)
cd ..
git add web/public/data/teams.json
git commit -m "Update data: $(date +%Y-%m-%d)"
git push
```

Vercel will automatically rebuild and deploy! ✨

---

## 🆘 Troubleshooting

### Data pipeline fails
- Check CSV files exist and have data
- Verify team name mappings
- Check TypeScript errors: `npx tsc --noEmit`

### Build fails
- Run `npm install` again
- Clear `.next`: `rm -rf .next`
- Check Node version: `node -v` (need 18+)

### Pages show "undefined"
- Verify teams.json was generated
- Check data structure matches types
- Look for null/missing fields

### Charts don't render
- Check browser console for errors
- Verify echarts installed: `npm list echarts`
- Check data format for chart

### Formulas don't render
- Verify katex CSS imported in globals.css
- Check LaTeX syntax in metrics.ts
- Test in browser console: `window.katex`

---

**Ready to ship! 🚀**

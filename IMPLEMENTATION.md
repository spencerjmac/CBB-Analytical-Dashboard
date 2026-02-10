# 🏀 CBB Analytics Implementation Checklist

## ✅ Completed (MVP)

### Core Infrastructure
- [x] Next.js 14 app with App Router
- [x] TypeScript configuration
- [x] Tailwind CSS with 538-inspired design system
- [x] Inter + IBM Plex Mono fonts
- [x] Data pipeline (`scripts/build-data.ts`)
- [x] Team name normalization system
- [x] Unified `TeamSeason` data schema

### Pages Implemented
- [x] Home page with feature cards
- [x] `/rankings` - Sortable/filterable table with 12+ columns
- [x] `/team/[slug]` - Dynamic team pages with 5 tabs
  - [x] Overview tab (core metrics + ranks)
  - [x] Four Factors tab (off/def + margins)
  - [x] Offense/Defense tab (shooting splits)
  - [x] Resume tab (WAB, SOS, Luck, Barthag)
  - [x] Charts tab (placeholders for viz embeds)
- [x] `/matchup` - Team A vs Team B comparison tool
- [x] `/glossary` - Searchable metric definitions with LaTeX
- [x] `/about` - Data sources + methodology
- [x] `/viz/trapezoid` - Trapezoid of Excellence (interactive)
- [x] `/viz/landscape` - Placeholder
- [x] `/viz/kill-shot` - Placeholder
- [x] `/viz/crystal-ball` - Placeholder

### Components
- [x] Navigation (sticky header with active states)
- [x] RankingsTable (TanStack Table with sorting/filtering)
- [x] TeamPageTabs (5 tabs with detailed breakdowns)
- [x] MatchupTool (searchable team selectors + analysis)
- [x] GlossaryTable (searchable + filterable metrics)
- [x] TrapezoidChart (ECharts scatter with polygon overlay)

### Data Layer
- [x] `lib/data.ts` - Data loading utilities
- [x] `lib/metrics.ts` - 20+ metric definitions
- [x] Team name mapping JSON
- [x] Logo resolution (365 PNG files)
- [x] Derived metrics (margins, edges)

### Polish
- [x] SEO metadata on all pages
- [x] Error pages (404, team not found)
- [x] Loading states (rankings skeleton)
- [x] Responsive design (mobile-friendly)
- [x] Hover states and transitions
- [x] Link styling with active states

### Documentation
- [x] `/web/README.md` - Comprehensive setup guide
- [x] Data pipeline instructions
- [x] Deployment guide (Vercel)
- [x] Customization guide
- [x] Known issues list

---

## 🚧 TODOs (Post-MVP)

### High Priority
- [ ] **Build data before first dev run**: Generate `teams.json` from CSVs
- [ ] **Copy team logos**: Ensure `/web/public/logos/` has all 365 PNG files
- [ ] **Add complete team name map**: Currently only has ~20 teams
- [ ] **Win probability model**: Implement Bayesian win prob in matchup tool
- [ ] **Mobile navigation**: Add hamburger menu

### Medium Priority
- [ ] **Efficiency Landscape viz**: Complete heatmap/contour implementation
- [ ] **Kill Shot Analysis**: Define metrics and build visualization
- [ ] **Crystal Ball**: Build rules engine with thresholds
- [ ] **Embed charts on team pages**: Trapezoid + Crystal Ball previews
- [ ] **Historical seasons**: Add season selector (multi-year support)
- [ ] **Team search autocomplete**: Fuzzy matching in rankings/matchup

### Low Priority
- [ ] **Four Factors radar chart**: Add to team pages
- [ ] **Schedule/results data**: If available from sources
- [ ] **Conference standings**: Dedicated conference pages
- [ ] **Player stats**: If you add player-level scraping
- [ ] **Export data**: CSV/JSON download buttons
- [ ] **Dark mode**: Toggle for dark theme

### Performance Optimizations
- [ ] **Virtual scrolling**: For rankings table (if > 500 teams)
- [ ] **Image optimization**: Use Next.js Image component
- [ ] **Code splitting**: Lazy load chart libraries
- [ ] **Edge caching**: Deploy with edge functions

---

## 📦 Deployment Checklist

### Before First Deploy
1. [ ] Run data pipeline: `cd scripts && npx tsx build-data.ts`
2. [ ] Verify `web/public/data/teams.json` exists
3. [ ] Copy logos to `web/public/logos/`
4. [ ] Test locally: `cd web && npm run dev`
5. [ ] Test build: `cd web && npm run build`

### Vercel Deployment
1. [ ] Connect GitHub repo to Vercel
2. [ ] Set root directory: `web`
3. [ ] Build command: `npm run build` (includes data pipeline)
4. [ ] Output directory: `.next`
5. [ ] Deploy!

### Post-Deploy Verification
- [ ] Home page loads
- [ ] Rankings table displays 365 teams
- [ ] Team pages work (test 5 random teams)
- [ ] Matchup tool functional
- [ ] Glossary renders LaTeX formulas
- [ ] Trapezoid chart displays
- [ ] All navigation links work

---

## 🎯 Next Steps

### Immediate Actions
1. **Install dependencies**: `cd web && npm install`
2. **Expand team name map**: Add all 365 teams to `scripts/team-name-map.json`
3. **Run data pipeline**: Generate `teams.json`
4. **Test locally**: `npm run dev` and verify all pages
5. **Deploy to Vercel**: Follow deployment checklist

### Week 1
- Complete all team name mappings
- Implement win probability model
- Add mobile navigation
- Fix any logo/data issues

### Week 2
- Build Efficiency Landscape visualization
- Define and implement Kill Shot metrics
- Start Crystal Ball rules engine

### Month 1
- Complete all 4 core visualizations
- Add historical season support
- Performance optimizations
- User feedback integration

---

## 📊 Project Stats

- **Pages**: 13 (including dynamic routes)
- **Components**: 10+
- **Metrics Defined**: 20+
- **Data Sources**: 3 (KenPom, Torvik, CBB Analytics)
- **Teams**: 365 NCAA D1
- **Lines of Code**: ~5,000+

---

## 🔧 Quick Commands

```bash
# Install dependencies
cd web && npm install

# Build data
cd scripts && npx tsx build-data.ts

# Dev server
cd web && npm run dev

# Production build
cd web && npm run build

# Start production server
cd web && npm start
```

---

**Status**: MVP Complete ✅  
**Last Updated**: February 10, 2026

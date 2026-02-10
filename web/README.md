# CBB Analytics Web Application

A production-ready college basketball analytics web application built with Next.js, featuring KenPom/Torvik-style UX with original design and advanced metrics.

## 🏀 Features

- **Team Rankings**: Sortable/filterable table with 365+ D1 teams
- **Team Profiles**: Detailed pages with tabs (Overview, Four Factors, Off/Def, Resume, Charts)
- **Matchup Tool**: Head-to-head comparison with efficiency projections
- **Visualizations**: Interactive charts including Trapezoid of Excellence
- **Glossary**: Comprehensive metric definitions with LaTeX formulas
- **About**: Data sources, methodology, and update information

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or 20+
- npm or yarn
- Python 3.14+ (for data pipeline)

### Installation

```bash
cd web
npm install
```

### Build Data

Before running the app, generate the unified data file:

```bash
# From the root project directory
cd scripts
npx tsx build-data.ts
```

This will:
1. Read KenPom, Torvik, and CBB Analytics CSVs
2. Normalize team names
3. Merge data sources
4. Calculate derived metrics
5. Output `web/public/data/teams.json`

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

The build process automatically runs the data pipeline (`build:data` script).

## 📂 Project Structure

```
web/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout with navigation
│   │   ├── page.tsx           # Home page
│   │   ├── rankings/          # Rankings page
│   │   ├── team/[slug]/       # Dynamic team pages
│   │   ├── matchup/           # Matchup comparison tool
│   │   ├── glossary/          # Metrics glossary
│   │   ├── about/             # About/methodology page
│   │   └── viz/               # Visualization pages
│   │       ├── trapezoid/
│   │       ├── landscape/
│   │       ├── kill-shot/
│   │       └── crystal-ball/
│   ├── components/            # React components
│   │   ├── Navigation.tsx
│   │   ├── RankingsTable.tsx
│   │   ├── TeamPageTabs.tsx
│   │   ├── MatchupTool.tsx
│   │   ├── GlossaryTable.tsx
│   │   └── TrapezoidChart.tsx
│   ├── lib/                   # Utilities
│   │   ├── data.ts           # Data loading functions
│   │   └── metrics.ts        # Metric definitions
│   └── types/                # TypeScript types
│       └── index.ts
├── public/
│   ├── data/
│   │   └── teams.json        # Unified dataset (generated)
│   └── logos/                # Team logos (365 PNG files)
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## 🎨 Design System

### Colors

- **Primary**: #ED713A (538 Orange)
- **Secondary**: #30A2DA (Blue)
- **Success**: #6D904F (Green)
- **Warning**: #E5AE38 (Yellow)
- **Neutral**: #8B8B8B (Gray)

### Fonts

- **UI/Body**: Inter (Google Fonts)
- **Numbers/Stats**: IBM Plex Mono (Google Fonts)

### Chart Palette

10-color categorical palette for visualizations (chart-1 through chart-10 in Tailwind config).

## 📊 Data Pipeline

### Input Files

Located in parent directories:
- `../KenPom Data/kenpom_tableau.csv`
- `../Bart Torvik/torvik_tableau.csv`
- `../CBB Analytics/cbb_analytics_tableau_cleaned.csv`

### Team Name Normalization

Edit `scripts/team-name-map.json` to add or fix team name mappings:

```json
{
  "Michigan": {
    "slug": "michigan",
    "display": "Michigan",
    "aliases": ["Michigan", "Mich"]
  }
}
```

### Data Schema

The unified `TeamSeason` interface includes:
- Core ratings (AdjEM, AdjO, AdjD, Tempo)
- Four Factors (eFG%, TOV%, ORB%, FTR) for offense and defense
- Calculated margins (eFG margin, TOV edge, etc.)
- Shooting splits (2P%, 3P%, 3P Rate)
- Resume metrics (WAB, SOS, Luck, Barthag)
- Source tracking (which datasets contributed data)

### Running the Pipeline

```bash
# Standalone
cd scripts
npx tsx build-data.ts

# Automatically during build
cd web
npm run build
```

## 🚀 Deployment

### Vercel (Recommended)

1. Connect your GitHub repo to Vercel
2. Set build command: `npm run build`
3. Set output directory: `.next`
4. Deploy!

Vercel will automatically:
- Run the data pipeline
- Build the Next.js app
- Deploy as static site (or with SSR if needed)

### Manual Static Export

```bash
npm run build
# Outputs to /out directory
# Upload /out to any static host (Netlify, GitHub Pages, S3, etc.)
```

### Environment Variables

None required for basic operation. The app reads from static JSON files.

## 📈 Adding New Visualizations

1. Create component in `src/components/` (e.g., `MyChart.tsx`)
2. Use Apache ECharts via `echarts-for-react` or raw `echarts`
3. Create page in `src/app/viz/my-chart/page.tsx`
4. Import component and pass `teams` data
5. Add navigation link in `src/components/Navigation.tsx`

Example:

```tsx
import ReactECharts from 'echarts-for-react';

export default function MyChart({ teams }: { teams: TeamSeason[] }) {
  const option = {
    // ECharts configuration
  };
  
  return <ReactECharts option={option} />;
}
```

## 🧪 Adding New Metrics

1. Update `src/types/index.ts` to add field to `TeamSeason`
2. Update `scripts/build-data.ts` to calculate metric from CSV data
3. Add definition to `src/lib/metrics.ts`
4. Use in tables/charts/pages as needed

## 🔧 Customization

### Changing Colors

Edit `web/tailwind.config.js`:

```js
colors: {
  primary: {
    DEFAULT: '#ED713A', // Change to your color
  },
}
```

### Changing Fonts

Edit `web/src/app/layout.tsx`:

```ts
import { YourFont } from 'next/font/google';
```

### Modifying Trapezoid Boundaries

Edit `src/components/TrapezoidChart.tsx`:

```ts
const trapezoidPoints = [
  [62, 15],   // Your coordinates
  // ...
];
```

## 📝 Known Issues & TODOs

- [ ] **Win probability model**: Add Bayesian win probability calculation to matchup tool
- [ ] **Mobile navigation**: Add hamburger menu for mobile devices
- [ ] **Logo fallbacks**: Some team logos may be missing (uses default.png)
- [ ] **Efficiency Landscape**: Complete contour/heatmap implementation
- [ ] **Kill Shot Analysis**: Define and implement kill shot metrics
- [ ] **Crystal Ball**: Build rules engine with configurable thresholds
- [ ] **Team search autocomplete**: Add fuzzy matching for better UX
- [ ] **Historical seasons**: Add season selector (currently 2025-26 only)

## 🤝 Contributing

This is a personal project, but contributions are welcome:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test locally (`npm run dev`)
5. Submit a pull request

## 📜 License

For educational and personal use. Not affiliated with KenPom.com or barttorvik.com.

## 🔗 Links

- **Data Sources**: KenPom.com, barttorvik.com, cbbanalytics.com
- **Tech Stack**: Next.js 14, TypeScript, Tailwind CSS, Apache ECharts, TanStack Table
- **Deployment**: Vercel (recommended)

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Last Updated**: February 2026  
**Version**: 1.0.0

# CBB Analytics - Next.js Frontend

Modern, production-ready frontend for College Basketball Analytics built with Next.js 14, TypeScript, and Tailwind CSS.

## 🏀 Features

- **Team Rankings** - Sortable/filterable table with 365 D1 teams
- **Team Profiles** - Detailed stats with tabs (Overview, Four Factors, Splits, Resume)
- **Matchup Tool** - Head-to-head comparison with win probabilities
- **Visualizations** - Interactive charts (Trapezoid of Excellence, etc.)
- **Glossary** - Searchable metric definitions
- **About** - Data sources and methodology

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or 20+
- npm or yarn
- Django backend running (see `/backend/README.md`)

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

The frontend will proxy API requests to the Django backend at `http://localhost:8000`.

### Build for Production

```bash
npm run build
npm start
```

## 🔧 Configuration

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

For production, set this to your deployed backend URL:

```env
NEXT_PUBLIC_API_URL=https://your-backend.com/api
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── rankings/        # Rankings page
│   │   ├── team/[slug]/     # Dynamic team profile pages
│   │   ├── matchup/         # Matchup tool
│   │   ├── glossary/        # Metrics glossary
│   │   ├── about/           # About page
│   │   └── viz/             # Visualization pages
│   ├── components/          # Reusable React components
│   │   └── Navigation.tsx
│   ├── lib/                 # Utilities
│   │   └── api.ts           # API client (axios)
│   └── types/               # TypeScript types
│       └── index.ts
├── public/                  # Static assets
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## 🎨 Design System

**Colors:**
- Primary: `#ED713A` (Orange)
- Blue: `#30A2DA`
- Green: `#2ECC71`
- Gray scale for backgrounds/text

**Fonts:**
- Sans: Inter
- Mono: IBM Plex Mono (for numbers)

**Styling:**
- Tailwind CSS utility classes
- Custom components in `globals.css`

## 🌐 API Integration

The frontend uses an axios-based API client (`src/lib/api.ts`) to communicate with the Django backend.

### API Client Usage

```typescript
import { api } from '@/lib/api';

// Get rankings
const rankings = await api.getRankings({
  season: 2026,
  sort: 'adj_em',
  dir: 'desc',
  conference: 'B10',
  search: 'michigan'
});

// Get team profile
const profile = await api.getTeamProfile('michigan', 2026);

// Get matchup
const matchup = await api.getMatchup('michigan', 'duke', 'neutral', 2026);
```

## 📊 Pages

### Rankings (`/rankings`)
- Sortable table with all teams
- Filter by conference
- Search by team name
- Click team to view profile

### Team Profile (`/team/[slug]`)
- Overview tab: Core efficiency metrics
- Four Factors tab: Offensive/defensive factors + margins
- Splits tab: Shooting percentages (2P, 3P)
- Resume tab: WAB, SOR, Barthag, Luck, SOS

### Matchup (`/matchup`)
- Enter two teams and site (neutral/home/away)
- Win probabilities via log5 formula
- Predicted margin with home court advantage
- Key edges visualization
- Side-by-side stats comparison

### Visualizations (`/viz/...`)
- `/viz/trapezoid` - Trapezoid of Excellence (in progress)
- More visualizations planned (see implementation checklist)

## 🚢 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.render.com/api
   ```
4. Deploy

### Manual Deployment

```bash
npm run build
npm start
```

The app will run on port 3000 by default.

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
EXPOSE 3000
```

## 🐛 Troubleshooting

**API errors:**
- Ensure Django backend is running
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings in Django (`settings.py`)

**Build errors:**
- Delete `.next` folder and rebuild
- Clear `node_modules` and reinstall

**TypeScript errors:**
- Run `npx tsc --noEmit` to check types
- Ensure types in `src/types/index.ts` match API responses

## 🔮 Future Enhancements

See `/IMPLEMENTATION_CHECKLIST.md` for planned features:
- [ ] Complete Trapezoid of Excellence visualization
- [ ] Efficiency Landscape heatmap
- [ ] Kill Shot graphic on team pages
- [ ] Crystal Ball championship predictor
- [ ] Advanced filtering (date range, custom metrics)
- [ ] Data export (CSV/JSON)
- [ ] Mobile-responsive optimization
- [ ] Dark mode support

## 📝 Contributing

1. Follow TypeScript strict mode
2. Use Tailwind for styling (avoid custom CSS)
3. Test API integration thoroughly
4. Keep components small and reusable

## 📄 License

See root LICENSE file.

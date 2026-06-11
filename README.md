# Match Forecast / 赛果先知

A bilingual 2026 World Cup entertainment forecast. The project uses versioned CSV files and does not require a database.

> Forecasts are for football data research and entertainment only. They are not betting or investment advice.

## Data flow

```text
OpenFootball CC0 schedule + Wikidata CC0 team metadata
                         +
         manually maintained CSV statistics
                         ↓
             Python validation/model
                         ↓
          web/data/predictions.json
                         ↓
                   Next.js site
```

Source files live in `data/`:

- `matches.csv`: schedule and source/license.
- `teams.csv`: bilingual team metadata and Wikidata links.
- `team_metrics.csv`: recent team aggregates.
- `player_stats.csv`: rolling 365-day player statistics.
- `reviews.csv`: frozen post-match review snapshots.

Values marked with a `manual://` source are editorial inputs. Replace them with verified values and public source URLs before presenting the forecast as based on current real-world statistics.

## Update predictions

Edit the CSV files, then run:

```powershell
npm run generate:data
npm test
npm run build
```

The generator validates duplicate IDs, team references, squad values, minutes and probability output before writing `web/data/predictions.json`.

## Local site

```powershell
npm --prefix web install
npm run dev
```

Open `http://localhost:3000`. English is the default language; Chinese is available at `/zh`.

## Vercel

Import the GitHub repository and configure:

```text
Framework Preset: Next.js
Root Directory: web
```

No database or environment variables are required. Commit the generated JSON whenever CSV data changes; pushing to `main` triggers a new Vercel deployment.

## Data and rights

- OpenFootball World Cup data: CC0-1.0.
- Wikidata structured data: CC0-1.0.
- Do not copy protected logos, player photos, or full commercial datasets.
- Keep a source URL for every externally verified row.
- The site is independent and is not affiliated with FIFA or any national association.

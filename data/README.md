# Data files

- `matches.csv`: World Cup schedule/results sourced from OpenFootball (CC0).
- `teams.csv`: team identifiers and bilingual labels, linked to Wikidata (CC0).
- `team_metrics.csv`: manually curated recent team aggregates.
- `player_stats.csv`: manually maintained rolling 365-day player aggregates with a source column.
- `reviews.csv`: frozen historical prediction snapshots and post-match analysis.

Rows using `manual://` are editorial inputs, not claims that the value came from an external licensed database. Replace them with verified statistics and a public source URL before treating a forecast as production data.

Run `python predictor/scripts/generate_predictions.py` after editing CSV files. The script validates the inputs and atomically writes `web/data/predictions.json`.

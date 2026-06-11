from __future__ import annotations

from datetime import datetime, timezone

from .model import predict_match
from .repository import PredictionRepository
from .sources.base import MatchSource
from .validation import validate_squad

MODEL_VERSION = "wc-poisson-1.1.0"


def run_daily(source: MatchSource, repository: PredictionRepository, data_version: str) -> int:
    run_id = repository.start_run(source.__class__.__name__)
    published = 0
    try:
        for match in source.upcoming_matches():
            validate_squad(match.home.squad)
            validate_squad(match.away.squad)
            result = predict_match(match)
            payload = {
                "id": match.match_id,
                "kickoff": match.kickoff.isoformat(),
                "homeTeam": {"code": match.home.code, "name": match.home.name},
                "awayTeam": {"code": match.away.code, "name": match.away.name},
                "homeWin": result.home_win,
                "draw": result.draw,
                "awayWin": result.away_win,
                "expectedHomeGoals": result.expected_home_goals,
                "expectedAwayGoals": result.expected_away_goals,
                "likelyScore": result.likely_score,
                "topScores": result.top_scores,
                "confidence": result.confidence,
                "factors": result.factors,
                "modelVersion": MODEL_VERSION,
                "dataVersion": data_version,
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            }
            repository.publish(f"{match.match_id}:{MODEL_VERSION}:{data_version}", payload, MODEL_VERSION, data_version)
            published += 1
        repository.finish_run(run_id, "succeeded", {"published": published})
        return published
    except Exception as error:
        # Existing published rows are untouched when validation or ingestion fails.
        repository.finish_run(run_id, "failed", {"error": str(error), "published": published})
        raise

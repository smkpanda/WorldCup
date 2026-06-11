from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .domain import MatchContext
from .metrics import brier_score, log_loss
from .model import predict_match


@dataclass(frozen=True)
class HistoricalMatch:
    context: MatchContext
    home_goals: int
    away_goals: int


def time_split(matches: Iterable[HistoricalMatch], cutoff: datetime) -> tuple[list[HistoricalMatch], list[HistoricalMatch]]:
    ordered = sorted(matches, key=lambda item: item.context.kickoff)
    return (
        [item for item in ordered if item.context.kickoff < cutoff],
        [item for item in ordered if item.context.kickoff >= cutoff],
    )


def evaluate(matches: Iterable[HistoricalMatch]) -> dict[str, float]:
    losses: list[float] = []
    briers: list[float] = []
    score_errors: list[float] = []
    for item in matches:
        result = predict_match(item.context)
        probabilities = (result.home_win / 100, result.draw / 100, result.away_win / 100)
        outcome = 0 if item.home_goals > item.away_goals else 1 if item.home_goals == item.away_goals else 2
        losses.append(log_loss(probabilities[outcome]))
        briers.append(brier_score(probabilities, outcome))
        score_errors.append(
            abs(result.expected_home_goals - item.home_goals)
            + abs(result.expected_away_goals - item.away_goals)
        )
    count = len(losses)
    if not count:
        return {"matches": 0, "log_loss": 0, "brier_score": 0, "score_mae": 0}
    return {
        "matches": count,
        "log_loss": sum(losses) / count,
        "brier_score": sum(briers) / count,
        "score_mae": sum(score_errors) / (2 * count),
    }

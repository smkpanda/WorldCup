from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from .domain import MatchContext
from .features import team_features


@dataclass(frozen=True)
class PredictionResult:
    expected_home_goals: float
    expected_away_goals: float
    home_win: float
    draw: float
    away_win: float
    likely_score: str
    top_scores: tuple[dict[str, float | int], ...]
    confidence: float
    factors: tuple[dict[str, float | str], ...]
    score_matrix: tuple[tuple[float, ...], ...]

    def as_dict(self) -> dict:
        return asdict(self)


def poisson_probability(goals: int, expected_goals: float) -> float:
    return math.exp(-expected_goals) * expected_goals**goals / math.factorial(goals)


def poisson_median(expected_goals: float) -> int:
    if expected_goals <= 0:
        return 0
    return max(0, math.floor(expected_goals + 1 / 3 - 0.02 / expected_goals))


def score_matrix(home_xg: float, away_xg: float, max_goals: int = 7) -> tuple[tuple[float, ...], ...]:
    matrix = tuple(
        tuple(poisson_probability(h, home_xg) * poisson_probability(a, away_xg) for a in range(max_goals + 1))
        for h in range(max_goals + 1)
    )
    total = sum(sum(row) for row in matrix)
    return tuple(tuple(value / total for value in row) for row in matrix)


def _expected_goals(own: dict[str, float], opponent: dict[str, float], advantage: float) -> float:
    baseline = 1.28
    signal = (
        0.78 * (own["attack"] - 0.5)
        + 0.52 * (0.5 - opponent["defense"])
        + 0.25 * (own["form"] - opponent["form"])
        + 0.18 * (own["quality"] - opponent["quality"])
        + 0.08 * (own["experience"] - opponent["experience"])
        + 0.05 * (own["rest"] - opponent["rest"])
        + advantage
    )
    return min(3.8, max(0.25, baseline * math.exp(signal)))


def predict_match(match: MatchContext) -> PredictionResult:
    home = team_features(match.home, match.kickoff)
    away = team_features(match.away, match.kickoff)
    home_xg = _expected_goals(home, away, match.venue_home_advantage)
    away_xg = _expected_goals(away, home, 0)
    matrix = score_matrix(home_xg, away_xg)

    home_win = sum(matrix[h][a] for h in range(len(matrix)) for a in range(len(matrix)) if h > a)
    draw = sum(matrix[i][i] for i in range(len(matrix)))
    away_win = 1 - home_win - draw
    scores = sorted(
        ({"home": h, "away": a, "probability": round(matrix[h][a] * 100, 2)} for h in range(len(matrix)) for a in range(len(matrix))),
        key=lambda item: item["probability"],
        reverse=True,
    )
    completeness = (home["completeness"] + away["completeness"]) / 2
    confidence = 55 + 35 * completeness
    factor_names = {
        "form": "近期状态",
        "quality": "阵容质量",
        "experience": "大赛经验",
        "defense": "攻防平衡",
    }
    factors = tuple(
        {
            "label": label,
            "home": round(home[key] * 100),
            "away": round(away[key] * 100),
            "note": "基于预测时点之前的数据计算",
        }
        for key, label in factor_names.items()
    )
    home_percent = round(home_win * 100, 2)
    draw_percent = round(draw * 100, 2)
    away_percent = round(100 - home_percent - draw_percent, 2)
    return PredictionResult(
        expected_home_goals=round(home_xg, 2),
        expected_away_goals=round(away_xg, 2),
        home_win=home_percent,
        draw=draw_percent,
        away_win=away_percent,
        likely_score=f"{poisson_median(home_xg)}-{poisson_median(away_xg)}",
        top_scores=tuple(scores[:3]),
        confidence=round(confidence, 1),
        factors=factors,
        score_matrix=matrix,
    )

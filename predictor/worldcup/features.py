from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from statistics import median

from .domain import PlayerPerformance, Position, SquadPlayer, TeamContext

POSITION_BASELINES = {
    Position.FORWARD: 0.52,
    Position.MIDFIELDER: 0.50,
    Position.DEFENDER: 0.48,
    Position.GOALKEEPER: 0.50,
}


def per90(value: float, minutes: int) -> float:
    return 0.0 if minutes <= 0 else value * 90.0 / minutes


def time_weight(occurred_at: datetime, prediction_at: datetime) -> float:
    age = max(0, (prediction_at - occurred_at).days)
    if age > 365:
        return 0.0
    # Half-life of 120 days; recent matches matter more without hard bucket edges.
    return math.exp(-math.log(2) * age / 120)


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, value))


def player_rating(performance: PlayerPerformance, prediction_at: datetime) -> float:
    if performance.minutes <= 0:
        return POSITION_BASELINES[performance.position]

    p = performance
    if p.position == Position.FORWARD:
        raw = (
            per90(p.goals, p.minutes) * 0.42
            + per90(p.assists, p.minutes) * 0.20
            + per90(p.shots_on_target, p.minutes) * 0.10
            + per90(p.shots, p.minutes) * 0.035
        )
    elif p.position == Position.MIDFIELDER:
        raw = (
            per90(p.goals, p.minutes) * 0.20
            + per90(p.assists, p.minutes) * 0.24
            + per90(p.chances_created, p.minutes) * 0.10
            + _bounded(p.pass_completion / 100) * 0.28
        )
    elif p.position == Position.DEFENDER:
        raw = (
            per90(p.tackles_won, p.minutes) * 0.09
            + per90(p.interceptions, p.minutes) * 0.09
            + per90(p.clearances, p.minutes) * 0.045
            + _bounded(p.pass_completion / 100) * 0.22
        )
    else:
        save_rate = p.saves / max(1.0, p.saves + max(0.0, -p.goals_prevented))
        raw = save_rate * 0.42 + per90(p.goals_prevented, p.minutes) * 0.20 + per90(p.clean_sheets, p.minutes) * 0.16

    strength = _bounded(p.competition_strength, 0.55, 1.25) * _bounded(p.opponent_strength, 0.65, 1.25)
    recency = time_weight(p.occurred_at, prediction_at)
    sample_confidence = min(1.0, p.minutes / 900)
    baseline = POSITION_BASELINES[p.position]
    # Raw event rates are sparse by nature; center them on a neutral football
    # contribution before applying position baselines and sample confidence.
    normalized = _bounded(0.25 + raw * strength)
    return baseline + (normalized - baseline) * recency * sample_confidence


@dataclass(frozen=True)
class SquadFeatures:
    attack: float
    defense: float
    form: float
    quality: float
    completeness: float


def aggregate_squad(squad: tuple[SquadPlayer, ...], prediction_at: datetime) -> SquadFeatures:
    role_weight = {"starter": 1.0, "substitute": 0.35, "reserve": 0.10}
    expected_count = 18
    ratings: list[tuple[Position, float, float]] = []
    values: list[float] = []

    for player in squad:
        weight = role_weight.get(player.role, 0.10)
        rating = player_rating(player.performance, prediction_at)
        ratings.append((player.performance.position, rating, weight))
        if player.market_value_m is not None and player.market_value_m >= 0:
            values.append(math.log1p(player.market_value_m) * weight)

    if not ratings:
        return SquadFeatures(0.5, 0.5, 0.5, 0.5, 0.0)

    def weighted(position_set: set[Position]) -> float:
        selected = [(rating, weight) for position, rating, weight in ratings if position in position_set]
        if not selected:
            return median(POSITION_BASELINES[position] for position in position_set)
        return sum(rating * weight for rating, weight in selected) / sum(weight for _, weight in selected)

    attack = weighted({Position.FORWARD, Position.MIDFIELDER})
    defense = weighted({Position.DEFENDER, Position.GOALKEEPER, Position.MIDFIELDER})
    form = sum(r * w for _, r, w in ratings) / sum(w for _, _, w in ratings)
    quality = _bounded((sum(values) / max(1, len(values))) / math.log1p(100))
    completeness = min(1.0, len(squad) / expected_count)
    return SquadFeatures(attack, defense, form, quality, completeness)


def team_features(team: TeamContext, prediction_at: datetime) -> dict[str, float]:
    squad = aggregate_squad(team.squad, prediction_at)
    rank_strength = 1 - min(team.fifa_rank, 100) / 110
    elo_strength = _bounded((team.elo - 1200) / 900)
    recent_form = _bounded(team.recent_points_per_game / 3)
    return {
        "attack": 0.45 * squad.attack + 0.30 * _bounded(team.recent_goals_for / 3) + 0.25 * elo_strength,
        "defense": 0.50 * squad.defense + 0.30 * (1 - _bounded(team.recent_goals_against / 3)) + 0.20 * elo_strength,
        "form": 0.60 * squad.form + 0.40 * recent_form,
        "quality": 0.55 * squad.quality + 0.25 * rank_strength + 0.20 * elo_strength,
        "experience": _bounded(team.world_cup_experience),
        "rest": _bounded(team.rest_days / 7),
        "completeness": squad.completeness,
    }

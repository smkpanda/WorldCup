from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Position(StrEnum):
    FORWARD = "forward"
    MIDFIELDER = "midfielder"
    DEFENDER = "defender"
    GOALKEEPER = "goalkeeper"


@dataclass(frozen=True)
class PlayerPerformance:
    player_id: str
    name: str
    position: Position
    team_code: str
    minutes: int
    goals: float = 0
    assists: float = 0
    shots: float = 0
    shots_on_target: float = 0
    chances_created: float = 0
    pass_completion: float = 0
    tackles_won: float = 0
    interceptions: float = 0
    clearances: float = 0
    saves: float = 0
    goals_prevented: float = 0
    clean_sheets: float = 0
    competition_strength: float = 1
    opponent_strength: float = 1
    occurred_at: datetime = field(default_factory=datetime.now)
    source: str = "demo"


@dataclass(frozen=True)
class SquadPlayer:
    performance: PlayerPerformance
    role: str
    market_value_m: float | None = None


@dataclass(frozen=True)
class TeamContext:
    code: str
    name: str
    fifa_rank: int
    elo: float
    recent_points_per_game: float
    recent_goals_for: float
    recent_goals_against: float
    world_cup_experience: float
    rest_days: float
    squad: tuple[SquadPlayer, ...]


@dataclass(frozen=True)
class MatchContext:
    match_id: str
    kickoff: datetime
    home: TeamContext
    away: TeamContext
    venue_home_advantage: float = 0

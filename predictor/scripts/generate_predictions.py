from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "predictor"))

from worldcup.domain import MatchContext, PlayerPerformance, Position, SquadPlayer, TeamContext
from worldcup.features import player_rating, team_features
from worldcup.model import predict_match, score_matrix
from worldcup.validation import validate_squad

DATA = ROOT / "data"
OUTPUT = ROOT / "web" / "data" / "predictions.json"
MODEL_VERSION = "wc-poisson-1.2.0"


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def number(row: dict[str, str], key: str, default: float = 0) -> float:
    value = row.get(key, "").strip()
    return float(value) if value else default


def integer(row: dict[str, str], key: str, default: int = 0) -> int:
    return int(number(row, key, default))


def iso_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def assert_unique(items: list[dict[str, str]], key: str, filename: str) -> None:
    values = [item[key] for item in items]
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise ValueError(f"{filename}: duplicate {key}: {', '.join(duplicates)}")


def team_payload(row: dict[str, str]) -> dict:
    return {
        "id": row["code"].lower(),
        "code": row["code"],
        "name": row["name_en"],
        "nameZh": row["name_zh"],
        "flag": row["flag"],
        "fifaRank": integer(row, "fifa_rank"),
        "squadValueM": number(row, "squad_value_m"),
        "form": row["form"].split("|"),
    }


def load() -> tuple[dict[str, dict], dict[str, TeamContext], dict[str, list[dict]]]:
    team_rows = rows("teams.csv")
    metric_rows = rows("team_metrics.csv")
    player_rows = rows("player_stats.csv")
    assert_unique(team_rows, "code", "teams.csv")
    assert_unique(metric_rows, "team_code", "team_metrics.csv")
    assert_unique(player_rows, "player_id", "player_stats.csv")

    raw_teams = {item["code"]: item for item in team_rows}
    metrics = {item["team_code"]: item for item in metric_rows}
    players_by_team: dict[str, list[dict]] = {}
    for item in player_rows:
        if item["team_code"] not in raw_teams:
            raise ValueError(f"player_stats.csv: unknown team {item['team_code']}")
        players_by_team.setdefault(item["team_code"], []).append(item)

    contexts: dict[str, TeamContext] = {}
    for code, team in raw_teams.items():
        metric = metrics.get(code)
        if not metric:
            raise ValueError(f"team_metrics.csv: missing metrics for {code}")
        squad: list[SquadPlayer] = []
        for item in players_by_team.get(code, []):
            performance = PlayerPerformance(
                player_id=item["player_id"],
                name=item["name"],
                position=Position(item["position"]),
                team_code=code,
                minutes=integer(item, "minutes"),
                goals=number(item, "goals"),
                assists=number(item, "assists"),
                shots=number(item, "shots"),
                shots_on_target=number(item, "shots_on_target"),
                chances_created=number(item, "chances_created"),
                pass_completion=number(item, "pass_completion"),
                tackles_won=number(item, "tackles_won"),
                interceptions=number(item, "interceptions"),
                clearances=number(item, "clearances"),
                saves=number(item, "saves"),
                goals_prevented=number(item, "goals_prevented"),
                clean_sheets=number(item, "clean_sheets"),
                competition_strength=number(item, "competition_strength", 1),
                opponent_strength=number(item, "opponent_strength", 1),
                occurred_at=iso_datetime(item["occurred_at"]),
                source=item["source_url"],
            )
            squad.append(SquadPlayer(performance, item["role"], number(item, "market_value_m")))
        contexts[code] = TeamContext(
            code=code,
            name=team["name_en"],
            fifa_rank=integer(team, "fifa_rank"),
            elo=number(team, "elo"),
            recent_points_per_game=number(metric, "recent_points_per_game"),
            recent_goals_for=number(metric, "recent_goals_for"),
            recent_goals_against=number(metric, "recent_goals_against"),
            world_cup_experience=number(metric, "world_cup_experience"),
            rest_days=number(metric, "rest_days"),
            squad=tuple(squad),
        )
    return raw_teams, contexts, players_by_team


FACTOR_LABELS = (
    ("form", "Recent form", "近期状态"),
    ("quality", "Squad quality", "阵容质量"),
    ("experience", "Tournament experience", "大赛经验"),
    ("defense", "Defensive balance", "防守平衡"),
)


def key_players(player_rows: list[dict], kickoff: datetime) -> list[dict]:
    rated = []
    for item in player_rows:
        performance = PlayerPerformance(
            player_id=item["player_id"],
            name=item["name"],
            position=Position(item["position"]),
            team_code=item["team_code"],
            minutes=integer(item, "minutes"),
            goals=number(item, "goals"),
            assists=number(item, "assists"),
            shots=number(item, "shots"),
            shots_on_target=number(item, "shots_on_target"),
            chances_created=number(item, "chances_created"),
            pass_completion=number(item, "pass_completion"),
            tackles_won=number(item, "tackles_won"),
            interceptions=number(item, "interceptions"),
            clearances=number(item, "clearances"),
            saves=number(item, "saves"),
            goals_prevented=number(item, "goals_prevented"),
            clean_sheets=number(item, "clean_sheets"),
            competition_strength=number(item, "competition_strength", 1),
            opponent_strength=number(item, "opponent_strength", 1),
            occurred_at=iso_datetime(item["occurred_at"]),
            source=item["source_url"],
        )
        rated.append((player_rating(performance, kickoff), item))
    position_zh = {"forward": "前锋", "midfielder": "中场", "defender": "后卫", "goalkeeper": "门将"}
    return [
        {
            "name": item["name"],
            "position": item["position"].title(),
            "positionZh": position_zh[item["position"]],
            "teamCode": item["team_code"],
            "goals": integer(item, "goals"),
            "assists": integer(item, "assists"),
            "minutes": integer(item, "minutes"),
            "rating": round(55 + rating * 40),
        }
        for rating, item in sorted(rated, reverse=True, key=lambda value: value[0])[:3]
    ]


def generate_upcoming(raw_teams: dict[str, dict], contexts: dict[str, TeamContext], players: dict[str, list[dict]]) -> list[dict]:
    match_rows = rows("matches.csv")
    assert_unique(match_rows, "id", "matches.csv")
    output = []
    for row in match_rows:
        home_code, away_code = row["home_team"], row["away_team"]
        if home_code not in contexts or away_code not in contexts:
            raise ValueError(f"matches.csv: unknown team in {row['id']}")
        kickoff = iso_datetime(row["kickoff_utc"])
        home, away = contexts[home_code], contexts[away_code]
        validate_squad(home.squad)
        validate_squad(away.squad)
        result = predict_match(MatchContext(row["id"], kickoff, home, away, number(row, "venue_home_advantage")))
        home_features, away_features = team_features(home, kickoff), team_features(away, kickoff)
        factors = [
            {
                "label": label_en,
                "labelZh": label_zh,
                "home": round(home_features[key] * 100),
                "away": round(away_features[key] * 100),
                "note": "Calculated from the versioned CSV snapshot",
                "noteZh": "根据版本化 CSV 数据快照计算",
            }
            for key, label_en, label_zh in FACTOR_LABELS
        ]
        output.append(
            {
                "id": row["id"],
                "kickoff": kickoff.isoformat().replace("+00:00", "Z"),
                "stage": row["stage_en"],
                "stageZh": row["stage_zh"],
                "venue": row["venue_en"],
                "venueZh": row["venue_zh"],
                "status": row["status"],
                "homeTeam": team_payload(raw_teams[home_code]),
                "awayTeam": team_payload(raw_teams[away_code]),
                "homeWin": result.home_win,
                "draw": result.draw,
                "awayWin": result.away_win,
                "expectedHomeGoals": result.expected_home_goals,
                "expectedAwayGoals": result.expected_away_goals,
                "likelyScore": result.likely_score,
                "topScores": list(result.top_scores),
                "confidence": result.confidence,
                "factors": factors,
                "keyPlayers": key_players(players.get(home_code, []) + players.get(away_code, []), kickoff),
                "modelVersion": MODEL_VERSION,
                "dataVersion": datetime.now(timezone.utc).date().isoformat(),
                "updatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            }
        )
    return output


def review_top_scores(home_xg: float, away_xg: float) -> list[dict]:
    matrix = score_matrix(home_xg, away_xg)
    scores = [
        {"home": home, "away": away, "probability": round(matrix[home][away] * 100, 1)}
        for home in range(len(matrix))
        for away in range(len(matrix))
    ]
    return sorted(scores, key=lambda item: item["probability"], reverse=True)[:3]


def generate_reviews(raw_teams: dict[str, dict]) -> list[dict]:
    review_rows = rows("reviews.csv")
    assert_unique(review_rows, "id", "reviews.csv")
    output = []
    for row in review_rows:
        home_xg, away_xg = number(row, "expected_home_goals"), number(row, "expected_away_goals")
        output.append(
            {
                "id": row["id"],
                "kickoff": row["kickoff_utc"],
                "stage": row["stage_en"],
                "stageZh": row["stage_zh"],
                "venue": row["venue_en"],
                "venueZh": row["venue_zh"],
                "status": "finished",
                "homeTeam": team_payload(raw_teams[row["home_team"]]),
                "awayTeam": team_payload(raw_teams[row["away_team"]]),
                "homeWin": number(row, "home_win"),
                "draw": number(row, "draw"),
                "awayWin": number(row, "away_win"),
                "expectedHomeGoals": home_xg,
                "expectedAwayGoals": away_xg,
                "likelyScore": row["likely_score"],
                "topScores": review_top_scores(home_xg, away_xg),
                "confidence": number(row, "confidence"),
                "factors": [],
                "keyPlayers": [],
                "modelVersion": "historical-snapshot",
                "dataVersion": "2022-12-17",
                "updatedAt": "2022-12-17T12:00:00Z",
                "actualScore": row["actual_score"],
                "resultNote": row["result_note_en"],
                "resultNoteZh": row["result_note_zh"],
                "errorReasons": row["error_reasons_en"].split("|"),
                "errorReasonsZh": row["error_reasons_zh"].split("|"),
            }
        )
    return output


def main() -> None:
    raw_teams, contexts, players = load()
    predictions = generate_upcoming(raw_teams, contexts, players) + generate_reviews(raw_teams)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(predictions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(predictions)} predictions at {OUTPUT}")


if __name__ == "__main__":
    main()

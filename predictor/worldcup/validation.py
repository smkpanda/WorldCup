from __future__ import annotations

from collections import Counter

from .domain import SquadPlayer


class DataValidationError(ValueError):
    pass


def validate_squad(squad: tuple[SquadPlayer, ...]) -> None:
    ids = [item.performance.player_id for item in squad]
    duplicates = [player_id for player_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise DataValidationError(f"Duplicate player ids: {', '.join(duplicates)}")
    for item in squad:
        if not 0 <= item.performance.minutes <= 6000:
            raise DataValidationError(f"Invalid minutes for {item.performance.name}")
        if item.market_value_m is not None and not 0 <= item.market_value_m <= 400:
            raise DataValidationError(f"Invalid market value for {item.performance.name}")

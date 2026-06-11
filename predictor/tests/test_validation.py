import unittest
from datetime import datetime

from worldcup.domain import PlayerPerformance, Position, SquadPlayer
from worldcup.validation import DataValidationError, validate_squad


class ValidationTests(unittest.TestCase):
    def test_duplicate_player_rejected(self):
        player = PlayerPerformance("same", "Player", Position.FORWARD, "AAA", 900, occurred_at=datetime(2026, 1, 1))
        with self.assertRaises(DataValidationError):
            validate_squad((SquadPlayer(player, "starter"), SquadPlayer(player, "substitute")))

    def test_invalid_market_value_rejected(self):
        player = PlayerPerformance("1", "Player", Position.FORWARD, "AAA", 900)
        with self.assertRaises(DataValidationError):
            validate_squad((SquadPlayer(player, "starter", 999),))


if __name__ == "__main__":
    unittest.main()

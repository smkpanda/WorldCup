import unittest
from datetime import datetime, timedelta

from worldcup.domain import PlayerPerformance, Position, SquadPlayer
from worldcup.features import aggregate_squad, per90, player_rating, time_weight


NOW = datetime(2026, 6, 11)


class FeatureTests(unittest.TestCase):
    def test_per90_handles_minutes(self):
        self.assertEqual(per90(10, 900), 1)
        self.assertEqual(per90(10, 0), 0)

    def test_time_decay_and_window(self):
        self.assertGreater(time_weight(NOW - timedelta(days=30), NOW), time_weight(NOW - timedelta(days=180), NOW))
        self.assertEqual(time_weight(NOW - timedelta(days=366), NOW), 0)

    def test_competition_strength_affects_rating(self):
        base = dict(
            player_id="9", name="Forward", position=Position.FORWARD, team_code="AAA",
            minutes=1800, goals=15, shots=60, shots_on_target=30, occurred_at=NOW,
        )
        strong = player_rating(PlayerPerformance(**base, competition_strength=1.2), NOW)
        weak = player_rating(PlayerPerformance(**base, competition_strength=0.6), NOW)
        self.assertGreater(strong, weak)

    def test_starters_outweigh_substitutes(self):
        starter = PlayerPerformance("1", "Starter", Position.FORWARD, "AAA", 900, goals=9, occurred_at=NOW)
        sub = PlayerPerformance("2", "Sub", Position.FORWARD, "AAA", 900, goals=0, occurred_at=NOW)
        features = aggregate_squad((SquadPlayer(starter, "starter", 50), SquadPlayer(sub, "sub", 10)), NOW)
        self.assertGreater(features.attack, 0.5)

    def test_empty_squad_uses_baseline(self):
        features = aggregate_squad((), NOW)
        self.assertEqual(features.attack, 0.5)
        self.assertEqual(features.completeness, 0)


if __name__ == "__main__":
    unittest.main()

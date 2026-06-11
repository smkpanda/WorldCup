import unittest
from datetime import datetime

from worldcup.domain import MatchContext, TeamContext
from worldcup.metrics import brier_score, log_loss
from worldcup.model import poisson_probability, predict_match, score_matrix


def team(code: str, rank: int, elo: float) -> TeamContext:
    return TeamContext(code, code, rank, elo, 2.0, 1.6, 0.8, 0.8, 5, ())


class ModelTests(unittest.TestCase):
    def test_poisson_distribution(self):
        self.assertAlmostEqual(sum(poisson_probability(i, 1.4) for i in range(15)), 1, places=7)

    def test_score_matrix_normalizes(self):
        matrix = score_matrix(1.7, 1.1)
        self.assertAlmostEqual(sum(map(sum, matrix)), 1, places=10)

    def test_prediction_probabilities_sum_to_100(self):
        match = MatchContext("a-b", datetime(2026, 6, 12), team("A", 1, 2000), team("B", 30, 1600))
        result = predict_match(match)
        self.assertAlmostEqual(result.home_win + result.draw + result.away_win, 100, places=1)
        self.assertGreater(result.home_win, result.away_win)
        home_goals, away_goals = map(int, result.likely_score.split("–"))
        self.assertGreater(home_goals, away_goals)

    def test_metrics(self):
        self.assertAlmostEqual(log_loss(0.5), 0.693147, places=5)
        self.assertAlmostEqual(brier_score((0.7, 0.2, 0.1), 0), 0.14)


if __name__ == "__main__":
    unittest.main()

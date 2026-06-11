import unittest
from datetime import datetime

from worldcup.backtest import HistoricalMatch, evaluate, time_split
from worldcup.domain import MatchContext, TeamContext


def team(code):
    return TeamContext(code, code, 10, 1800, 1.8, 1.4, 1.0, 0.6, 5, ())


class BacktestTests(unittest.TestCase):
    def test_time_split_prevents_future_leakage(self):
        old = HistoricalMatch(MatchContext("old", datetime(2024, 1, 1), team("A"), team("B")), 1, 0)
        new = HistoricalMatch(MatchContext("new", datetime(2025, 1, 1), team("A"), team("B")), 1, 1)
        train, test = time_split([new, old], datetime(2024, 6, 1))
        self.assertEqual([item.context.match_id for item in train], ["old"])
        self.assertEqual([item.context.match_id for item in test], ["new"])
        self.assertEqual(evaluate(test)["matches"], 1)


if __name__ == "__main__":
    unittest.main()

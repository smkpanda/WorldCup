from __future__ import annotations

import math


def log_loss(probability: float) -> float:
    return -math.log(max(1e-15, min(1 - 1e-15, probability)))


def brier_score(probabilities: tuple[float, float, float], outcome: int) -> float:
    expected = [0.0, 0.0, 0.0]
    expected[outcome] = 1.0
    return sum((probabilities[i] - expected[i]) ** 2 for i in range(3))

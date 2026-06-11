from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain import MatchContext


class MatchSource(ABC):
    @abstractmethod
    def upcoming_matches(self) -> list[MatchContext]:
        """Return normalized matches without bypassing source access controls."""

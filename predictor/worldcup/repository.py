from __future__ import annotations

import json
from pathlib import Path


class PredictionRepository:
    """Small file-backed repository used by local/CI generation jobs."""

    def __init__(self, output_path: str | Path):
        self.output_path = Path(output_path)
        self.payloads: dict[str, dict] = {}

    def publish(self, prediction_id: str, payload: dict, model_version: str, data_version: str) -> None:
        self.payloads[prediction_id] = payload

    def start_run(self, source: str) -> int:
        return 1

    def finish_run(self, run_id: int, status: str, details: dict) -> None:
        if status != "succeeded":
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(list(self.payloads.values()), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

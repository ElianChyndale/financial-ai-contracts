"""Parse and require records in every generated machine artifact."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _nonempty_json(value: Any) -> bool:
    if isinstance(value, (dict, list)):
        return bool(value)
    return value is not None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result_root = root / "research" / "results" / "v0.1"
    files = sorted(result_root.iterdir())
    if not files:
        raise SystemExit("no generated artifacts")
    checked = 0
    for path in files:
        if path.suffix == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
            if not _nonempty_json(value):
                raise SystemExit(f"empty JSON artifact: {path}")
        elif path.suffix == ".jsonl":
            rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            if not rows:
                raise SystemExit(f"empty JSONL artifact: {path}")
        elif path.suffix == ".csv":
            with path.open(encoding="utf-8", newline="") as stream:
                if not list(csv.DictReader(stream)):
                    raise SystemExit(f"empty CSV artifact: {path}")
        else:
            continue
        checked += 1
    if checked == 0:
        raise SystemExit("no parseable artifacts")
    print(f"parsed {checked} non-empty artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def valid_records(project_root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in sorted((project_root / "fixtures" / "valid").glob("*.json")):
        records[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return records


from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from financial_ai_contracts.cli import main
from financial_ai_contracts.reporting import generate_reports


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def test_cli_validate_catalog(project_root: Path, capsys: object) -> None:
    code = main(["validate", "--catalog", str(project_root / "fixtures" / "valid")])
    assert code == 0


def test_cli_invalid_returns_one(project_root: Path) -> None:
    code = main(
        [
            "validate",
            str(project_root / "fixtures" / "invalid" / "bad-currency.json"),
        ]
    )
    assert code == 1


def test_cli_hash_matches_vector(project_root: Path, capsys: object) -> None:
    code = main(["hash", str(project_root / "fixtures" / "valid" / "evidence-unit.json")])
    assert code == 0


def test_cli_malformed_json_returns_two(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")
    assert main(["validate", str(path)]) == 1


def test_report_is_deterministic_and_artifacts_parse(project_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "reports"
    first = generate_reports(project_root, output)
    first_hashes = _hashes(sorted(output.iterdir()))
    second = generate_reports(project_root, output)
    assert first == second
    assert first_hashes == _hashes(sorted(output.iterdir()))
    assert first["passed"] is True

    machine = project_root / "research" / "results" / "v0.1"
    json_files = sorted(machine.glob("*.json"))
    jsonl_files = sorted(machine.glob("*.jsonl"))
    csv_files = sorted(machine.glob("*.csv"))
    assert json_files and jsonl_files and csv_files
    for path in json_files:
        assert json.loads(path.read_text(encoding="utf-8"))
    for path in jsonl_files:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert rows
    for path in csv_files:
        with path.open(encoding="utf-8", newline="") as stream:
            assert list(csv.DictReader(stream))


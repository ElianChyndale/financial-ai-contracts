"""Synchronize public schemas into the Python wheel package."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "schemas"
    target = root / "src" / "financial_ai_contracts" / "schema_data"
    if args.check:
        mismatches: list[str] = []
        for source_file in sorted(source.rglob("*.json")):
            relative = source_file.relative_to(source)
            target_file = target / relative
            if not target_file.exists() or target_file.read_bytes() != source_file.read_bytes():
                mismatches.append(relative.as_posix())
        expected = {path.relative_to(source) for path in source.rglob("*.json")}
        actual = {path.relative_to(target) for path in target.rglob("*.json")}
        mismatches.extend(f"unexpected:{path.as_posix()}" for path in sorted(actual - expected))
        if mismatches:
            raise SystemExit("schema mirror mismatch: " + ", ".join(mismatches))
        return 0
    target.mkdir(parents=True, exist_ok=True)
    for source_file in sorted(source.rglob("*.json")):
        relative = source_file.relative_to(source)
        target_file = target / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, target_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

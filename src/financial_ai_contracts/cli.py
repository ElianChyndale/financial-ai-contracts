"""Command-line interface for conformance and release workflows."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from financial_ai_contracts.canonical import canonical_text, record_hash
from financial_ai_contracts.migrations import migrate_record
from financial_ai_contracts.reporting import generate_reports, verify_golden_vectors
from financial_ai_contracts.validation import read_json, validate_record


def repository_root() -> Path:
    candidates = [Path.cwd(), Path(__file__).resolve().parents[2]]
    for candidate in candidates:
        if (candidate / "schemas" / "catalog.json").exists() and (candidate / "fixtures").exists():
            return candidate
    raise RuntimeError("run this release command from a Financial AI Contracts source checkout")


def _json_output(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)


def _files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.rglob("*.json"))
    raise ValueError(f"path does not exist: {path}")


def command_validate(args: argparse.Namespace) -> int:
    path = Path(args.catalog or args.path)
    rows: list[dict[str, Any]] = []
    all_valid = True
    for file_path in _files(path):
        try:
            record = read_json(file_path)
            result = validate_record(record, args.contract_type)
            row = {
                "path": file_path.as_posix(),
                "contract_type": result.contract_type,
                "valid": result.valid,
                "issues": [issue.__dict__ for issue in result.issues],
            }
            all_valid = all_valid and result.valid
        except (KeyError, RuntimeError, ValueError) as exc:
            row = {
                "path": file_path.as_posix(),
                "contract_type": args.contract_type,
                "valid": False,
                "issues": [{"layer": "input", "path": "$", "message": str(exc)}],
            }
            all_valid = False
        rows.append(row)
    if not rows:
        raise ValueError(f"no JSON files found: {path}")
    print(_json_output({"valid": all_valid, "count": len(rows), "results": rows}))
    return 0 if all_valid else 1


def command_canonicalize(args: argparse.Namespace) -> int:
    record = read_json(Path(args.input))
    result = validate_record(record, args.contract_type)
    if not result.valid:
        print(_json_output({"valid": False, "issues": [issue.__dict__ for issue in result.issues]}))
        return 1
    text = canonical_text(record)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text)
    return 0


def command_hash(args: argparse.Namespace) -> int:
    record = read_json(Path(args.input))
    result = validate_record(record, args.contract_type)
    if not result.valid:
        print(_json_output({"valid": False, "issues": [issue.__dict__ for issue in result.issues]}))
        return 1
    print(record_hash(record))
    return 0


def command_migrate(args: argparse.Namespace) -> int:
    migrated = migrate_record(read_json(Path(args.input)), args.contract_type, args.target)
    text = _json_output(migrated) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0


def command_verify_golden(args: argparse.Namespace) -> int:
    root = repository_root()
    rows = verify_golden_vectors(root)
    passed = bool(rows) and all(bool(row["valid"]) for row in rows)
    print(_json_output({"valid": passed, "count": len(rows), "results": rows}))
    return 0 if passed else 1


def command_report(args: argparse.Namespace) -> int:
    root = repository_root()
    output = Path(args.output)
    summary = generate_reports(root, output)
    print(_json_output(summary))
    return 0 if bool(summary["passed"]) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="financial-ai-contracts",
        description="Validate and verify versioned Financial AI Contracts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a JSON file or directory")
    validate_parser.add_argument("path", nargs="?", default="fixtures/valid")
    validate_parser.add_argument("--catalog", help="directory alias used by release checks")
    validate_parser.add_argument("--type", dest="contract_type")
    validate_parser.set_defaults(handler=command_validate)

    canonical_parser = subparsers.add_parser("canonicalize", help="write FAC canonical JSON")
    canonical_parser.add_argument("input")
    canonical_parser.add_argument("--type", dest="contract_type")
    canonical_parser.add_argument("--output")
    canonical_parser.set_defaults(handler=command_canonicalize)

    hash_parser = subparsers.add_parser("hash", help="hash a validated record")
    hash_parser.add_argument("input")
    hash_parser.add_argument("--type", dest="contract_type")
    hash_parser.set_defaults(handler=command_hash)

    migration_parser = subparsers.add_parser("migrate", help="run an explicit schema migration")
    migration_parser.add_argument("input")
    migration_parser.add_argument("--type", dest="contract_type", required=True)
    migration_parser.add_argument("--target", default="1.0.0")
    migration_parser.add_argument("--output")
    migration_parser.set_defaults(handler=command_migrate)

    golden_parser = subparsers.add_parser("verify-golden", help="verify canonical and ABI vectors")
    golden_parser.set_defaults(handler=command_verify_golden)

    report_parser = subparsers.add_parser("report", help="regenerate release evidence")
    report_parser.add_argument("--output", default="reports/v0.1")
    report_parser.set_defaults(handler=command_report)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (KeyError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

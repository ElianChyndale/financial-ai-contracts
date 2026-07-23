"""FAC Canonical JSON Profile and deterministic record hashing."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    """Serialize JSON-compatible data with sorted keys and no extra whitespace."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def record_hash(value: Any) -> str:
    return "0x" + hashlib.sha256(canonical_bytes(value)).hexdigest()


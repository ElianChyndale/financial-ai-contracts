import { createHash } from "node:crypto";

function normalized(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(normalized);
  }
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return Object.fromEntries(
      Object.keys(record)
        .sort()
        .map((key) => [key, normalized(record[key])]),
    );
  }
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  throw new TypeError(`value is not JSON-compatible: ${typeof value}`);
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalized(value));
}

export function recordHash(value: unknown): string {
  return `0x${createHash("sha256").update(canonicalJson(value), "utf8").digest("hex")}`;
}


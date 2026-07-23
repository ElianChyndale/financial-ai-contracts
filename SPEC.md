# Specification

## Purpose

Financial AI Contracts defines a small, portable contract layer for evidence-grounded
financial-AI systems. It standardizes interchange records without implementing
retrieval, risk scoring, valuation, lending, or research experiments.

## Normative Language

The words **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative.

## Contract Identity

Every top-level record MUST contain:

- `schema_version`, fixed to a supported semantic version;
- a stable record identifier;
- only fields declared by the selected schema.

v0.1 publishes schema version `1.0.0`. Schemas use JSON Schema Draft 2020-12 and
reject undeclared properties.

## Shared Rules

- Timestamps MUST be RFC 3339 date-times with an explicit UTC offset.
- Canonical persisted timestamps MUST be normalized to `Z`.
- Calendar dates MUST use `YYYY-MM-DD`.
- Hashes MUST use lowercase, `0x`-prefixed hexadecimal.
- Human decimal quantities MUST be JSON strings in non-exponent canonical decimal
  form. This avoids binary floating-point differences between languages.
- Basis-point values MUST be integers.
- Risk score and confidence strings MUST use at most six fractional digits so the
  Solidity parts-per-million projection is exact.
- Currency MUST be a three-letter uppercase ISO-style code. Validation checks syntax,
  not whether a code is currently issued.
- Identifiers MUST match `[a-z0-9][a-z0-9._:-]{2,127}`.
- Empty strings, non-finite numbers, negative elapsed times, naive timestamps, and
  duplicate identifiers MUST be rejected where applicable.

## Canonical JSON Profile

The repository uses the **FAC Canonical JSON Profile**, not a claim of full RFC 8785
conformance:

1. UTF-8 encoding without a byte-order mark.
2. Object keys sorted by Unicode code point.
3. No insignificant whitespace.
4. JSON literals serialized in lowercase.
5. Arrays retain input order.
6. Contract decimal values are strings and are therefore not reformatted by the
   serializer.
7. A trailing newline is excluded from canonical bytes.

The record hash is `sha256(canonical_bytes)` and is rendered as lowercase
`0x`-prefixed hexadecimal.

## Validation Layers

1. JSON parsing.
2. Draft 2020-12 schema validation.
3. Pydantic type validation.
4. Cross-field semantic checks.
5. Optional cross-language golden-vector comparison.

Passing these layers proves structural conformance only.

## Security Boundaries

`RiskAttestation.signature` is an opaque byte string. Structural validation MUST NOT
be described as signature verification. A consumer MUST independently verify the
signer, chain, domain, expiry, nonce, and business authorization.

The public cryptographic fixtures use a documented test identity and MUST NOT be used
to protect assets.

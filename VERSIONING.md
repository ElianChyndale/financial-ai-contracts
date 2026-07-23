# Versioning and Migration

## Version Axes

- Repository releases use SemVer tags such as `v0.1.0`.
- Each record carries its own `schema_version`.
- v0.1 of the repository publishes record schema `1.0.0`.

Repository and schema versions are intentionally independent.

## Compatibility Policy

- Patch schema releases may clarify descriptions or tighten a rule only when the
  previously accepted instance set does not change.
- Minor schema releases may add optional fields.
- Major schema releases may rename fields, change required fields, alter canonical
  representation, or change semantic constraints.
- Unknown properties remain rejected. A new optional field therefore requires a new
  schema version even if older consumers can ignore it after explicit negotiation.

## Migration Rules

Migrations:

- MUST name both source and target versions;
- MUST be deterministic;
- MUST preserve all representable information;
- MUST fail on unknown input fields rather than silently discard them;
- MUST validate the migrated result;
- MUST be idempotent when input already uses the target version.

v0.1 includes documented legacy `0.1.0` to `1.0.0` examples for
`EvidenceUnit` and `RiskAttestation`.

## Deprecation

Deprecated schemas remain readable for at least one repository minor release when
they have been publicly released. No deprecated schema is present in v0.1.


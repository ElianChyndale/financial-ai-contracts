# Cross-Language Conformance

- Canonical JSON and SHA-256 vectors: 5 checked.
- Python ↔ TypeScript canonical byte agreement: covered by checked-in vectors and
  the TypeScript conformance suite.
- Python ↔ TypeScript risk-attestation ABI agreement: checked for the synthetic
  golden vector.
- Solidity source: compiled with Solidity 0.8.30 using the IR pipeline.

The ABI representation is the projection documented in `solidity/ABI_MAPPING.md`.
Identifier hashes and parts-per-million probability conversions are explicit.

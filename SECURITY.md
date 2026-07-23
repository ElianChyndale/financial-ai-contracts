# Security Policy

## Scope

This repository defines data shapes and deterministic encodings. It does not provide
authorization, key custody, signature verification, transaction execution, or
financial controls.

## Reporting

Please report a suspected vulnerability privately through the GitHub repository's
security advisory interface. Do not include real private keys, credentials, customer
records, or confidential financial documents in an issue.

## Fixture safety

Addresses, identifiers, hashes, signature bytes, and records under `fixtures/` are
synthetic. They MUST NOT be treated as trusted identities or used to protect assets.

## Consumer responsibilities

Consumers must independently enforce:

- signer and provider authorization;
- chain ID and verifying-contract domain separation;
- nonce replay protection;
- issue and expiry policy;
- evidence availability and content integrity;
- unit, precision, rounding, and financial-model policy;
- logging, access control, incident response, and regulatory review.


# Contributing

Contributions should solve a concrete interoperability problem and keep the default
workflow deterministic and offline.

Before opening a change:

```bash
python -m pip install -e ".[dev]"
pnpm install --frozen-lockfile
python scripts/sync-schemas.py --check
python -m pytest
python -m ruff check src tests scripts
python -m mypy src/financial_ai_contracts
pnpm check
financial-ai-contracts report --output reports/v0.1
python scripts/check-artifacts.py
```

Schema changes require a versioning assessment, matching Python and TypeScript types,
valid and invalid fixtures, migration guidance, and changelog entry. Solidity changes
also require an explicit JSON-to-ABI mapping and cross-language golden vector.

Do not submit real private documents, credentials, wallet material, copyrighted
documents without redistribution rights, or claims that fixtures are external
experimental results.


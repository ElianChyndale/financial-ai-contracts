# FAC Canonical JSON Profile

Canonicalization exists so Python and TypeScript can hash the same valid JSON record.
It sorts object keys, preserves array order, removes insignificant whitespace, writes
UTF-8, and excludes a trailing newline.

```python
from financial_ai_contracts.canonical import canonical_text, record_hash

text = canonical_text(record)
digest = record_hash(record)
```

```typescript
import { canonicalJson, recordHash } from "./typescript/dist/index.js";
```

This deliberately narrow profile is not advertised as full RFC 8785. Contract
financial decimals are strings, eliminating the most relevant cross-runtime numeric
serialization ambiguity. Callers must validate a record before treating its hash as a
contract hash.

Arrays are order-sensitive. This is intentional for evidence lists, cash flows,
metrics, assumptions, and limitations. A producer must establish domain-specific
ordering before hashing.


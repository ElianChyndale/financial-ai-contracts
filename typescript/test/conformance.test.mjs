import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  canonicalJson,
  encodeRiskAttestation,
  recordHash,
  validateRecord,
} from "../dist/index.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

async function json(relative) {
  return JSON.parse(await readFile(path.join(root, relative), "utf8"));
}

test("golden canonical JSON and hashes match", async () => {
  const lines = (await readFile(path.join(root, "fixtures/golden/vectors.jsonl"), "utf8"))
    .trim()
    .split("\n")
    .map(JSON.parse);
  assert.equal(lines.length, 5);
  for (const vector of lines) {
    assert.equal(canonicalJson(vector.record), vector.canonical_json);
    assert.equal(recordHash(vector.record), vector.sha256);
    if (vector.contract_type === "risk-attestation") {
      assert.equal(encodeRiskAttestation(vector.record), vector.abi_encoding);
    }
  }
});

test("all public valid fixtures pass schema and semantic validation", async () => {
  const catalog = await json("schemas/catalog.json");
  for (const [contractType, schemaPath] of Object.entries(catalog.contracts)) {
    const schema = await json(`schemas/${schemaPath}`);
    const record = await json(`fixtures/valid/${contractType}.json`);
    const result = validateRecord(contractType, record, schema);
    assert.deepEqual(result, { valid: true, issues: [] });
  }
});

test("all invalid fixtures fail at their declared layer", async () => {
  const catalog = await json("schemas/catalog.json");
  const { readdir } = await import("node:fs/promises");
  const files = await readdir(path.join(root, "fixtures/invalid"));
  assert.ok(files.length >= 10);
  for (const file of files) {
    const fixture = await json(`fixtures/invalid/${file}`);
    const schema = await json(`schemas/${catalog.contracts[fixture.contract_type]}`);
    const result = validateRecord(fixture.contract_type, fixture.record, schema);
    assert.equal(result.valid, false, file);
    assert.equal(result.issues[0]?.layer, fixture.expected_layer, file);
  }
});


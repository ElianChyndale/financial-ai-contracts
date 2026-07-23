import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import solc from "solc";

const sourcePath = path.resolve("solidity/src/FinancialAIContractsV1.sol");
const source = await readFile(sourcePath, "utf8");
const input = {
  language: "Solidity",
  sources: {
    "FinancialAIContractsV1.sol": { content: source },
  },
  settings: {
    optimizer: { enabled: true, runs: 200 },
    viaIR: true,
    outputSelection: {
      "*": { "*": ["abi", "evm.bytecode.object"] },
    },
  },
};
const output = JSON.parse(solc.compile(JSON.stringify(input)));
const errors = (output.errors ?? []).filter((item) => item.severity === "error");
assert.deepEqual(errors, []);
const contracts = output.contracts?.["FinancialAIContractsV1.sol"];
assert.ok(contracts?.FinancialAIContractsV1);
assert.ok(contracts?.FinancialAIContractsCodecV1);
assert.ok(contracts.FinancialAIContractsCodecV1.evm.bytecode.object.length > 0);

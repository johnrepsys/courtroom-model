# Courtroom contributor demo: canonicalization slice

A small offline example for contributors: run the **existing unitless canonicalization prototype** on invented
inputs. This does not run the Courtroom solver or reproduce a pilot result.

## One command

From this directory, with Python 3.10 or newer:

```sh
python3 -I -B demo.py
```

No installation, account, API key, network, AWS or paid service is needed. Only
Python's standard library is used. The command verifies the preserved source
hash, runs 15 synthetic tests, then prints JSON. It exits nonzero on failure.
It creates no output files; `-B` avoids bytecode caches. Re-running is safe.

The stable summary fields are:

```json
{
  "status": "pass",
  "scope": "existing-unitless-canonicalization-prototype",
  "synthetic_tests_passed": 15,
  "numeric_precision": 6,
  "rounding": "half-even",
  "illustrative_exponent_bounds": [-6, 9],
  "solver_ran": false,
  "benchmark_records_loaded": 0
}
```

The exact full stdout is in `EXPECTED_OUTPUT.json`. It includes five invented examples:

| Input | Result |
| --- | --- |
| `1/3` | positive coefficient `333333`, normalized exponent `-1` |
| `1.234565` | positive coefficient `123456`, exponent `0` (half-even tie) |
| `9.999995` | positive coefficient `100000`, exponent `1` (rounding carry) |
| `1e10` | bottom, `rounded_exponent_out_of_range` |
| `3 kg` | bottom, `unsupported_or_malformed_number` |

A finite label represents `sign × coefficient × 10^(exponent − 5)`. There is
also a single zero label and a bottom/invalid label. Two bottom labels do **not**
mean two answers are correct. No scorer is implemented here.

## What actually runs

`canonical_numeric.py` is copied byte-for-byte from the existing prototype.
The source hash is recorded in `PROVENANCE.json` and checked by `demo.py`.
Exact integer/rational arithmetic parses strings and rounds to six significant
digits with half-even ties. The illustrative range is global, not per example.
Tests cover parsing, schema rejection, range bounds, carry, ties, no mutation,
finite-grid size and round trips. New test/demo glue is not production solver code.

The entry point adds a Python audit-hook tripwire against socket operations and
child process launches, and tests the guard. This is cooperative regression
protection, **not** network isolation or a security sandbox. It does not prove
that arbitrary future code or native extensions cannot communicate. `-I` ignores
Python environment settings and user site-packages; the demo never reads secrets.

## Boundaries

- Unitless only. No Pint normalization, typed quantities or dimensional checks.
- No solver, LLM, retrieval, knowledge graph, motif admission, assessor, custody
  gate, archive, trusted release, live provider, benchmark or private record loads.
- No registered FormulaReasoning answer schema or experiment exponent bounds.
- No benchmark accuracy, real family-pool size or deployment-readiness claim.
- S3 is private deployment-only infrastructure, separate from the contribution
  path. This demo has no S3 or AWS dependency. GitHub source review and local
  tests are sufficient for this contribution slice.

See `CONTRIBUTING.md` for ways to help and `LICENSE` for the MIT terms
that apply to this example.

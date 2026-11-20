#!/usr/bin/env python3
"""Run synthetic checks of the preserved unitless canonicalizer, offline."""
from pathlib import Path
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parent


def no_external_io(event, args):
    # A regression tripwire for this cooperative demo, not an OS sandbox.
    if event.startswith("socket.") or event in {"subprocess.Popen", "os.system"}:
        raise PermissionError("contributor demo forbids network and child processes")


def main():
    sys.addaudithook(no_external_io)
    sys.path.insert(0, str(ROOT))
    provenance = json.loads((ROOT / "PROVENANCE.json").read_text(encoding="utf-8"))
    actual = hashlib.sha256((ROOT / "canonical_numeric.py").read_bytes()).hexdigest()
    if actual != provenance["preserved_source_sha256"]:
        raise SystemExit("Preserved source changed: review provenance before running.")

    from canonical_numeric import GridConfig, canonicalize_answer
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_*.py")
    result = unittest.TestResult()
    suite.run(result)
    if not result.wasSuccessful() or not result.testsRun:
        for test, error in result.errors + result.failures:
            print(f"FAIL: {test}\n{error}", file=sys.stderr)
        raise SystemExit("Synthetic checks failed or no tests were collected.")

    config = GridConfig(-6, 9)  # Illustrative global range, not a registered study setting.
    examples = [
        {"input": token, "result": canonicalize_answer({"answer": token}, config).as_dict()}
        for token in ("1/3", "1.234565", "9.999995", "1e10", "3 kg")
    ]
    print(json.dumps({
        "status": "pass",
        "scope": "existing-unitless-canonicalization-prototype",
        "synthetic_tests_passed": result.testsRun,
        "numeric_precision": 6,
        "rounding": "half-even",
        "illustrative_exponent_bounds": [-6, 9],
        "solver_ran": False,
        "benchmark_records_loaded": 0,
        "examples": examples,
    }, indent=2))


if __name__ == "__main__":
    main()

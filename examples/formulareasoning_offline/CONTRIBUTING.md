# Contributing to the local slice

The intended path is source changes and local tests reviewed through GitHub.
No cloud account or credentials should be needed to contribute. This example
can be run without the rest of the repository. See `LICENSE` for its terms.

## First small contribution

Add an invented edge case to `test_canonical_numeric.py`, then run:

```sh
python3 -I -B demo.py
```

Keep fixtures synthetic, exact-string and unitless. Do not paste a benchmark
question, hidden reference, historical prompt, notebook, solver trace or private
path. Tests count methods; update the documented count if you add a new method.
The guard checks require this entry point, not standalone unittest discovery.
The preserved file's hash is intentional: a code change requires explicit source
review and a corresponding provenance update, not simply removing the check.

## Subsequent contribution lanes (not implemented here)

- **Solver:** separately identify and audit the minimal real solver dependency
  slice and synthetic mock provider before proposing an offline runner. Preserve
  the solver source and test a genuine execution path. Do not relabel these
  numeric checks as a solver test.
- **Assessor:** propose a separately reviewed typed-normalization contract and
  synthetic fixtures, then integrate the existing assessor after its dependencies
  and provenance are vetted. Keep rejection distinct from answer correctness.
- **Gates/custody:** propose synthetic fail-closed tests for existing receipt and
  reveal boundaries, with explicit mock-versus-deployment limits. Do not infer
  real eligible-family counts or confidentiality from a local test double.

Keep these lanes additive and separately reviewable. The present demo is not
coupled to the trusted v4 runtime and must not edit or deploy that runtime.
Cloud storage, credentials and optional deployment plumbing belong outside core.

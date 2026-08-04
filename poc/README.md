# PoC — reproduce in under a minute

```bash
cd poc
python verify_vendor_hashes.py   # confirm every vendored file matches potpie-ai/potpie@b5a67742, byte-for-byte
python injection_chain_repro.py  # run the 5-stage reproduction
```

Requires only the Python standard library. No API keys, no network access
(beyond the optional `--live` flag on `verify_vendor_hashes.py`, which
re-fetches from GitHub via the `gh` CLI to double-check the local copies —
skip it if you don't have `gh` installed; the local hash comparison alone
is sufficient), no Neo4j, no LLM calls, no live Potpie instance.

## What it does

Walks a synthetic "attacker opens a public GitHub Issue" scenario through
five real, cited stages of `potpie-ai/potpie`'s own source (see
`RESEARCH.md` for the full pipeline diagram and the five questions this
answers) and writes the final delivered artifact to `final_artifact.json`.

## What's real code vs. reproduced

| File | Status |
|---|---|
| `vendor/potpie_context_core/ports/claim_query.py` | Unmodified, real import |
| `vendor/potpie_context_core/agent_envelope.py` | Unmodified, real import |
| `vendor/potpie_context_core/graph_contract.py`, `semantic_mutations.py`, `ports/agent_context.py`, `ports/graph_service.py` | Unmodified, real import (transitive dependencies of the above) |
| `vendor/potpie_nudge.py` | Unmodified, real import |
| `vendor/read_presenter.py` | Unmodified, real import |
| `claim_payload()`, `_format_inject_context()` (inside `injection_chain_repro.py`) | Verbatim copies, exact file:line cited in the docstring. Not imported because their parent modules pull in unrelated package machinery; their function bodies call nothing from those imports. |
| `_verify_signature()` (inside `injection_chain_repro.py`) | Verbatim copy of `connector.py:266-270`. Not imported because the parent module constructs a live `PyGithub` client at import time. |

`VENDOR_HASHES.json` records a SHA-256 for every vendored file, computed
against the file as fetched from `potpie-ai/potpie` at commit `b5a67742`.
`verify_vendor_hashes.py` recomputes and compares — run it before trusting
anything else in this directory.

## Windows note

`read_presenter.py` uses a Unicode arrow character (`↳`) in its real
output. If you see a `UnicodeEncodeError` on Windows, run with:

```bash
PYTHONIOENCODING=utf-8 python injection_chain_repro.py
```

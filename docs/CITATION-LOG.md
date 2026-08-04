# Citation log and corrections

Every non-trivial claim in this repository, with its source, plus a record
of claims from earlier materials on this vendor that turned out to be
wrong when checked directly against live source. Listed because the
constitution this research follows treats one uncaught false claim as more
damaging than an admitted correction.

## Corrections — claims from prior materials that did not survive verification

An earlier OSINT-style audit of this vendor (AI-generated; the source PDF
carries a visible Qwen watermark) made several claims tagged as
`[VERIFIED]` that were not, in fact, verifiable against live source:

| Claim | Audit's tag | What direct verification found |
|---|---|---|
| PR #630 was merged into `main` | `[VERIFIED]` | `gh api repos/potpie-ai/potpie/pulls/630` → `"merged": false, "state": "open"`. Still open, 5+ months after being filed. |
| `uv.lock` confirms a vulnerable pinned LiteLLM version (CVE-2026-40217) | `[VERIFIED]` | `litellm` does not appear anywhere in `uv.lock` (4487 lines, zero matches), nor in the dependency list of the root `pyproject.toml` or any workspace member's `pyproject.toml`. The `# litellm>=1.83.10 clears CVE-2026-40217...` comment in `pyproject.toml` is residual documentation of a historical `override-dependencies` decision, not evidence of a currently-installed vulnerable package. |
| The vulnerability is CWE-1387 | Used as headline classification in both the original March advisory and the OSINT audit | CWE-1387 is not a weakness. It is a *View* — "Weaknesses in the 2022 CWE Top 25 Most Dangerous Software Weaknesses" — a navigational index over other CWEs, and its own MITRE page states `Vulnerability Mapping: PROHIBITED`. It was never possible to correctly map this finding to CWE-1387. The correct entry is **CWE-1427**, "Improper Neutralization of Input Used for LLM Prompting" — real, Base-level, approved for mapping (verified directly against cwe.mitre.org). |

A separate, earlier AI-assisted verification pass on this same research
(logged in full in the working notes, not reproduced here) independently
fabricated a nonexistent function name (`fence_untrusted_content`) and two
nonexistent file paths (`parsing/python.rs`, `parsing/utils.py`) while
attempting to confirm a related claim. Those fabrications were caught
before anything built on them and are not present anywhere in this
repository. Noted here as a record of why every claim below was
independently re-checked rather than taken from any single source,
including AI-generated ones — including this one's own prior drafts.

## Primary citations — this finding

| Claim | File | Lines | Commit |
|---|---|---|---|
| `ClaimRow` has no trust/provenance field | `potpie/context-core/src/potpie_context_core/ports/claim_query.py` | 23-55 | `b5a67742` |
| `EvidenceItem`/`AgentEnvelope` have no trust/provenance field; module states no server-side answer synthesis occurs | `potpie/context-core/src/potpie_context_core/agent_envelope.py` | 1-8, 24-33, 57-68 | `b5a67742` |
| `claim_payload()` passes `fact`/`description` through unmodified | `potpie/context-engine/src/potpie_context_engine/application/readers/_common.py` | 152-181 | `b5a67742` |
| `EnvelopeBuilder` copies `payload` without transformation | `potpie/context-engine/src/potpie_context_engine/application/services/envelope_builder.py` | 89 | `b5a67742` |
| Nudge `_format_inject_context()` builds injected text from `description`/`summary`/`fact`, unsanitized | `potpie/context-engine/src/potpie_context_engine/application/services/nudge_service.py` | 40-90, 160-196 | `b5a67742` |
| `render_output()` injects raw text into Claude Code's `additionalContext`/`systemMessage`, no fence/tag | `potpie/cli/templates/claude_plugin/hooks/potpie_nudge.py` | 397-422 | `b5a67742` |
| `graph read --relations full` prints `fact` verbatim | `potpie/cli/read_presenter.py` | `_display_fact` at 514-518, `_format_relations_full_lines` at 459-481 | `b5a67742` |
| `graph neighborhood --detail full` dumps raw node `properties` | `potpie/cli/commands/graph.py` | 1449-1466 | `b5a67742` |
| GitHub webhook signature check verifies delivery origin only, not actor identity | `potpie/context-engine/.../adapters/outbound/connectors/github/connector.py` | 266-270 | `b5a67742` |
| Linear webhook signature check is skipped entirely when `LINEAR_WEBHOOK_SECRET` is unset | `potpie/integrations/integrations/adapters/inbound/http/sources_router.py` | 317-332 | `b5a67742` |
| No `author_association`/`collaborator` gate anywhere in the codebase | repo-wide search, zero hits | — | `b5a67742` |
| Reconciliation write-path validator is structural only, does not inspect claim content | `potpie/context-engine/.../reconciliation/reconciliation_validation.py` | `validate_reconciliation_plan`, ~49-145 | `b5a67742` |
| Claim/entity mutations classified low-risk, auto-applied | `potpie/context-engine/.../reconciliation/semantic_mutation_validator.py` | 740-765 | `b5a67742` |
| Ingress-side prompt-level untrusted-data defense and data-fencing | `potpie/context-engine/.../reconciliation/pydantic_deep_agent.py` | 1122-1130 (instruction), 1166-1181 (fence), 389/911/1094 (tool-call budget citing "security review H-1") | `b5a67742` |
| `py_graph.py::create_graph()` embeds full raw file text on `FILE` nodes | `potpie/parsing/parsing/py_graph.py` | 73-80 | `b5a67742` |
| `create_graph()` has no callers outside `potpie/parsing/` package | repo-wide search | — | `b5a67742` |
| `litellm` absent from all dependency manifests | `pyproject.toml` (root + all workspace members), `uv.lock` | — | `b5a67742` |
| `/debug/oauth-config` missing auth guard, leaks `SENTRY_CLIENT_SECRET` in plaintext | `potpie/integrations/integrations/adapters/inbound/http/integrations_router.py` | 2629-2693 (compare guarded neighbor at 2595-2596) | `b5a67742` |
| Issue #629 open, PR #630 open/unmerged | GitHub API (`issues/629`, `pulls/630`) | — | live, checked at research time |
| v2.0.0 released 3 July 2026 | GitHub API (`releases/tags/v2.0.0`) → `published_at` | — | — |
| CWE-1427 is real, Base-level, mapping-approved | cwe.mitre.org/data/definitions/1427.html | — | — |
| CWE-1387 is a View, `Vulnerability Mapping: PROHIBITED` | cwe.mitre.org/data/definitions/1387.html | — | — |

Every file listed above with commit `b5a67742` is also byte-for-byte
hash-verified in `poc/VENDOR_HASHES.json` where it was vendored for the
PoC — see `poc/verify_vendor_hashes.py`.

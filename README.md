# potpie-context-provenance

A deterministic, model-free reproduction of a trust-provenance defect in
Potpie AI's Context Graph: content that can originate from an untrusted,
externally-controlled source (a GitHub Issue, a Linear ticket) is delivered
to external coding agents (Claude Code, Cursor, Codex) through Potpie's own
CLI/hook contract with **no field, tag, or marker distinguishing it from
developer-authored context**.

This is part 2 of a two-part disclosure. Part 1,
[`potpie-graphrag-prompt-injection`](https://github.com/marsakahenry14-lab/potpie-graphrag-prompt-injection),
covers the original 8 March 2026 finding — five direct outreach attempts
to Potpie's founders across email and LinkedIn, a CVE request that went
nowhere, and 5+ months of silence before a July 2026 public announcement.
That report's specific mechanism (Potpie's own LLM agent, with
tool-access, reading unsanitized graph content) no longer exists — Potpie
shipped a substantial architectural rewrite in the interim. A new instance
of the same underlying defect does exist, in different code; see
[`docs/ARCHITECTURE-DELTA.md`](docs/ARCHITECTURE-DELTA.md).

**→ Full writeup: [RESEARCH.md](RESEARCH.md)**

## TL;DR

- **The property under test**: can an external agent, using only Potpie's
  own contract, tell attacker-controlled content apart from trusted
  context? **No.** Nothing in the contract carries that information.
- **Root cause, not a bug in one function**: the `ClaimRow`/`EvidenceItem`
  schema shared by every reader and writer in `potpie-context-core` has no
  trust/provenance field. `truth`/`confidence`/`evidence_strength` exist,
  but encode *epistemic* confidence ("is this claim true"), not *security*
  provenance ("is this text safe to treat as passive data").
- **Two independent egress sinks, same leak**: the PoC proves this isn't
  one overlooked function. The identical poisoned `EvidenceItem` leaks
  through both the Claude Code/Cursor/Codex hook path (`potpie_nudge.py`)
  and the plain-text CLI reader (`read_presenter.py`) — different files,
  different code, same missing schema field.
- **Deterministic, no LLM calls**: the PoC does not call, jailbreak, or
  make claims about any model. It traces real, unmodified source through
  five stages — ingress, internal representation, envelope, and two egress
  surfaces — and asserts the final JSON/text artifact contains the
  attacker's text verbatim.
- **Self-verifying**: every vendored file is checked byte-for-byte against
  `potpie-ai/potpie @ b5a67742` — `python poc/verify_vendor_hashes.py`.
  Nothing is taken on trust, including from us.

## Quickstart

```bash
cd poc
python verify_vendor_hashes.py   # confirm every vendored file matches upstream, byte-for-byte
python injection_chain_repro.py  # run the 5-stage reproduction, writes final_artifact.json
```

No network calls, no API keys, no Neo4j, no live Potpie instance required.

## What's in here

| Path | What it is |
|---|---|
| `RESEARCH.md` | Full writeup — root cause, evidence chain, both egress sinks, classification. |
| `docs/VECTOR-MAP.md` | Inventory of every ingress/egress channel checked, each independently verified. |
| `docs/ARCHITECTURE-DELTA.md` | What changed in Potpie's codebase between March and August 2026, and what didn't. |
| `docs/OAUTH-LEAK.md` | A separate, unrelated live vulnerability found during this research (unauthenticated `/debug/oauth-config`) — kept apart from the provenance finding, not mixed in. |
| `docs/CITATION-LOG.md` | Every claim's file:line:commit citation, plus a log of fabricated claims caught and corrected during this research. |
| `docs/DISCLOSURE.md` | Responsible-disclosure status for this finding. |
| `poc/` | The reproduction: `injection_chain_repro.py`, `verify_vendor_hashes.py`, vendored real source. |

## Honest scope

- This traces a **data-flow property**, not a jailbreak. No model is called;
  the claim is about the contract, and is true regardless of which model
  ends up reading the delivered context.
- The hop from "ingress event" to "ClaimRow written" is performed in
  production by an LLM (`pydantic_deep_agent.py`) and is genuinely
  non-deterministic. This PoC does not simulate or claim anything about
  whether that LLM's own prompt-level defenses hold. What it proves is
  narrower and does not depend on that question: nothing in the
  deterministic code on either side of that LLM call inspects, sanitizes,
  or tags `fact`/`description` content.
- Potpie's team has visibly engineered real defenses elsewhere in this same
  codebase (ingress-side prompt fencing, a numbered internal security
  review — see `docs/ARCHITECTURE-DELTA.md`). This is not a claim of
  negligence; it's a claim that the fix didn't reach the egress contract.

## License

MIT — see [`LICENSE`](LICENSE).

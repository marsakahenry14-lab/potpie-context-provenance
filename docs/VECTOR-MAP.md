# Vector map — ingress and egress channels

Every channel below shares the same root cause (see `RESEARCH.md`): the
`ClaimRow`/`EvidenceItem` schema carries no trust/provenance field, so
nothing built on it can either gate ingress by content trustworthiness or
mark egress by content origin.

Confidence key:
- **Verified directly** — read the exact cited source at
  `potpie-ai/potpie @ b5a67742` myself, with line numbers, during this
  research.
- **Reported, re-verified** — first surfaced by an independent AI-assisted
  audit pass, then independently re-checked by me against live source
  before inclusion here.
- **Reported, not independently re-verified** — surfaced by that audit
  pass only; plausible and consistent with the rest of the findings, but I
  did not personally re-read the cited code before listing it. Treat as
  lower confidence than the other two tiers.

## Ingress — how content enters the graph

| ID | Channel | What gates it | Confidence |
|---|---|---|---|
| I-1 | GitHub webhook | `_verify_signature()` (`connectors/github/connector.py:266-270`) — HMAC-SHA256 over the delivery body, constant-time compare. Verifies the delivery is genuinely from GitHub for this repo. Does **not** check `author_association`/`collaborator` status of the issue/PR author — a repo-wide search for those terms returns zero hits. | **Verified directly** — reproduced live in `poc/injection_chain_repro.py` Stage 1. |
| I-2 | Linear webhook | `linear_sources_webhook()` (`integrations/adapters/inbound/http/sources_router.py:317-332`). Signature check is conditional: `if secret and not linear_signature: raise 401`. If `LINEAR_WEBHOOK_SECRET` is unset, the entire block is skipped and the payload is processed with **no verification at all**. | **Verified directly** — read the exact function, lines 317-332. |
| I-3 | Agent-mediated ingestion (`potpie-source-ingestion` skill) | The skill (`cli/templates/claude_plugin/skills/potpie-source-ingestion/SKILL.md`) is explicitly designed to have an in-session coding agent read PRs, issues, tickets, runbooks, and "web links" from a third-party source and write graph claims from them. Required metadata per write is "source refs, source authority, truth class, confidence" — again the epistemic fields, not a security-trust field. | **Verified directly** for the skill's stated purpose and required fields (first 60 lines read); **reported, not independently re-verified** for the specific claim that the full file contains no injection-risk warning anywhere. |
| I-4 | `POST /context/record` (API-key auth) | Turns submitted text directly into claims with `description`/`summary` fields; authenticated by API key, not by any check on the submitted content. | **Reported, not independently re-verified.** |

## Egress — how content leaves the graph toward an external agent

| ID | Channel | Confirmed leak | Confidence |
|---|---|---|---|
| E-1 | Nudge auto-push hooks (`SessionStart`/`PreToolUse`/`PostToolUse`/`Stop`) | `render_output()` (`cli/templates/claude_plugin/hooks/potpie_nudge.py:397-422`) injects `str(text)` into `additionalContext`/`systemMessage` with no fence or tag. Fires automatically, not on developer request. | **Verified directly** — `poc/injection_chain_repro.py` Stage 4 (Egress A), real import, executed. |
| E-2 | `potpie graph read --relations full` (CLI text) | `read_presenter.py` (`render_items_bullets`, `_format_relations_full_lines`) prints `fact` verbatim in plain text, meant for a human or a shelling-out agent to read from stdout. | **Verified directly** — `poc/injection_chain_repro.py` Stage 5 (Egress B), real import, executed. |
| E-3 | `potpie graph neighborhood --detail full` | `graph.py:1449-1466` (CLI command `graph_neighborhood`): with `--detail full`, returns `"properties": dict(n.properties)` for every node in the neighborhood, unfiltered. | **Verified directly** — read the exact function body. Not independently re-executed as a sixth PoC stage (would require standing up a graph backend); the source is unambiguous on its own. |
| E-4 | `potpie graph search-entities` | Returns entity `name`/`summary`/`description` plus `supporting_claims` carrying raw `fact` text. | **Reported, re-verified**: confirmed `claim_payload()` (the same function underlying E-1/E-2) is the shared source of these fields; did not separately trace the `search-entities` command's call path. |
| E-5 | Inline relations in `graph read` | `_assemble_inline_relation_items` places `entity.summary`/`entity.description` from entity properties, plus claim data, directly into the read payload. | **Reported, not independently re-verified.** |
| E-6 | Daemon HTTP UI (`/api/graph`, `/api/neighborhood`, `/api/read`, `/api/search`) | `daemon/http/ui/router.py:112-125` (`_slice_to_graph`): `properties = normalize_entity_properties(dict(n.properties), ...)`, included in the API response. `normalize_entity_properties` only normalizes `name`/`summary`/`description` shape — it does not strip or filter content. Gated by localhost + bearer token, which limits this to an agent/process already running on the same machine as the (already-compromised-in-effect) developer session. | **Verified directly** for the properties-dump behavior (read the exact function). **Reported, not independently re-verified** for the exact bearer-token gate mechanics. |
| E-7 | Context-engine HTTP API (`/context/graph/query`) | Same envelope shape as the CLI surfaces, no additional trust field; protected by API key. | **Reported, not independently re-verified.** |
| E-8 | Secondary stdout channels (`graph inbox list/show`, `graph quality *`, `timeline recent`, `graph history`) | Print claim summaries/facts verbatim as part of their normal output. | **Reported, not independently re-verified.** |

## Why two egress checks (E-1, E-2) are enough to establish the pattern

`RESEARCH.md` treats E-1 and E-2 as sufficient to answer "root cause vs.
stage" (Q5) because they are maximally different from each other — one is
a JSON envelope injected into an agent's context via a hook mechanism, the
other is human-readable text printed to a terminal — and yet both leak
identically from the same object. E-3 through E-8 are listed for
completeness and to size the actual attack surface, not because the core
claim needs all eight confirmed to hold.

## Legacy vector — checked, appears dead

The original March 2026 report's mechanism — a payload in a docstring,
picked up by `parsing/parsing/py_graph.py::create_graph()`, which embeds
the full raw text of a file onto its `FILE` node (`text=read_text(file_path)
or ""`, `py_graph.py:73-80`, verified directly) — still exists in the
repository. A repository-wide search for callers of `create_graph` outside
its own package (`parsing/`) returns none: `context-engine`, `daemon`,
`sandbox`, and `cli` do not import it. This is consistent with it being
orphaned/legacy code post-rewrite, not a live ingestion path. **Not claimed
as part of this finding.**

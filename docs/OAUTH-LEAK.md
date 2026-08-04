# Unauthenticated OAuth client secret disclosure — Issue #629

Kept deliberately separate from the trust-provenance finding in
`RESEARCH.md`. Different root cause (a missing auth decorator, not a
missing schema field), different fix, should not be blended into one
severity number.

## Summary

`GET /api/v1/integrations/debug/oauth-config` (and two neighboring debug
endpoints) returns the full `SENTRY_CLIENT_SECRET` value in plaintext, with
no authentication check, on the current `main` branch.

## Status, verified directly against live sources

| Fact | Evidence |
|---|---|
| Issue opened | `gh api repos/potpie-ai/potpie/issues/629` → `created_at: 2026-02-24T19:04:00Z`, `state: open` |
| Fix proposed | PR #630, "fix(security): remove unauthenticated debug endpoints that expose OAuth creds", opened same day |
| Fix status | `gh api repos/potpie-ai/potpie/pulls/630` → `"merged": false, "state": "open"` as of this research. **Not merged**, 5+ months after being opened. (An earlier AI-generated audit of this vendor claimed this PR had been merged — it had not; see `docs/CITATION-LOG.md`.) |
| Vulnerable code present on `main` | `potpie/integrations/integrations/adapters/inbound/http/integrations_router.py:2629-2693`, commit `b5a67742` |

## The vulnerable code

```python
# integrations_router.py:2629-2631
@router.get("/debug/oauth-config")
async def debug_oauth_config(
    integrations_service: IntegrationsService = Depends(get_integrations_service),
) -> Dict[str, Any]:
```

No `user: dict = Depends(AuthService.check_auth)` parameter — compare to a
neighboring, correctly-guarded endpoint in the same file:

```python
# integrations_router.py:2595-2596
    integrations_service: IntegrationsService = Depends(get_integrations_service),
    user: dict = Depends(AuthService.check_auth),
```

The handler body reads the configured secret directly from environment
config and returns it:

```python
client_secret = config("SENTRY_CLIENT_SECRET", default="")
...
"client_secret": {
    "value": client_secret,
    ...
}
```

Two neighboring endpoints, `/debug/test-token-exchange` (line 2702) and
`/debug/sentry-app-info` (line 2727), share the same missing-auth pattern.

## Bonus finding, same file family

`integrations_router.py` (Jira webhook handling, ~line 1806): JWT
verification is skipped entirely if `JIRA_CLIENT_SECRET` is unset — the
code's own comment marks this `(INSECURE!)`. Not independently re-verified
line-by-line for this writeup; flagged for anyone picking this up.

## Classification

CWE-306 (Missing Authentication for Critical Function) for the missing
`Depends(AuthService.check_auth)`; CWE-200 (Exposure of Sensitive
Information to an Unauthorized Actor) for the plaintext secret in the
response body. Not CWE-1427 — this has nothing to do with LLM prompting or
trust provenance; it's a conventional missing-auth bug that happens to sit
in the same file as an OAuth integration.

## Why this is in the repo at all

This isn't a finding the research set out to make. During source
verification for the provenance research (see `docs/CITATION-LOG.md`), an
earlier AI-generated audit of this vendor claimed PR #630 had already been
merged. Checking that claim directly against the GitHub API showed the
opposite: the fix was still unmerged, and the vulnerable endpoint was still
live on `main`. In other words, this isn't "stumbled onto a bug while doing
something else" — verifying one unrelated claim, on principle, produced an
independently confirmed live vulnerability. The root cause here (a missing
auth decorator) has nothing to do with the provenance finding this
repository is actually about, so it's kept separate rather than folded in
— but it's real, it's live, and the disclosure history (a proposed fix
sitting unmerged for 5+ months) is itself a relevant data point about this
vendor's remediation velocity — see `docs/ARCHITECTURE-DELTA.md`.

# Disclosure status

## The March 2026 finding (CWE-1427, mislabeled at the time as CWE-1387)

- **8 March 2026** — submitted to the vendor under a 30-day responsible
  disclosure window (deadline 8 April 2026), directly to `hello@potpie.ai`,
  and followed up 25 March 2026 by email and LinkedIn message to both
  co-founders individually.
- **8 April 2026 → present** — no response received on any channel: no
  acknowledgment, no issue opened on their tracker, no comment anywhere.
- Full timeline, including a CVE request that also went unanswered:
  [`potpie-graphrag-prompt-injection`](https://github.com/marsakahenry14-lab/potpie-graphrag-prompt-injection).
- Per standard responsible-disclosure practice (30–90 day windows are
  typical; Google Project Zero uses 90), this window has been closed for
  approximately four months. Publishing is consistent with normal industry
  practice for an unresponsive vendor.

## The new finding (trust-provenance loss) and the OAuth leak — published now, not pre-notified

Both the egress/trust-provenance finding (`RESEARCH.md`) and the
independently-surfaced OAuth leak (`docs/OAUTH-LEAK.md`) are published in
this repository without a separate private notification window beforehand.
Reasoning:

- Same vendor, same disclosure channel already established and already
  unresponsive for 5+ months on a directly related report — a second
  private attempt through the same channel has no reason to land
  differently, and delaying publication to test that again has limited
  value.
- The provenance finding's PoC (`poc/`) is synthetic and offline: it runs
  against vendored source snapshots and fabricated data, never against a
  live Potpie deployment, real repository, or real user's session. There's
  no working exploit against production being handed out here — the claim
  is architectural, and the evidence is a demonstrated data-flow property.
- The OAuth leak is a live, real bug in `potpie-ai/potpie`'s current `main`
  branch. That's a genuinely different risk profile from the provenance
  finding, and normally would argue for private notification first. It's
  published anyway, on the same reasoning as above (established channel,
  already unresponsive) — documented plainly here rather than left
  unstated, so the tradeoff is visible rather than hidden.

## What this repository does not do

- No exploit against a live Potpie deployment, real repository, or real
  user's data anywhere in this repository.
- `poc/` runs entirely offline against synthetic data and vendored source
  snapshots.
- `docs/OAUTH-LEAK.md` documents the bug with exact citations; it does not
  provide a ready-to-run exploitation script against production.

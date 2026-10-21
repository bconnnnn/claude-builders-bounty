# Supplemental real PR fetch evidence

These files are deterministic heuristic triage, NOT Claude-generated review outputs.
They establish that the live unauthenticated GitHub fetch and renderer completed
for two real public PRs on 2026-10-21. They do not satisfy the genuine Claude
sample gate. No target PR code or tests were executed.

- Flask #6168: drop support for Python 3.10; 12/12 files fetched, partial coverage
  because at least one GitHub patch was unavailable.
- Flask #5400: GitHub Actions dependency updates; 2/2 files fetched, no locally
  missing/truncated patches. GitHub patches still omit repository context.

See provenance.json for source/output SHA-256, base/head SHA and UTC timestamps.
The recorded command is the equivalent CLI invocation; collection called the
same GitHub.fetch and review functions to capture provenance in one process.

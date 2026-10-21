# Bounty readiness — 2026-10-21

Implementation work is prepared for review. **Do not submit as complete yet.**

| Requirement | Evidence/status |
| --- | --- |
| CLI accepts a public PR URL | Implemented; offline CLI tests and live fetch integration |
| Claude Code agent | Documented custom-agent definition selected with --agents + --agent; actual runtime NOT TESTED |
| Summary 2–3 sentences | Prompt and conservative validation; mocked contract tests |
| Risk and suggestion lists | Required one-line Markdown bullets; mocked contract tests |
| Low / Medium / High confidence | Exact-label validation; mocked contract tests |
| Two real PR sample outputs | Two genuine public PR fetches and HEURISTIC outputs; 0 genuine Claude outputs |
| Setup and usage README | Included with runtime requirements and honest limitations |
| Acceptance/payment | Not established; maintainers/platform decide |

Remaining blocker: install a compatible official Claude Code CLI in the isolated development account and authenticate that account legitimately. The current development account has neither. No root credentials should be copied.

Then run, from this directory:
    
    ./claude-review --pr https://github.com/pallets/flask/pull/6168 > samples/flask-6168.claude.md
    ./claude-review --pr https://github.com/pallets/flask/pull/5400 > samples/flask-5400.claude.md

Record exact source hash, CLI version, timestamps, PR base/head SHA before and after, command/exit status, output hashes and manual review. Discard failed or empty outputs. Inspect actual review accuracy and any unsafe model text; do not silently edit raw model output. A passing shape validator alone does not prove a good review.

The issue title mentions posting a comment, while listed criteria describe returned Markdown. This implementation prints stdout and performs no remote write; state that limitation in any future submission. It selects a custom agent directly and does not claim to have demonstrated nested parent-to-worker delegation.

The earlier audit in the parent directory describes the pre-improvement implementation. It is preserved as historical evidence; this file describes the reviewer subdirectory now.

# claude-review

A bounded public-GitHub PR reviewer driven by an actual Claude Code custom agent. It returns Markdown for human review: a 2–3 sentence summary, risk bullets, improvement bullets, and Low / Medium / High confidence.

**Submission status: not ready for bounty acceptance.** The implementation passes offline tests, and two real public PR fetches have supplemental heuristic outputs. Genuine Claude model runs are pending an installed, authenticated Claude Code CLI. These samples are not presented as Claude output.

## Quickstart

Requires Python 3.10+ and a separately installed, authenticated [Claude Code CLI](https://code.claude.com/docs/en/setup). No Python runtime dependencies.

```sh
cd solutions/pr-reviewer
./claude-review --pr https://github.com/pallets/flask/pull/6168
# Save the model-generated Markdown:
./claude-review --pr https://github.com/pallets/flask/pull/5400 > review.md
```

The source executable works without package installation. Optional `python3 -m pip install .` supplies the `claude-review` console command and may fetch setuptools. See [Claude authentication](https://code.claude.com/docs/en/authentication); the wrapper does not install Claude, configure billing, or manage credentials. Claude usage follows the invoking account's service terms and quota.

To exercise fetching and deterministic triage without Claude:

```sh
./claude-review --pr https://github.com/pallets/flask/pull/6168 --engine heuristic
python3 -B -m unittest discover -s tests -v
```

Heuristic mode is always explicit and labeled. Missing CLI, timeout, authentication/startup error, malformed output, or excessive output fails with exit 1; there is no silent engine fallback. Invalid CLI arguments exit 2. A generated review exits 0, including reviews with partial coverage or possible defects.

## Actual agent integration

The wrapper defines a `pr-reviewer` custom subagent through Claude Code's documented `--agents` JSON and selects that definition as the session agent with `--agent pr-reviewer`. This is a selected custom-agent session, not a claim that a parent model spawned a nested worker. The matching reusable definition is in [.claude/agents/pr-reviewer.md](.claude/agents/pr-reviewer.md).

All PR-controlled data travels on stdin as JSON; arguments and the agent prompt are fixed. Built-in tools are disabled (`--tools ''` and the agent's empty tool list), MCP is restricted to an empty configuration, commands/skills and persistence are disabled, and user/project/local setting sources are excluded. No permission-bypass flags are used. Claude starts in a private empty temporary working directory. Only PATH, HOME, locale, certificate path, TERM, and the invoking account's supported API-key/OAuth environment variables are inherited; unrelated secrets and service-endpoint overrides are excluded.

The CLI can still use its own authentication store under HOME, and machine-managed policy may apply. This wrapper is not an OS sandbox or a guarantee against a compromised Claude executable. Run under an ordinary dedicated account with a trusted Claude installation. No root credentials are required or copied.

Current official references: [CLI flags](https://code.claude.com/docs/en/cli-reference) and [custom subagents](https://code.claude.com/docs/en/sub-agents), checked 2026-10-21. Runtime CLI compatibility and actual model behavior remain unverified in this environment.

## Output contract and trust

Claude output must contain exactly Summary, Risks, Suggestions, Confidence level-two sections. The summary parser expects 2–3 ordinary English sentences separated by punctuation and whitespace; it is intentionally conservative and can reject abbreviations or unusual prose. Risk and suggestion sections must use one-line bullets. Confidence must be a single allowed label. HTML, images, code fences and control/format characters are rejected. This validates shape, not factual correctness. Findings need source inspection; no target code or tests are executed.

The final wrapper adds PR URL, head SHA, engine attribution and coverage. Model text remains untrusted source-derived content. Inspect it before rendering or posting. The tool prints stdout only; it does not post GitHub comments or perform any remote write.

## Fetch and runtime limits

- Canonical public `https://github.com/OWNER/REPO/pull/NUMBER` only. Queries, fragments, alternate hosts, credentials and ports are rejected.
- Only public GitHub PR metadata and files API endpoints are read. No GitHub credentials, Authorization headers, environment proxies, redirects or repository checkout.
- At most 3,000 files, 8 MiB per API response, 200,000 characters per patch, 2,000,000 characters across patches. Missing/locally truncated patches are declared partial; GitHub may omit context even with complete file coverage.
- Metadata is fetched again to detect a changed head/file count. This is not an atomic GitHub snapshot.
- Up to three HTTP attempts per request; short bounded retries for transient errors and rate limits. Socket timeout is 20 seconds; this is not an overall fetch deadline.
- Claude has a 120-second process wait timeout, plus bounded cleanup. Both stdout and stderr are limited to 128 KiB; an overflow terminates the child. Child stderr is never echoed.

## Evidence

[samples/provenance.json](samples/provenance.json) records timestamps, PR SHAs, coverage, output hashes and source hashes for two successful real API fetches. [Flask #6168](samples/flask-6168.heuristic.md) and [Flask #5400](samples/flask-5400.heuristic.md) are heuristic triage, not model reviews. No PR tests were run.

Offline tests cover API pagination/errors/rate limits, consistency checks, hostile data, engine selection, strict review validation, and the actual subprocess transport using a synthetic Python child (output caps, timeout, private cwd, environment filtering). Those child tests are not Claude tests.

To complete [bounty issue #4](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/4), run the default engine on two real PRs with genuine authenticated Claude, preserve raw outputs/provenance, inspect each result, and include those artifacts in the upstream PR. Acceptance and payment are controlled by the maintainers/platform; neither is established here.

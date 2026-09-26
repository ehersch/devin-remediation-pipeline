# 5-minute Loom script — Devin remediation pipeline on Apache Superset

**Tabs to have open, in this order**

0. `docs/architecture.png` from https://github.com/ehersch/devin-remediation-pipeline — full screen, this is your opening and closing frame
1. https://github.com/ehersch/superset/issues (label column visible)
2. The dashboard HTML (open the attachment locally)
3. https://app.devin.ai/sessions — one settled session with its structured output
4. https://github.com/ehersch/superset/pull/21 (the `-0.00` fix, diff tab)
5. https://github.com/ehersch/superset/pull/23 (Korean i18n, **Conversation** tab — shows the review round trip)
6. `devin_pipeline/pipeline/orchestrator.py` open in an editor at `monitor()`
7. https://github.com/ehersch/superset/actions — the dispatch run fired by the label event

Keep the diagram one keystroke away (a pinned tab): come back to it each time you
change columns, point at the box, then cut to the tab that proves it.

---

## 0:00–0:45 — What (problem framing)

"Every engineering org has a backlog of work that is *known*, *mechanical*, and *never prioritised*: dependency CVEs three levels deep in a lockfile, 1,154 broken i18n placeholders across 20 locales, product bugs with a clean reproduction. Superset has all three. Nobody staffs it, because each item is 30 minutes of tedium and the team has features to ship.

I built a control plane that turns each of those findings into an approved, tracked, verified pull request — with Devin as the worker, not as an assistant someone drives."

## 0:45–1:15 — How (the map)

**Tab 0, full screen.** Read it left to right in four sentences, one per column:

- "Four events drive everything, all of them GitHub Actions: a nightly scan, an issue getting labelled `devin-fix`, a 15-minute poll, and a PR's checks going red."
- "They all enter the same control plane — one Docker image, one CLI: detect and file, dispatch, monitor, feed back, and a ledger that is the only state in the system."
- "The worker is a Devin session. It has an id, so I can talk to it again later — that turns out to be the whole design."
- "And everything it does surfaces where the team already looks: issues, pull requests, and a dashboard rendered from the ledger."

Then: "Let me run the middle column."

## 1:15–2:30 — How (the demo)

- **Tab 1.** "Detectors run nightly — npm audit, OSV, a placeholder linter, and a mirror of upstream issues. They file issues in the fork, each carrying a machine-readable evidence block: a reproduction command and pass/fail acceptance criteria."
- Add the `devin-fix` label to an issue on camera. "That label is the event *and* the approval gate. GitHub's `issues.labeled` webhook fires the dispatch workflow." **Tab 7**: the run appears within seconds — no CLI, no human in the loop.
- **Tab 3.** "The workflow calls the Devin API, records the session id in a ledger, and comments the session link on the issue. The session gets the issue body plus a structured-output schema it must fill in: outcome, PR url, verification transcript, blockers."
- **Tab 4.** "Here is what came back for the `-0.00` bug — it mirrors d3's own sign-suppression rule and adds eleven parametrized cases, including the one where `+` mode must keep the sign."
- **Tab 2.** "And here is the answer to 'how would I know this is working': in flight, fixed with a PR, escalated, autonomous resolution rate, median time to settle, CI retries, and the verification transcript per session. All derived from the ledger, so a scheduled run, a local run, and the published page produce the same numbers."

## 2:30–3:30 — How (architecture, 3 decisions)

Back to **tab 0** for one beat each, then `orchestrator.py` for the third.

1. **The label is the gate.** Dispatch re-checks `devin-fix` on the issue itself, so a stray CLI call can't spend ACUs. Approval lives in GitHub, where the humans already are.
2. **Evidence, not vibes.** Every issue carries acceptance criteria; the session must return structured output; a session that can't reproduce the bug is labelled `needs-human` instead of inventing a fix. Point at the escalated row on the dashboard: "that's why the success rate isn't self-graded."
3. **The session is a durable worker, not a one-shot call.** (On the diagram: the three arrows into the same Devin box — dispatch, monitor, feed back.) When CI fails on a remediation PR, the `check_suite` event feeds the failing job logs back into *the same session*, which still has the whole context. Show tab 5: "I reviewed the Korean PR, sent the critique into the owning session, and it dropped the ignored build artifact and repaired 41 placeholders in place instead of blanking them. Same loop, human instead of CI."

## 3:30–4:20 — Why Devin specifically

"Three things here are not scriptable:

- The `po2json` upgrade crosses a major version — the CLI flags changed, so the build script had to change too. A Dependabot bump red-lines.
- The i18n work is 20 locales × ~60 strings of judgement about which translation to keep; six sessions ran in parallel and finished in the time one engineer fixes one locale.
- The `restore-version` issue couldn't be reproduced, and the session said so rather than shipping a plausible diff.

A deterministic bot can only do the first 10% of each of those. What makes the *system* work is that the agent is addressable: it has an id, a state, an inbox, and it reports in a schema I can put on a dashboard."

## 4:20–5:00 — When (next steps)

"In a real engagement I'd extend this along three axes:

1. **Source of events**: Snyk/Dependabot alerts, Jira tickets, Sentry regressions — the dispatcher only needs an issue with acceptance criteria.
2. **Policy**: per-wave ACU budgets, required reviewers by blast radius, auto-merge for the classes that carry a regression test.
3. **Feedback**: today CI failures loop back automatically; next is feeding *review* comments back the same way, so the PR converges without a human re-explaining.

The thing to take away: the unit of work isn't a prompt, it's a tracked session with an owner, a budget, and an acceptance test."

End on **tab 0** — every box on it is running today.

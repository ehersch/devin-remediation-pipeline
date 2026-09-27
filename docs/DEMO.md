# Start here — what this is, and what to show

## The point, in three sentences

Every engineering org carries work that is known, mechanical and never staffed:
CVEs buried three levels deep in a lockfile, 1,154 broken translation
placeholders, product bugs with a clean reproduction. This system turns each of
those findings into a GitHub issue carrying a reproduction and acceptance
criteria, lets a human approve it with a label, and hands it to a Devin session
that must reproduce the problem, fix it, prove the fix, and open a PR — or say
it could not. Everything it does lands where the team already looks: issues,
pull requests, and a dashboard that answers "is this working?" in one glance.

## What exists right now

| | |
|---|---|
| Solution repo (Docker + CLI + workflows) | https://github.com/ehersch/devin-remediation-pipeline |
| Superset fork with the issues | https://github.com/ehersch/superset/issues |
| Pinned "how to read this fork" issue | https://github.com/ehersch/superset/issues/34 |
| Remediation PRs Devin opened | https://github.com/ehersch/superset/pulls |
| Dashboard | `gh-pages` branch of the fork (`index.html`) |
| Architecture diagram | [`architecture.png`](architecture.png) |
| Full narration script | [`demo-script.md`](demo-script.md) |
| Hands-on runbook | [`WALKTHROUGH.md`](WALKTHROUGH.md) |

Live state at the time of writing: 13 issues dispatched, 12 with a merged-ready
PR, 1 escalated to a human, ~0.92 autonomous resolution rate, median 17.4
minutes from label to settled.

## The four labels (the whole state machine)

| Label | Meaning |
|---|---|
| *(none)* | A detector filed it. Nothing has been spent on it. |
| `devin-fix` | **Approved.** This label is the event that starts a session — added by a human, or by the standing policy when an evidence-backed issue is opened or in the nightly run (high-or-worse findings, at most `AUTO_APPROVE_LIMIT` per run and `MAX_IN_FLIGHT` live sessions, with a comment saying so). |
| `devin-working` | A session owns it; its URL is commented on the issue. |
| `devin-fixed` | The session returned a PR and the verification it ran. |
| `needs-human` | The session could not reproduce it, or refused to ship an unsafe fix. |

## The demo, in order

Five tabs. Roughly five minutes. Full wording per beat is in
[`demo-script.md`](demo-script.md) — this is just the click order.

**1. The diagram** — [`architecture.png`](architecture.png), full screen.
Four events on the left, one control plane in the middle, a Devin session as
the worker, observable output on the right. One sentence per column.

**2. The issues** — https://github.com/ehersch/superset/issues
Open https://github.com/ehersch/superset/issues/18 and scroll to the evidence
block: the reproduction command and the pass/fail acceptance criteria the
session has to satisfy. *"A detector filed this. Nothing has been spent on it
yet."*

**3. Fire the event, on camera** — on that same issue: right sidebar →
**Labels** → check `devin-fix` → click outside the dropdown.
Cut to https://github.com/ehersch/superset/actions — a `devin-pipeline /
dispatch` run appears within seconds, triggered by `issues`. Back on the issue:
a bot comment with the `app.devin.ai/sessions/...` link, and the label has
flipped to `devin-working`. *No CLI, no human in the loop.*

**4. What came back** — don't wait for this session live; show one that already
settled:
- https://github.com/ehersch/superset/pull/21 — the `-0.00` report bug. Mirrors
  d3's own sign-suppression rule and adds 11 parametrized cases, including the
  one where `+` mode must keep the sign.
- https://github.com/ehersch/superset/pull/22 — the `po2json` critical RCE
  chain. Crosses a major version, so the CLI invocation had to change too: a
  Dependabot bump red-lines here.
- https://github.com/ehersch/superset/pull/23, **Conversation** tab — the
  Korean i18n PR. I reviewed it, sent the critique back into the *owning
  session*, and it dropped a gitignored build artifact and repaired 41
  placeholders in place instead of blanking 118. Same loop CI failures use.

**5. The dashboard** — the answer to *"how would I know this is working?"*:
in flight / fixed with a PR / escalated / autonomous resolution rate / median
time to settle / CI retries, a throughput chart, and per issue the session, the
PR, and the verification transcript it ran.

Land on the escalated row — https://github.com/ehersch/superset/issues/13,
where the session could not reproduce the failing tests on a clean checkout and
opened nothing. *"The success rate isn't self-graded: that is the one it
refused to fake."*

**6. The best 30 seconds, if you have them — answering an escalation.**
Issue https://github.com/ehersch/superset/issues/12 also came back unfixed, but
with a question rather than a diff: every paramiko `<= 4.0.0` carries the
advisory, and 5.0.0 removes `DSSKey`, which `sshtunnel` calls unconditionally.
Shim it, replace sshtunnel, or accept the risk? I answered *shim it* in the
session — no re-run, no new issue, just a reply to the agent that still held the
context — and it came back with https://github.com/ehersch/superset/pull/33:
the shim, the upgrade, tests on both paramiko 3.x and 5.x, and the `UPDATING.md`
note for dropped DSA support. Superset's own CI is green on it. The next poll
cleared `needs-human`, labelled the issue `devin-fixed`, and moved the
dashboard row — nobody touched the pipeline.

*"That is the shape of the whole thing: escalation is a question to a worker
that is still alive, not a dead end."*

## Gotchas while filming

- **Don't wait on the schedule.** The 15-minute poll settles sessions, but on
  camera settle it by hand: Actions → *devin-pipeline / dispatch* →
  **Run workflow**. That same run also republishes the dashboard.
- **A session takes ~10 minutes to settle.** Label on camera, then cut to an
  already-settled PR; come back at the end if you want to show it landed.
- **The dashboard is a static file** on the `gh-pages` branch. Enabling
  Settings → Pages → `gh-pages` gives you a URL to show instead of a local file.
- **Unlabelled issues are the point, not a gap.** `#9, #10, #17, #19, #20` sit
  detected and unapproved: a detector can file freely, but nothing spends money
  until the issue is labelled — by a human on camera, or by the standing
  policy (on `issues.opened` and in the nightly run), which approves a bounded
  number itself and comments the decision on the issue. Those five predate the
  policy, so they stay put until the nightly run picks them up; set the
  repository variable `AUTO_APPROVE_LIMIT` to `0` if you want them untouched
  until you film. A fresh issue with a valid evidence block, on the other hand,
  gets a session within a minute of being opened.

## If someone asks "why Devin and not a script?"

- The `po2json` upgrade crosses a major version — the flags changed, so the
  build script had to change with it.
- The i18n work is 20 locales × ~60 strings of judgement about which
  translation to keep; six sessions ran in parallel and finished in the time one
  engineer fixes one locale.
- Two issues came back unfixed *with reasons* rather than with a plausible diff
  — and one of them shipped as soon as a human answered the question, inside
  the same session.

The system works because the agent is addressable: it has an id, a state, an
inbox and a reporting schema — so CI failures and review comments go back to the
session that holds the context, instead of starting over.

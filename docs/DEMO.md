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
| Remediation PRs Devin opened | https://github.com/ehersch/superset/pulls |
| Dashboard | `gh-pages` branch of the fork (`index.html`) |
| Architecture diagram | [`architecture.png`](architecture.png) |
| Full narration script | [`demo-script.md`](demo-script.md) |
| Hands-on runbook | [`WALKTHROUGH.md`](WALKTHROUGH.md) |

Live state at the time of writing: 13 issues dispatched, 11 with a merged-ready
PR, 2 escalated to a human, ~0.85 autonomous resolution rate, median 10.7
minutes from label to settled.

## The four labels (the whole state machine)

| Label | Meaning |
|---|---|
| *(none)* | A detector filed it. Nothing has been spent on it. |
| `devin-fix` | **A human approved it.** This label is the event that starts a session. |
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

Land on the two escalated rows — https://github.com/ehersch/superset/issues/13
(could not reproduce) and https://github.com/ehersch/superset/issues/12
(paramiko: the only unaffected release removes an API `sshtunnel` depends on).
*"The success rate isn't self-graded: those are the two it refused to fake."*

## Gotchas while filming

- **Scheduled workflows are disabled on forks.** The 15-minute poll that settles
  sessions will not fire by itself. After labelling, settle it by hand:
  Actions → *devin-pipeline / dispatch* → **Run workflow**. That same run also
  republishes the dashboard.
- **A session takes ~10 minutes to settle.** Label on camera, then cut to an
  already-settled PR; come back at the end if you want to show it landed.
- **The dashboard is a static file** on the `gh-pages` branch. Enabling
  Settings → Pages → `gh-pages` gives you a URL to show instead of a local file.
- **Unlabelled issues are the point, not a gap.** `#9, #10, #17, #19, #20` sit
  detected and unapproved: a detector can file freely, but nothing spends money
  until a human labels it.

## If someone asks "why Devin and not a script?"

- The `po2json` upgrade crosses a major version — the flags changed, so the
  build script had to change with it.
- The i18n work is 20 locales × ~60 strings of judgement about which
  translation to keep; six sessions ran in parallel and finished in the time one
  engineer fixes one locale.
- Two issues came back unfixed *with reasons* rather than with a plausible diff.

The system works because the agent is addressable: it has an id, a state, an
inbox and a reporting schema — so CI failures and review comments go back to the
session that holds the context, instead of starting over.

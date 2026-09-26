<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->
# Run it yourself

Six steps, in order. Steps 1–3 need nothing but Docker and cost nothing; step 4
spends a Devin session; steps 5–6 read what the system has already produced.

Every command below has been run as written.

```bash
git clone https://github.com/ehersch/devin-remediation-pipeline.git
git clone https://github.com/ehersch/superset.git      # the repository it operates on
cd devin-remediation-pipeline
docker build -t devin-pipeline .
```

---

## 1. See what the detectors find (no credentials, no writes)

```bash
docker run --rm -v "$PWD/../superset:/repo:ro" devin-pipeline --dry-run detect
```

Each line is a candidate issue: severity, fingerprint, title. The fingerprint is
a hash of the thing being fixed — it is what makes filing idempotent, so a
nightly scan updates an existing issue instead of opening a second one.

Narrow to one detector and read the whole finding:

```bash
docker run --rm -v "$PWD/../superset:/repo:ro" devin-pipeline \
  --dry-run detect --only i18n_placeholders --json | head -40
```

Look at `reproduction` and `acceptance`. **This is the load-bearing idea of the
whole system**: a finding is only admitted if a command can decide whether it is
fixed. Those two strings become the issue checklist, the session prompt, and the
bar the session has to clear before it is allowed to report `fixed`.

The five detectors are `npm_audit`, `osv_python`, `i18n_placeholders`,
`engine_spec_metadata` and `upstream_mirror`.

## 2. Read a filed issue

<https://github.com/ehersch/superset/issues/8> — scroll to the bottom and view
the raw markdown (`…` menu → Edit, or append `.md`). The HTML comment
`<!-- devin-pipeline:evidence {...} -->` carries the fingerprint, reproduction
and acceptance criteria as JSON.

The dispatcher reads that block back **off the issue**, so a hand-written issue
with a valid block is dispatched by exactly the same code path as a detected
one, and an issue without one is refused rather than turned into a vague prompt.

## 3. Rehearse the full loop with no spend

```bash
export GITHUB_TOKEN=ghp_...        # a read-only PAT is enough here
docker run --rm -e GITHUB_TOKEN -e TARGET_REPO=ehersch/superset \
  -v "$PWD/../superset:/repo:ro" -v "$PWD/.state:/state" \
  devin-pipeline -v --dry-run run
```

`--dry-run` turns every write — issue, comment, label, **and session creation** —
into a log line, so you can watch detect → file → gate → dispatch → poll without
touching GitHub or spending an ACU.

Note the gate in the log: issues without `devin-fix` are skipped, and so are
issues labelled `needs-human`. Dispatch re-checks the label on the issue itself,
so a stray CLI call cannot start a session a human did not approve.

(Dry-run still *reads* GitHub — without a token you get `401: Bad credentials`.
Step 1 is the only credential-free step.)

## 4. Fire the real event

This is the demo. In <https://github.com/ehersch/superset/issues>, add the
**`devin-fix`** label to an open issue that is not already labelled
`devin-working` or `devin-fixed`.

Then watch, in this order:

1. <https://github.com/ehersch/superset/actions> — a *Devin pipeline dispatch*
   run appears within seconds, triggered by `issues.labeled`.
2. The issue — a comment lands with the session URL and the ACU cap, and the
   label flips to `devin-working`.
3. The session URL — Devin reproducing the bug, fixing it, then running the
   acceptance command.
4. The issue again, within ~15 minutes — the scheduled poll settles it: outcome
   comment, `devin-fixed` (with a PR link) or `needs-human`.

Nothing in that sequence involves a human after the label. The label *is* the
approval, and it is the only approval.

To drive the same thing from your machine instead of from Actions:

```bash
docker run --rm -e GITHUB_TOKEN -e DEVIN_API_KEY \
  -e TARGET_REPO=ehersch/superset \
  -v "$PWD/../superset:/repo:ro" -v "$PWD/.state:/state" \
  devin-pipeline -v dispatch --issue 16
docker run --rm ... devin-pipeline monitor     # settle whatever has finished
```

## 5. Rebuild the dashboard from the ledger

The ledger is a JSON file on the `devin-pipeline-state` branch of the fork — one
commit per write. Everything observable is derived from it, so you can rebuild
the status page yourself with **no credentials at all**:

```bash
cd ../superset
git fetch origin devin-pipeline-state
git show origin/devin-pipeline-state:state.json > /tmp/state.json

cd ../devin-remediation-pipeline
pip install -r devin_pipeline/requirements.txt
PIPELINE_STATE=/tmp/state.json python -m devin_pipeline.pipeline.cli metrics
PIPELINE_STATE=/tmp/state.json python -m devin_pipeline.pipeline.cli dashboard --out /tmp/index.html
open /tmp/index.html
```

`metrics` prints the same numbers the workflow publishes:

```json
{"issues_tracked": 11, "dispatched": 11, "in_flight": 2, "settled": 9,
 "fixed_with_pr": 8, "escalated": 1, "not_reproducible": 1,
 "autonomous_resolution_rate": 0.889, "median_minutes_to_settle": 10.6}
```

The escalated row is the one worth staring at: that session could not reproduce
its bug and said so. The resolution rate is not self-graded.

## 6. Make CI talk back to the session

Open a remediation PR (e.g. <https://github.com/ehersch/superset/pull/22>) and
push a commit that breaks a test. When the check suite fails, the
`devin-pipeline-ci-feedback` workflow finds the session that opened that PR in
the ledger and messages **that same session** with the failing job — it still
has the full context of its own change. The retry budget (`MAX_CI_RETRIES`,
default 2) is enforced in the ledger; when it is exhausted the issue is
escalated to `needs-human` instead of looping.

You can invoke that path directly:

```bash
docker run --rm -e GITHUB_TOKEN -e DEVIN_API_KEY -e TARGET_REPO=ehersch/superset \
  -v "$PWD/.state:/state" devin-pipeline \
  ci-failure --pr-url https://github.com/ehersch/superset/pull/22 --head-sha <sha>
```

---

## What to take away

| Step | The point |
| --- | --- |
| 1 | a finding is only automatable if a script can verify the fix |
| 2 | the issue is the API — evidence in, prompt out |
| 3 | the label is the approval gate, enforced at dispatch, not in the UI |
| 4 | the event chain runs with no human after the label |
| 5 | every number comes from one auditable ledger |
| 6 | the session is addressable after it finishes — that is the unlock |

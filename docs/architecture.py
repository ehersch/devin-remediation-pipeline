#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Render the architecture diagram.

    python docs/architecture.py        # writes docs/architecture.{svg,png}
"""

from __future__ import annotations

from pathlib import Path

from graphviz import Digraph

INK = "#1f2933"
MUTED = "#6b7785"
EVENT = "#fde68a"
PLANE = "#bfdbfe"
DEVIN = "#c7d2fe"
OUTPUT = "#bbf7d0"
GATE = "#fecaca"

OUT = Path(__file__).resolve().parent / "architecture"


def build() -> Digraph:
    g = Digraph("architecture", format="svg")
    g.attr(
        rankdir="LR",
        splines="spline",
        newrank="true",
        nodesep="0.45",
        ranksep="1.0",
        bgcolor="white",
        fontname="Helvetica",
        labelloc="t",
        label=(
            "Devin remediation pipeline — event-driven control plane "
            "over the Devin API"
        ),
        fontsize="20",
        fontcolor=INK,
    )
    g.attr(
        "node",
        shape="box",
        style="filled,rounded",
        fontname="Helvetica",
        fontsize="12",
        color="#00000000",
        fontcolor=INK,
        margin="0.18,0.12",
    )
    g.attr("edge", fontname="Helvetica", fontsize="10", color=MUTED, fontcolor=MUTED)

    with g.subgraph(name="cluster_events") as c:
        c.attr(
            label="Events (GitHub Actions)",
            style="rounded",
            color="#d8dee6",
            fontname="Helvetica",
            fontsize="13",
            fontcolor=MUTED,
        )
        c.node("schedule", "nightly schedule\nscan", fillcolor=EVENT)
        c.node("labeled", "issues.labeled\n`devin-fix`", fillcolor=EVENT)
        c.node("poll", "every 15 min\npoll", fillcolor=EVENT)
        c.node("checks", "check_suite\nfailure", fillcolor=EVENT)
        c.attr(rank="same")

    with g.subgraph(name="cluster_plane") as c:
        c.attr(
            label="Control plane  (Docker image / python -m devin_pipeline.pipeline.cli)",
            style="rounded",
            color="#d8dee6",
            fontname="Helvetica",
            fontsize="13",
            fontcolor=MUTED,
        )
        c.node(
            "detect",
            "detectors\nnpm audit · OSV · i18n placeholders\nengine specs · upstream mirror",
            fillcolor=PLANE,
        )
        c.node(
            "file",
            "issue filer\nembeds evidence block:\nfingerprint · repro · acceptance",
            fillcolor=PLANE,
        )
        c.node(
            "gate",
            "approval gate\nlabel present?  ACU + dispatch budget?",
            fillcolor=GATE,
        )
        c.node("dispatch", "dispatcher\nprompt from the evidence block", fillcolor=PLANE)
        c.node(
            "monitor",
            "monitor\nsettles on structured output",
            fillcolor=PLANE,
        )
        c.node(
            "feedback",
            "CI feedback\nfailing checks → owning session",
            fillcolor=PLANE,
        )
        c.node(
            "ledger",
            "ledger (JSON on a branch)\nissue → attempts → session id,\noutcome, PR, timings",
            shape="cylinder",
            fillcolor="#e5e7eb",
        )
        c.attr(rank="same")

    g.node(
        "devin",
        "Devin API\nPOST /v1/sessions\nGET  /v1/session/{id}\nPOST /v1/session/{id}/message",
        fillcolor=DEVIN,
    )
    g.node(
        "session",
        "Devin session\nreproduce → fix →\nrun acceptance criteria →\nreport structured outcome",
        fillcolor=DEVIN,
    )

    with g.subgraph(name="cluster_out") as c:
        c.attr(
            label="Observable output",
            style="rounded",
            color="#d8dee6",
            fontname="Helvetica",
            fontsize="13",
            fontcolor=MUTED,
        )
        c.node("issues", "issues in the fork\n+ session-url comments", fillcolor=OUTPUT)
        c.node("prs", "pull requests\n(fix + the test that proves it)", fillcolor=OUTPUT)
        c.node(
            "labels",
            "labels\ndevin-working / devin-fixed / needs-human",
            fillcolor=OUTPUT,
        )
        c.node(
            "dash",
            "dashboard + metrics\nresolution rate · time to settle ·\nthroughput · escalations",
            fillcolor=OUTPUT,
        )
        c.attr(rank="same")

    g.edge("schedule", "detect")
    g.edge("labeled", "gate", label="human approval")
    g.edge("poll", "monitor")
    g.edge("checks", "feedback", label="failed PR checks")

    g.edge("detect", "file", label="findings", constraint="false")
    g.edge("gate", "dispatch", label="pass", constraint="false")

    g.edge("dispatch", "devin", label="create session")
    g.edge("monitor", "devin", label="read status +\nstructured output")
    g.edge("feedback", "devin", label="message the\nsame session")
    g.edge("devin", "session")

    g.edge("dispatch", "ledger", label="session id", style="dotted", constraint="false")
    g.edge("monitor", "ledger", style="dotted", constraint="false")
    g.edge(
        "ledger",
        "feedback",
        label="PR → owning session",
        style="dotted",
        constraint="false",
    )

    g.edge("file", "issues", label="files")
    g.edge("monitor", "issues", label="comments outcome")
    g.edge("monitor", "labels", label="settles")
    g.edge("gate", "labels", label="blocked → needs-human", style="dashed")
    g.edge("session", "prs", label="opens")
    g.edge("ledger", "dash", label="rendered from")
    return g


def main() -> None:
    graph = build()
    graph.render(OUT, format="svg", cleanup=True)
    graph.render(OUT, format="png", cleanup=True)
    print(f"wrote {OUT}.svg and {OUT}.png")


if __name__ == "__main__":
    main()

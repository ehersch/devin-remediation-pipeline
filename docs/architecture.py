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

INK = "#111827"
MUTED = "#7b8794"
LINE = "#9aa5b1"
EVENT = "#fde68a"
PLANE = "#bfdbfe"
DEVIN = "#c7b2fd"
OUTPUT = "#a7f3d0"
STORE = "#e5e7eb"

OUT = Path(__file__).resolve().parent / "architecture"


def label(title: str, subtitle: str = "") -> str:
    """A bold title with an optional muted second line."""
    if not subtitle:
        return f"<<b>{title}</b>>"
    return (
        f'<<b>{title}</b><br/><font point-size="10" color="{MUTED}">'
        f"{subtitle}</font>>"
    )


def build() -> Digraph:
    g = Digraph("architecture", format="svg")
    g.attr(
        rankdir="LR",
        splines="spline",
        nodesep="0.5",
        ranksep="1.4",
        bgcolor="white",
        fontname="Helvetica",
        margin="0.2",
    )
    g.attr(
        "node",
        shape="box",
        style="filled,rounded",
        fontname="Helvetica",
        fontsize="13",
        penwidth="0",
        fontcolor=INK,
        height="0.7",
        margin="0.24,0.16",
    )
    g.attr(
        "edge",
        fontname="Helvetica",
        fontsize="10",
        color=LINE,
        fontcolor=MUTED,
        arrowsize="0.7",
        penwidth="1.1",
    )

    def cluster(name: str, title: str, nodes: list[tuple[str, str, str, str]]) -> None:
        with g.subgraph(name=f"cluster_{name}") as c:
            c.attr(
                label=f"  {title}  ",
                labeljust="l",
                style="rounded",
                color="#dfe3e8",
                fontname="Helvetica",
                fontsize="11",
                fontcolor=MUTED,
                margin="16",
            )
            for key, title_, subtitle, fill in nodes:
                shape = "cylinder" if key == "ledger" else "box"
                c.node(key, label(title_, subtitle), fillcolor=fill, shape=shape)
            c.attr(rank="same")

    cluster(
        "events",
        "EVENTS · GitHub Actions",
        [
            ("scan", "nightly schedule", "", EVENT),
            ("labeled", "issue labeled devin-fix", "", EVENT),
            ("poll", "poll every 15 min", "", EVENT),
            ("ci", "PR checks failed", "", EVENT),
        ],
    )
    cluster(
        "plane",
        "CONTROL PLANE · one Docker image",
        [
            ("detect", "Detect &amp; file", "evidence: repro + acceptance", PLANE),
            ("dispatch", "Dispatch", "approval gate, ACU budget", PLANE),
            ("monitor", "Monitor", "settle on structured outcome", PLANE),
            ("feedback", "Feed back", "failing checks → same session", PLANE),
            ("ledger", "Ledger", "issue → session → outcome", STORE),
        ],
    )
    cluster(
        "devin",
        "DEVIN",
        [("session", "Devin session", "reproduce → fix → verify", DEVIN)],
    )
    cluster(
        "out",
        "OBSERVABLE OUTPUT",
        [
            ("issues", "Issues", "session links, status labels", OUTPUT),
            ("prs", "Pull requests", "fix + the test that proves it", OUTPUT),
            ("dash", "Dashboard", "resolution rate, throughput", OUTPUT),
        ],
    )

    g.edge("scan", "detect")
    g.edge("labeled", "dispatch")
    g.edge("poll", "monitor")
    g.edge("ci", "feedback")

    g.edge("detect", "issues", label="files")
    g.edge("dispatch", "session", label="create session")
    g.edge("monitor", "session", label="read outcome", style="dashed")
    g.edge("feedback", "session", label="message")
    g.edge("session", "prs", label="opens")
    g.edge("monitor", "issues", label="comment + label")
    g.edge("ledger", "dash", label="rendered from")

    g.edge("dispatch", "ledger", style="dotted", constraint="false")
    g.edge("monitor", "ledger", style="dotted", constraint="false")
    g.edge("ledger", "feedback", style="dotted", constraint="false")
    return g


def main() -> None:
    graph = build()
    graph.render(OUT, format="svg", cleanup=True)
    graph.render(OUT, format="png", cleanup=True)
    print(f"wrote {OUT}.svg and {OUT}.png")


if __name__ == "__main__":
    main()

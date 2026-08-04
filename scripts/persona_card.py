#!/usr/bin/env python3
"""Render an animated "persona blend" card from live GitHub activity.

RIDGE (IEEE CoG 2026) runs one PPO agent whose behaviour comes from four persona
reward weights blended by smooth sigmoids over a game-state vector. This script
does the same thing with the author as the agent: four real GitHub signals become
a game-state vector, the same sigmoid blend turns them into persona weights, and
the result is drawn as an animated SVG.

No third-party dependencies — urllib and the standard library only, so the workflow
needs no install step. Everything is deterministic given the same API response.

Usage:
    GITHUB_TOKEN=... python scripts/persona_card.py --user Al-Scripting --out persona-card.svg
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

GRAPHQL = "https://api.github.com/graphql"

# One query for everything: contribution totals drive three of the four personas,
# and the repository sample supplies language breadth for the fourth.
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER],
                 isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        primaryLanguage { name }
      }
    }
  }
}
"""


@dataclass
class Persona:
    """One persona: a label, the real signal behind it, and its blended weight."""

    key: str
    label: str
    signal: str          # human-readable description of what drives it
    raw: float           # the underlying count
    weight: float = 0.0  # sigmoid-blended, 0..1


def fetch(login: str, token: str) -> dict:
    """Run the GraphQL query and return the `user` object."""
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    request = urllib.request.Request(
        GRAPHQL,
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "persona-card",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]["user"]


def current_streak(weeks: list[dict]) -> int:
    """Consecutive days with at least one contribution, counting back from today.

    Today contributing nothing yet is not a broken streak, so a zero on the most
    recent day is skipped once before counting starts.
    """
    days = [day for week in weeks for day in week["contributionDays"]]
    days.sort(key=lambda day: day["date"])
    streak = 0
    for index, day in enumerate(reversed(days)):
        if day["contributionCount"] > 0:
            streak += 1
        elif index == 0:
            continue  # today may simply not have happened yet
        else:
            break
    return streak


def sigmoid(x: float, midpoint: float, steepness: float) -> float:
    """The blending curve RIDGE uses: smooth, bounded, saturating.

    `midpoint` is the raw value that maps to 0.5, and `steepness` controls how
    sharply the weight climbs around it. Overflow on extreme inputs is clamped
    rather than raised, so an unusually busy year cannot crash the render.
    """
    exponent = -steepness * (x - midpoint)
    if exponent > 60:
        return 0.0
    if exponent < -60:
        return 1.0
    return 1.0 / (1.0 + math.exp(exponent))


def build_personas(user: dict) -> tuple[list[Persona], dict]:
    """Map live GitHub signals onto the four RIDGE personas.

    The midpoints below are the honest part of this card: each is a plausible
    "solid year" value for that signal, so a weight near 0.5 means typical and a
    weight near 1.0 means genuinely high. They are not tuned to flatter anyone.
    """
    contributions = user["contributionsCollection"]
    repositories = user["repositories"]["nodes"]
    calendar = contributions["contributionCalendar"]

    languages = {
        repository["primaryLanguage"]["name"]
        for repository in repositories
        if repository.get("primaryLanguage")
    }
    stars = sum(repository["stargazerCount"] for repository in repositories)
    streak = current_streak(calendar["weeks"])

    personas = [
        Persona(
            "explorer",
            "EXPLORER",
            f"{len(languages)} languages · {contributions['totalRepositoriesWithContributedCommits']} repos touched",
            len(languages) + contributions["totalRepositoriesWithContributedCommits"],
        ),
        Persona(
            "craftsman",
            "CRAFTSMAN",
            f"{contributions['totalCommitContributions']} commits this year",
            contributions["totalCommitContributions"],
        ),
        Persona(
            "survivor",
            "SURVIVOR",
            f"{streak}-day streak · {calendar['totalContributions']} contributions",
            streak * 6 + calendar["totalContributions"] / 12,
        ),
        Persona(
            "warrior",
            "WARRIOR",
            f"{contributions['totalPullRequestContributions']} PRs · "
            f"{contributions['totalIssueContributions']} issues · "
            f"{contributions['totalPullRequestReviewContributions']} reviews",
            contributions["totalPullRequestContributions"]
            + contributions["totalIssueContributions"]
            + contributions["totalPullRequestReviewContributions"],
        ),
    ]

    midpoints = {"explorer": 18, "craftsman": 420, "survivor": 60, "warrior": 40}
    steepness = {"explorer": 0.16, "craftsman": 0.006, "survivor": 0.045, "warrior": 0.06}
    for persona in personas:
        persona.weight = sigmoid(persona.raw, midpoints[persona.key], steepness[persona.key])

    facts = {
        "total": calendar["totalContributions"],
        "streak": streak,
        "stars": stars,
        "repos": user["repositories"]["totalCount"],
        "languages": len(languages),
    }
    return personas, facts


# --------------------------------------------------------------------------- render

# Four columns that must not collide: label | signal | bar | value, with the
# sigmoid glyph parked in its own gutter on the right.
WIDTH, HEIGHT = 900, 300
LABEL_X, SIGNAL_X = 34, 132
BAR_X, BAR_W, BAR_H = 344, 286, 13
GLYPH_X, GLYPH_W = 706, 160
ROW_Y, ROW_GAP = 112, 40

RED, DIM, INK, BG = "#E5484D", "#8B949E", "#E6EDF3", "#0D1117"


def bar(index: int, persona: Persona) -> str:
    """One persona row: label, animated fill, live weight readout."""
    y = ROW_Y + index * ROW_GAP
    filled = max(6.0, BAR_W * persona.weight)
    delay = 0.35 + index * 0.16

    # Opacity starts at 1 and SMIL animates it *from* 0. Content must never be
    # hidden behind an animation that might not run: GitHub serves README images
    # through camo as <img>, where CSS @keyframes are unreliable but SMIL works.
    return f"""
  <g class="row">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s"
             begin="{max(0.0, delay - 0.3):.2f}s" fill="freeze"/>
    <text x="{LABEL_X}" y="{y + 10}" class="plabel">{persona.label}</text>
    <text x="{SIGNAL_X}" y="{y + 10}" class="psig">{persona.signal}</text>
    <rect x="{BAR_X}" y="{y}" width="{BAR_W}" height="{BAR_H}" rx="6" class="track"/>
    <rect x="{BAR_X}" y="{y}" width="{filled:.1f}" height="{BAR_H}" rx="6" class="fill">
      <animate attributeName="width" from="0" to="{filled:.1f}"
               dur="1.1s" begin="{delay:.2f}s" fill="freeze"
               calcMode="spline" keySplines="0.16 1 0.3 1" keyTimes="0;1"/>
    </rect>
    <text x="{BAR_X + BAR_W + 14}" y="{y + 11}" class="pval">{persona.weight:.2f}</text>
  </g>"""


def sigmoid_glyph() -> str:
    """A small sigmoid curve with a dot travelling it — the blend function itself."""
    top, bottom = 140, 236  # kept clear of the bar column and the footer rule
    points = []
    for step in range(49):
        t = step / 48
        x = GLYPH_X + t * GLYPH_W
        y = bottom - sigmoid(t * 12 - 6, 0, 1) * (bottom - top)
        points.append(f"{x:.1f},{y:.1f}")
    path = "M" + " L".join(points)
    return f"""
  <g opacity="0.95">
    <text x="{GLYPH_X}" y="{top - 16}" class="glabel">blend σ(w·s)</text>
    <line x1="{GLYPH_X}" y1="{bottom + 7}" x2="{GLYPH_X + GLYPH_W}" y2="{bottom + 7}"
          stroke="#21262D" stroke-width="1"/>
    <path d="{path}" class="curve"/>
    <circle r="3.5" class="dot">
      <animateMotion dur="3.4s" repeatCount="indefinite" path="{path}"
                     calcMode="spline" keySplines="0.4 0 0.6 1" keyTimes="0;1"/>
    </circle>
  </g>"""


def render(personas: list[Persona], facts: dict, login: str) -> str:
    """Assemble the whole card. Pure string building — no templating dependency."""
    rows = "".join(bar(index, persona) for index, persona in enumerate(personas))
    dominant = max(personas, key=lambda persona: persona.weight)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" role="img"
     aria-label="Live persona blend for {login}: dominant persona {dominant.label}">
  <title>{login} — live persona blend</title>
  <style>
    text {{ font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .frame {{ fill: {BG}; stroke: {RED}; stroke-opacity: 0.55; stroke-width: 1.5; }}
    .chrome {{ fill: #161B22; }}
    .title {{ fill: {RED}; font-size: 17px; font-weight: 700; letter-spacing: 1.5px; }}
    .sub {{ fill: {DIM}; font-size: 10.5px; letter-spacing: 0.4px; }}
    .plabel {{ fill: {INK}; font-size: 12px; font-weight: 700; letter-spacing: 1.2px; }}
    .psig {{ fill: {DIM}; font-size: 9.5px; }}
    .pval {{ fill: {RED}; font-size: 12px; font-weight: 700; }}
    .track {{ fill: #21262D; }}
    .fill {{ fill: url(#grad); }}
    .curve {{ fill: none; stroke: {RED}; stroke-width: 1.6; stroke-opacity: 0.8; }}
    .dot {{ fill: {RED}; }}
    .glabel {{ fill: {DIM}; font-size: 9px; letter-spacing: 0.6px; }}
    .foot {{ fill: {DIM}; font-size: 9.5px; }}
    .accent {{ fill: {RED}; font-size: 9.5px; font-weight: 700; }}
    .row {{ opacity: 1; }}
  </style>
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8E2429"/>
      <stop offset="100%" stop-color="{RED}"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="12" class="frame"/>
  <path d="M1 13 a12 12 0 0 1 12-12 h{WIDTH - 26} a12 12 0 0 1 12 12 v19 h-{WIDTH - 2} z" class="chrome"/>
  <circle cx="24" cy="17" r="4.5" fill="{RED}"/>
  <circle cx="40" cy="17" r="4.5" fill="#3D444D"/>
  <circle cx="56" cy="17" r="4.5" fill="#3D444D"/>
  <text x="{WIDTH / 2}" y="21" class="sub" text-anchor="middle">al@oshawa: ~/ridge --live</text>

  <text x="34" y="62" class="title">PERSONA BLEND</text>
  <text x="34" y="80" class="sub">state-conditioned reward weights, recomputed from live activity<tspan> _<animate
    attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></tspan></text>

{rows}
{sigmoid_glyph()}

  <line x1="34" y1="266" x2="{WIDTH - 34}" y2="266" stroke="#21262D" stroke-width="1"/>
  <text x="34" y="284" class="foot">dominant: <tspan class="accent">{dominant.label}</tspan>
    &#183; {facts['total']} contributions &#183; {facts['streak']}d streak
    &#183; {facts['repos']} repos &#183; {facts['languages']} languages</text>
  <text x="{WIDTH - 34}" y="284" class="foot" text-anchor="end">{stamp}</text>
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True)
    parser.add_argument("--out", default="persona-card.svg")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 1

    try:
        user = fetch(args.user, token)
    except (urllib.error.URLError, RuntimeError) as error:
        print(f"failed to fetch GitHub data: {error}", file=sys.stderr)
        return 1

    personas, facts = build_personas(user)
    with open(args.out, "w", encoding="utf8") as handle:
        handle.write(render(personas, facts, args.user))

    for persona in personas:
        print(f"{persona.label:<10} {persona.weight:.3f}  ({persona.signal})")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

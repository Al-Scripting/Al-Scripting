#!/usr/bin/env python3
"""Render an animated activity card from live GitHub data.

Four real signals - language breadth, commit volume, consistency, and
collaboration - are read from the GitHub GraphQL API, normalised against a
solid-year benchmark, and drawn as an animated SVG with a contribution
sparkline.

No third-party dependencies — urllib and the standard library only, so the workflow
needs no install step. Everything is deterministic given the same API response.

Usage:
    GITHUB_TOKEN=... python scripts/activity_card.py --user Al-Scripting --out activity-card.svg
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

# One query for everything: contribution totals drive three of the four rows,
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
class Metric:
    """One row: a label, the real numbers behind it, and its normalised score."""

    key: str
    label: str
    signal: str         # human-readable description of the underlying numbers
    raw: float          # the underlying count
    score: float = 0.0  # normalised to 0..1 for the bar fill


def fetch(login: str, token: str) -> dict:
    """Run the GraphQL query and return the `user` object."""
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    request = urllib.request.Request(
        GRAPHQL,
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "activity-card",
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


def normalise(x: float, midpoint: float, steepness: float) -> float:
    """Squash a raw count into 0..1 with a smooth, saturating curve.

    `midpoint` is the raw value that maps to 0.5, and `steepness` controls how
    sharply the score climbs around it. Overflow on extreme inputs is clamped
    rather than raised, so an unusually busy year cannot crash the render.
    """
    exponent = -steepness * (x - midpoint)
    if exponent > 60:
        return 0.0
    if exponent < -60:
        return 1.0
    return 1.0 / (1.0 + math.exp(exponent))


def build_metrics(user: dict) -> tuple[list[Metric], dict, list[int]]:
    """Turn the API response into four scored rows plus a sparkline series.

    The midpoints below are the honest part of this card: each is a plausible
    "solid year" value for that signal, so a score near 0.5 means typical and a
    score near 1.0 means genuinely high. They are not tuned to flatter anyone.
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

    metrics = [
        Metric(
            "breadth",
            "BREADTH",
            f"{len(languages)} languages · {contributions['totalRepositoriesWithContributedCommits']} repos touched",
            len(languages) + contributions["totalRepositoriesWithContributedCommits"],
        ),
        Metric(
            "volume",
            "COMMITS",
            f"{contributions['totalCommitContributions']} commits this year",
            contributions["totalCommitContributions"],
        ),
        Metric(
            "consistency",
            "CONSISTENCY",
            f"{streak}-day streak · {calendar['totalContributions']} contributions",
            streak * 6 + calendar["totalContributions"] / 12,
        ),
        Metric(
            "collaboration",
            "COLLAB",
            f"{contributions['totalPullRequestContributions']} PRs · "
            f"{contributions['totalIssueContributions']} issues · "
            f"{contributions['totalPullRequestReviewContributions']} reviews",
            contributions["totalPullRequestContributions"]
            + contributions["totalIssueContributions"]
            + contributions["totalPullRequestReviewContributions"],
        ),
    ]

    midpoints = {"breadth": 18, "volume": 420, "consistency": 60, "collaboration": 40}
    steepness = {"breadth": 0.16, "volume": 0.006, "consistency": 0.045, "collaboration": 0.06}
    for metric in metrics:
        metric.score = normalise(metric.raw, midpoints[metric.key], steepness[metric.key])

    # Weekly contribution totals for the sparkline, oldest week first.
    weekly = [
        sum(day["contributionCount"] for day in week["contributionDays"])
        for week in calendar["weeks"]
    ]

    facts = {
        "total": calendar["totalContributions"],
        "streak": streak,
        "stars": stars,
        "repos": user["repositories"]["totalCount"],
        "languages": len(languages),
    }
    return metrics, facts, weekly


# --------------------------------------------------------------------------- render

# Four columns that must not collide: label | signal | bar | score.
WIDTH, HEIGHT = 900, 312
LABEL_X, SIGNAL_X = 34, 148
BAR_X, BAR_W, BAR_H = 360, 340, 12
SPARK_X, SPARK_W, SPARK_H = 724, 142, 46
ROW_Y, ROW_GAP = 116, 40

# Neo-Japanese palette: vermillion ink on kinari paper.
RED, DIM, INK, BG = "#BC2D29", "#8C7B66", "#2B2320", "#F4EBDA"
CHROME, TRACK, LINE, GRAD0 = "#EAE0C9", "#E3D5B8", "#D8C5A0", "#8E1F1D"


def bar(index: int, metric: Metric) -> str:
    """One row: label, the real numbers, an animated fill, and the score."""
    y = ROW_Y + index * ROW_GAP
    filled = max(6.0, BAR_W * metric.score)
    delay = 0.3 + index * 0.14

    # Opacity starts at 1 and SMIL animates it *from* 0. Content must never be
    # hidden behind an animation that might not run: GitHub serves README images
    # through camo as <img>, where CSS @keyframes are unreliable but SMIL works.
    return f"""
  <g>
    <animate attributeName="opacity" from="0" to="1" dur="0.45s"
             begin="{max(0.0, delay - 0.28):.2f}s" fill="freeze"/>
    <text x="{LABEL_X}" y="{y + 10}" class="label">{metric.label}</text>
    <text x="{SIGNAL_X}" y="{y + 10}" class="signal">{metric.signal}</text>
    <rect x="{BAR_X}" y="{y}" width="{BAR_W}" height="{BAR_H}" rx="6" class="track"/>
    <rect x="{BAR_X}" y="{y}" width="{filled:.1f}" height="{BAR_H}" rx="6" class="fill">
      <animate attributeName="width" from="0" to="{filled:.1f}"
               dur="1.05s" begin="{delay:.2f}s" fill="freeze"
               calcMode="spline" keySplines="0.16 1 0.3 1" keyTimes="0;1"/>
    </rect>
    <text x="{BAR_X + BAR_W + 14}" y="{y + 10}" class="score">{metric.score:.2f}</text>
  </g>"""


def sparkline(weekly: list[int]) -> str:
    """52 weeks of contributions, drawn small, with the line stroking itself in.

    The draw-on effect is a dash offset animated to zero, which needs the path
    length; a straight-line estimate is close enough for a 142px sparkline and
    avoids measuring geometry we cannot query from a script.
    """
    if not weekly:
        return ""
    peak = max(weekly) or 1
    step = SPARK_W / max(1, len(weekly) - 1)
    base = ROW_Y + 3 * ROW_GAP + BAR_H  # sits level with the last row

    points = [
        (SPARK_X + i * step, base - (value / peak) * SPARK_H)
        for i, value in enumerate(weekly)
    ]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{line} L{points[-1][0]:.1f},{base:.1f} L{points[0][0]:.1f},{base:.1f} Z"
    length = int(SPARK_W * 1.6)

    return f"""
  <g>
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.55s" fill="freeze"/>
    <text x="{SPARK_X}" y="{base - SPARK_H - 12:.0f}" class="glabel">52-week contributions</text>
    <path d="{area}" class="spark-area"/>
    <path d="{line}" class="spark-line" stroke-dasharray="{length}" stroke-dashoffset="{length}">
      <animate attributeName="stroke-dashoffset" from="{length}" to="0"
               dur="1.6s" begin="0.6s" fill="freeze"
               calcMode="spline" keySplines="0.3 0.9 0.3 1" keyTimes="0;1"/>
    </path>
    <circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="3" class="spark-dot">
      <animate attributeName="opacity" values="1;0.25;1" dur="2.2s" repeatCount="indefinite"/>
    </circle>
  </g>"""


def render(metrics: list[Metric], facts: dict, weekly: list[int], login: str) -> str:
    """Assemble the card. Pure string building — no templating dependency."""
    rows = "".join(bar(index, metric) for index, metric in enumerate(metrics))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" role="img"
     aria-label="Live GitHub activity for {login}">
  <title>{login} — live GitHub activity</title>
  <style>
    text {{ font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .frame {{ fill: {BG}; stroke: {RED}; stroke-opacity: 0.85; stroke-width: 2; }}
    .chrome {{ fill: {CHROME}; }}
    .kacc {{ fill: {RED}; font-size: 15px; font-weight: 700;
            font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif; }}
    .title {{ fill: {RED}; font-size: 16px; font-weight: 700; letter-spacing: 2px; }}
    .sub {{ fill: {DIM}; font-size: 10.5px; letter-spacing: 0.4px; }}
    .label {{ fill: {INK}; font-size: 11.5px; font-weight: 700; letter-spacing: 1.2px; }}
    .signal {{ fill: {DIM}; font-size: 9.5px; }}
    .score {{ fill: {RED}; font-size: 11.5px; font-weight: 700; }}
    .track {{ fill: {TRACK}; }}
    .fill {{ fill: url(#grad); }}
    .spark-line {{ fill: none; stroke: {RED}; stroke-width: 1.6; stroke-linejoin: round; }}
    .spark-area {{ fill: url(#fade); }}
    .spark-dot {{ fill: {RED}; }}
    .glabel {{ fill: {DIM}; font-size: 9px; letter-spacing: 0.6px; }}
    .foot {{ fill: {DIM}; font-size: 9.5px; }}
    .accent {{ fill: {RED}; font-size: 9.5px; font-weight: 700; }}
  </style>
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{GRAD0}"/>
      <stop offset="100%" stop-color="{RED}"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{RED}" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="12" class="frame"/>
  <path d="M1 13 a12 12 0 0 1 12-12 h{WIDTH - 26} a12 12 0 0 1 12 12 v19 h-{WIDTH - 2} z" class="chrome"/>
  <circle cx="24" cy="17" r="4.5" fill="{RED}"/>
  <circle cx="40" cy="17" r="4.5" fill="#CDBC9C"/>
  <circle cx="56" cy="17" r="4.5" fill="#CDBC9C"/>
  <text x="{WIDTH / 2}" y="21" class="sub" text-anchor="middle">al@oshawa: ~/activity --live</text>

  <text x="34" y="64" class="title">GITHUB ACTIVITY <tspan class="kacc" dx="6">活動記録</tspan></text>
  <text x="34" y="83" class="sub">generated daily from the GitHub API<tspan> _<animate
    attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></tspan></text>

{rows}
{sparkline(weekly)}

  <line x1="34" y1="{HEIGHT - 34}" x2="{WIDTH - 34}" y2="{HEIGHT - 34}" stroke="{LINE}" stroke-width="1"/>
  <text x="34" y="{HEIGHT - 16}" class="foot"><tspan class="accent">{facts['total']}</tspan> contributions
    &#183; <tspan class="accent">{facts['streak']}d</tspan> streak
    &#183; {facts['repos']} repos &#183; {facts['languages']} languages
    &#183; {facts['stars']} stars</text>
  <text x="{WIDTH - 34}" y="{HEIGHT - 16}" class="foot" text-anchor="end">{stamp}</text>
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True)
    parser.add_argument("--out", default="activity-card.svg")
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

    metrics, facts, weekly = build_metrics(user)
    with open(args.out, "w", encoding="utf8") as handle:
        handle.write(render(metrics, facts, weekly, args.user))

    for metric in metrics:
        print(f"{metric.label:<12} {metric.score:.3f}  ({metric.signal})")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Make the section header strips. Pure stdlib. Run: python scripts/make_headers.py"""

import os

HEADERS = [
    ("h-research", "RESEARCH", "研究", "papers and lab work"),
    ("h-building", "BUILDING", "構築", "projects in motion"),
    ("h-shipped", "SHIPPED", "出荷", "work in production"),
    ("h-stack", "STACK", "道具", "tools and languages"),
]

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="56" viewBox="0 0 900 56" role="img" aria-label="{title} section">
  <title>{title}</title>
  <style>
    .strip {{ fill: #F4EBDA; stroke: #BC2D29; stroke-width: 1.6; }}
    .title {{ fill: #2B2320; font-size: 19px; font-weight: 700; letter-spacing: 5px;
             font-family: "JetBrains Mono", ui-monospace, monospace; }}
    .sub   {{ fill: #8C7B66; font-size: 11px; letter-spacing: 1px;
             font-family: "JetBrains Mono", ui-monospace, monospace; }}
    .kanji {{ fill: #F4EBDA; font-size: 22px; font-weight: 700;
             font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif; }}
  </style>
  <rect x="1" y="1" width="898" height="54" rx="10" class="strip"/>
  <path d="M1 11 a10 10 0 0 1 10-10 h64 v54 h-64 a10 10 0 0 1 -10-10 z" fill="#BC2D29"/>
  <text x="38" y="36" class="kanji" text-anchor="middle">{kanji}</text>
  <text x="96" y="35" class="title">{title}</text>
  <text x="898" y="35" class="sub" text-anchor="end" transform="translate(-20 0)">{sub}</text>
  <line x1="{rule_x}" y1="28" x2="720" y2="28" stroke="#BC2D29" stroke-opacity="0.45" stroke-width="1.4"/>
  <circle cx="726" cy="28" r="3" fill="#BC2D29"/>
</svg>
"""


def main() -> None:
    root = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(root, exist_ok=True)
    for name, title, kanji, sub in HEADERS:
        rule_x = 96 + 24 * len(title) + 24
        svg = TEMPLATE.format(title=title, kanji=kanji, sub=sub, rule_x=rule_x)
        path = os.path.join(root, f"{name}.svg")
        with open(path, "w", encoding="utf8") as handle:
            handle.write(svg)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()

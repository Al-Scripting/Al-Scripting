#!/usr/bin/env python3
"""Make the glass cards for the profile README. Pure stdlib. Run: python scripts/make_glass.py

Every card is its own SVG, so every card can have its own link in the README.
Each card has a light and a dark version for <picture> prefers-color-scheme.
GitHub shows SVGs through <img>, so images are embedded as base64 and fonts are system fonts.
"""

import base64
import os
from html import escape
from xml.etree import ElementTree

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "glass-src")
OUT = os.path.join(HERE, "..", "assets", "glass")

SANS = "-apple-system, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
JP = "'Hiragino Mincho ProN', 'Yu Mincho', 'Noto Serif JP', serif"

THEMES = {
    "light": dict(bg="#f5f1ea", blobs=("#e8604a", "#5b6fd6", "#e8b04a", "#c43d2b"), blob_op=0.55,
                  tint="#f5f1ea", tint_op=0.30, glass="#ffffff", glass_op=0.40, edge_op=0.85, ink="#1c1a17", sub="#3d4250",
                  accent="#c43d2b", chip="#ffffff", chip_op=0.55),
    "dark": dict(bg="#0d1117", blobs=("#c43d2b", "#3b4fc4", "#b8862a", "#ff6a4d"), blob_op=0.75,
                 tint="#0d1117", tint_op=0.55, glass="#ffffff", glass_op=0.06, edge_op=0.30, ink="#f5f1ea", sub="#d4cfc6",
                 accent="#ff8a6e", chip="#ffffff", chip_op=0.10),
}


def b64(name: str) -> str:
    ext = name.rsplit(".", 1)[1].replace("jpg", "jpeg")
    with open(os.path.join(SRC, name), "rb") as handle:
        return f"data:image/{ext};base64," + base64.b64encode(handle.read()).decode()


def wrap(text: str, size: float, width: float) -> list[str]:
    # shortcut: fixed average glyph width, upgrade to real metrics if lines overflow
    limit = max(8, int(width / (size * 0.54)))
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > limit:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def tspans(lines: list[str], x: float, y: float, lh: float, **attrs) -> str:
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return "".join(f'<text x="{x}" y="{y + i * lh:.1f}" {a}>{escape(t)}</text>' for i, t in enumerate(lines))


def blobs(t: dict, w: int, h: int, seed: int, blur: int) -> str:
    # four soft colour fields that drift slowly; seed moves them so each card differs
    out = []
    for i, colour in enumerate(t["blobs"]):
        k = (seed * 7 + i * 3) % 10 / 10
        cx, cy = w * ((0.15 + 0.7 * ((k + i * 0.29) % 1))), h * ((0.2 + 0.6 * ((k * 1.7 + i * 0.37) % 1)))
        r = max(w, h) * (0.22 + 0.06 * ((i + seed) % 3))
        dx, dy = w * 0.08 * (1 if i % 2 else -1), h * 0.12 * (1 if i < 2 else -1)
        dur = 14 + (i * 5 + seed) % 9
        out.append(
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{colour}" opacity="{t["blob_op"]}">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx:.0f} {dy:.0f};0 0" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>')
    return f'<g filter="url(#blur{blur})">{"".join(out)}</g>'


def card(t: dict, w: int, h: int, seed: int, body: str, label: str, pad: int = 12, rx: int = 22) -> str:
    gx, gy, gw, gh = pad, pad, w - 2 * pad, h - 2 * pad
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<defs>
<clipPath id="tile"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>
<clipPath id="pane"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="{rx - 6}"/></clipPath>
<filter id="blur28" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter>
<filter id="blur60" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.06 0"/></filter>
<linearGradient id="sheen" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.45"/><stop offset="0.45" stop-color="#fff" stop-opacity="0.06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="{t['edge_op']}"/><stop offset="0.5" stop-color="#fff" stop-opacity="{t['edge_op'] * 0.25:.2f}"/><stop offset="1" stop-color="#fff" stop-opacity="{t['edge_op'] * 0.7:.2f}"/></linearGradient>
</defs>
<g clip-path="url(#tile)">
<rect width="{w}" height="{h}" fill="{t['bg']}"/>
{blobs(t, w, h, seed, 28)}
<g clip-path="url(#pane)">
<rect width="{w}" height="{h}" fill="{t['bg']}"/>
{blobs(t, w, h, seed, 60)}
<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="{t['tint']}" opacity="{t['tint_op']}"/>
<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="{t['glass']}" opacity="{t['glass_op']}"/>
<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" filter="url(#grain)"/>
<rect x="{gx}" y="{gy}" width="{gw}" height="{gh * 0.6:.0f}" fill="url(#sheen)"/>
</g>
<rect x="{gx + 0.6}" y="{gy + 0.6}" width="{gw - 1.2}" height="{gh - 1.2}" rx="{rx - 6}" fill="none" stroke="url(#rim)" stroke-width="1.2"/>
</g>
{body}
</svg>
"""


def chip(t: dict, x: float, y: float, text: str, size: int = 12, accent: bool = False) -> tuple[str, float]:
    w = len(text) * size * 0.6 + 22
    colour = t["accent"] if accent else t["ink"]
    svg = (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{size + 14}" rx="{(size + 14) / 2}" fill="{t["chip"]}" '
           f'fill-opacity="{t["chip_op"]}" stroke="#fff" stroke-opacity="{t["edge_op"] * 0.6:.2f}"/>'
           f'<text x="{x + w / 2:.0f}" y="{y + size + 3}" text-anchor="middle" font-family="{MONO}" '
           f'font-size="{size}" fill="{colour}" letter-spacing="0.3">{escape(text)}</text>')
    return svg, w


def hero(t: dict) -> str:
    w, h = 900, 330
    lines = ["I build RL agents that playtest games.", "I make LLM NPCs that stay in character.",
             "I program P4 data planes at line rate.", "I secure the networks research runs on."]
    cycle = len(lines) * 3
    tag = "".join(
        f'<text x="262" y="226" font-family="{MONO}" font-size="15" fill="{t["accent"]}" opacity="0">'
        f'&gt; {escape(s)}<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.03;0.22;0.25;1" '
        f'dur="{cycle}s" begin="{i * 3}s" repeatCount="indefinite"/></text>' for i, s in enumerate(lines))
    chips, x = [], 262
    for text, acc in [("IEEE CoG 2026 · first author", True), ("CSER 2026 · 2 posters", False), ("TinyBrains · #1 of 69", False)]:
        svg, cw = chip(t, x, 250, text, 12, acc)
        chips.append(svg)
        x += cw + 10
    body = f"""
<circle cx="146" cy="165" r="98" fill="#fff" fill-opacity="{t['chip_op']}" stroke="#fff" stroke-opacity="{t['edge_op']}" stroke-width="1.5"/>
<clipPath id="face"><circle cx="146" cy="165" r="88"/></clipPath>
<image href="{b64('photo.jpg')}" x="58" y="77" width="176" height="176" clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/>
<text x="262" y="96" font-family="{SANS}" font-size="38" font-weight="800" fill="{t['ink']}" letter-spacing="-0.5">Al Muqshith Shifan</text>
<image href="{b64('hanko-seal.png')}" x="644" y="62" width="40" height="40"/>
<text x="264" y="126" font-family="{JP}" font-size="17" fill="{t['accent']}" letter-spacing="4">アル・ムクシット・シファン</text>
<text x="262" y="164" font-family="{SANS}" font-size="16" fill="{t['sub']}">MSc Computer Science · Ontario Tech University</text>
<text x="262" y="188" font-family="{SANS}" font-size="16" fill="{t['sub']}">Graduate Research Assistant · Code &amp; Sorcery Lab</text>
{tag}
{''.join(chips)}
<text x="852" y="70" font-family="{JP}" font-size="24" fill="{t['ink']}" opacity="0.18" text-anchor="middle">コ</text>
<text x="852" y="100" font-family="{JP}" font-size="24" fill="{t['ink']}" opacity="0.18" text-anchor="middle">ー</text>
<text x="852" y="130" font-family="{JP}" font-size="24" fill="{t['ink']}" opacity="0.18" text-anchor="middle">ド</text>
<text x="852" y="160" font-family="{JP}" font-size="24" fill="{t['ink']}" opacity="0.18" text-anchor="middle">と</text>
<text x="852" y="190" font-family="{JP}" font-size="24" fill="{t['ink']}" opacity="0.18" text-anchor="middle">魔</text>
<text x="852" y="220" font-family="{JP}" font-size="24" fill="{t['ink']}" opacity="0.18" text-anchor="middle">術</text>
"""
    return card(t, w, h, 1, body, "Al Muqshith Shifan, MSc Computer Science, Ontario Tech University", pad=16, rx=28)


def header(t: dict, title: str, kanji: str, sub: str, seed: int) -> str:
    w, h = 900, 76
    body = f"""
<rect x="26" y="20" width="36" height="36" rx="8" fill="{t['accent']}"/>
<text x="44" y="45" font-family="{JP}" font-size="17" font-weight="700" fill="#fff" text-anchor="middle">{kanji[0]}</text>
<text x="78" y="46" font-family="{SANS}" font-size="20" font-weight="800" fill="{t['ink']}" letter-spacing="5">{escape(title)}</text>
<text x="{92 + len(title) * 19}" y="45" font-family="{JP}" font-size="15" fill="{t['accent']}" letter-spacing="3">{kanji}</text>
<text x="874" y="44" font-family="{MONO}" font-size="12" fill="{t['sub']}" text-anchor="end">{escape(sub)}</text>
"""
    return card(t, w, h, seed, body, f"{title} section", pad=8, rx=20)


def pill(t: dict, text: str, seed: int) -> str:
    w, h = 168, 52
    body = (f'<circle cx="32" cy="26" r="4.5" fill="{t["accent"]}"/>'
            f'<text x="94" y="31" font-family="{SANS}" font-size="15" font-weight="700" fill="{t["ink"]}" '
            f'text-anchor="middle" letter-spacing="1.5">{escape(text.upper())}</text>')
    return card(t, w, h, seed, body, text, pad=5, rx=26)


def paper(t: dict, p: dict, seed: int) -> str:
    w, h = 440, 290
    title = wrap(p["title"], 17, w - 64)
    ty = 112
    note = wrap(p["note"], 13, w - 64)
    ny = ty + len(title) * 22 + 34
    badge, _ = chip(t, 32, 64, p["venue"], 11, True)
    role, _ = chip(t, w - 32 - (len(p["role"]) * 11 * 0.6 + 22), 64, p["role"], 11)
    body = f"""
<text x="32" y="48" font-family="{JP}" font-size="15" fill="{t['accent']}" letter-spacing="3">論文</text>
<text x="76" y="48" font-family="{MONO}" font-size="12" fill="{t['sub']}">/ {p['num']}</text>
{badge}{role}
{tspans(title, 32, ty, 22, font_family=SANS, font_size=17, font_weight=800, fill=t['ink'])}
<text x="32" y="{ty + len(title) * 22 + 6}" font-family="{SANS}" font-size="12" fill="{t['sub']}">{escape(p['authors'])}</text>
{tspans(note, 32, ny, 18, font_family=SANS, font_size=13, fill=t['ink'], opacity=0.85)}
<text x="{w - 32}" y="{h - 28}" font-family="{MONO}" font-size="12" font-weight="700" fill="{t['accent']}" text-anchor="end">{escape(p['cta'])} →</text>
"""
    return card(t, w, h, seed, body, p["title"])


def project(t: dict, p: dict, seed: int) -> str:
    w, h = 440, 200
    desc = wrap(p["desc"], 13.5, w - 64)
    sw = len(p["status"]) * 11 * 0.6 + 22
    status, _ = chip(t, w - 32 - sw, 34, p["status"], 11, True)
    tags, x = [], 32
    for tag in p["tags"]:
        svg, cw = chip(t, x, h - 54, tag, 11)
        tags.append(svg)
        x += cw + 8
    body = f"""
<text x="32" y="52" font-family="{JP}" font-size="14" fill="{t['accent']}" letter-spacing="3">作品</text>
<text x="72" y="52" font-family="{MONO}" font-size="12" fill="{t['sub']}">· {escape(p['kind'])}</text>
{status}
<text x="32" y="92" font-family="{SANS}" font-size="24" font-weight="800" fill="{t['ink']}" letter-spacing="-0.3">{escape(p['name'])}</text>
{tspans(desc, 32, 118, 19, font_family=SANS, font_size=13.5, fill=t['ink'], opacity=0.85)}
{''.join(tags)}
"""
    return card(t, w, h, seed, body, p["name"])


def lab(t: dict) -> str:
    w, h = 900, 190
    body = f"""
<text x="40" y="58" font-family="{JP}" font-size="15" fill="{t['accent']}" letter-spacing="3">研究室</text>
<text x="40" y="92" font-family="{SANS}" font-size="24" font-weight="800" fill="{t['ink']}">Code &amp; Sorcery Lab</text>
<text x="40" y="118" font-family="{SANS}" font-size="14" fill="{t['sub']}">Game development, software engineering and AI meet here.</text>
<text x="40" y="146" font-family="{SANS}" font-size="13" fill="{t['sub']}">Supervisors · Dr. Cristiano Politowski · Dr. Loutfouz Zaman · Dr. Ali Neshati</text>
<rect x="566" y="42" width="300" height="106" rx="16" fill="#fff" fill-opacity="{0.78 if t['bg'] != '#f5f1ea' else 0.6}"/>
<image href="{b64('otu-logo.png')}" x="586" y="66" width="47" height="58"/>
<image href="{b64('code-sorcery-logo.png')}" x="650" y="66" width="56" height="58"/>
<image href="{b64('uxid-logo.png')}" x="720" y="80" width="80" height="26"/>
<image href="{b64('gamer-logo.png')}" x="812" y="76" width="38" height="35"/>
"""
    return card(t, w, h, 5, body, "Code and Sorcery Lab, Ontario Tech University", pad=14, rx=26)


def footer(t: dict) -> str:
    w, h = 900, 150
    body = f"""
<image href="{b64('hanko-seal.png')}" x="426" y="30" width="48" height="48"/>
<text x="450" y="104" font-family="{JP}" font-size="16" fill="{t['accent']}" text-anchor="middle" letter-spacing="6">コードと魔術・研究と実装</text>
<text x="450" y="126" font-family="{SANS}" font-size="13" font-style="italic" fill="{t['sub']}" text-anchor="middle">The best software feels like a game.</text>
<text x="40" y="126" font-family="{MONO}" font-size="11" fill="{t['sub']}">Ontario, Canada</text>
<text x="860" y="126" font-family="{MONO}" font-size="11" fill="{t['sub']}" text-anchor="end">al-scripting.github.io</text>
"""
    return card(t, w, h, 8, body, "Code and sorcery, research and implementation", pad=14, rx=26)


PAPERS = [
    dict(slug="ridge", num="001", venue="IEEE CoG 2026 · Madrid", role="first author",
         title="RIDGE: State-Conditioned Reward Blending for Behavioral Coverage in Deep RL Game Agents",
         authors="Shifan · Chua · Neshati · Zaman · Politowski",
         note="One PPO agent blends four persona rewards from the game state. The only condition that reaches both wood-tier branches on Crafter.",
         cta="arXiv"),
    dict(slug="peak", num="002", venue="CSER 2026 · Poster", role="first author",
         title="Evolved Neural Agents as Tireless Playtesters",
         authors="Shifan · Chua · Neshati · Zaman · Politowski",
         note="Frozen agents act as regression tests for levels. They caught 70 of 76 edits that changed play, with no false alarm on 54 controls.",
         cta="code"),
    dict(slug="tast", num="003", venue="CSER 2026 · Poster", role="second author",
         title="Trait Activation Steering: Keeping Small-Model NPCs in Character",
         authors="Chua · Shifan · Neshati · Zaman · Politowski",
         note="A 1 MB trait cartridge edits the hidden state at run time. Over a 20-turn attack, the judge score goes from 3.3 to 4.8.",
         cta="dataset"),
    dict(slug="slr", num="004", venue="Draft · Mapping Study", role="in progress",
         title="Emotional Memory in LLM-Driven NPCs: A Systematic Mapping Study",
         authors="87 records screened · 29 primary studies",
         note="Only 3 of 29 studies link a stored emotion to a memory and base that link on psychology.",
         cta="ask for preprint"),
]

PROJECTS = [
    dict(slug="afterstate", kind="MSc thesis", name="AFTERSTATE", status="coming soon",
         desc="The characters you meet in games, and what they get wrong about you. More when the paper is out.",
         tags=["Python", "Game characters"]),
    dict(slug="fathom", kind="companion AI", name="FATHOM", status="sneak peek",
         desc="An AI companion in the Subnautica PDA. It speaks only when a line changes what you do.",
         tags=["UE 5.6", "UE4SS Lua", "Ollama"]),
    dict(slug="peak", kind="engine", name="PEAK", status="CSER 2026",
         desc="Game-balancing engine. Evolved agents playtest 5 deterministic 2D games for 7 player personas.",
         tags=["Pygame", "NumPy", "Neuroevolution"]),
    dict(slug="rogue", kind="sequel to RIDGE", name="ROGUE", status="paper in progress",
         desc="RIDGE for any Unity ML-Agents game. Each persona is a YAML block that prices game events.",
         tags=["ML-Agents", "PyTorch", "C#"]),
    dict(slug="raven", kind="VR", name="RAVEN", status="in development",
         desc="Hears a fire alarm, a door or a dog in the real room, and warns the VR player to match the risk.",
         tags=["Unity 6", "Quest 3", "YAMNet"]),
    dict(slug="raze", kind="competition", name="RAZE", status="#1 of 69",
         desc="Hand-built ONNX brains with no learned weights. A flood fill written as convolution layers.",
         tags=["ONNX", "NumPy", "Python"]),
    dict(slug="gestura", kind="hackathon", name="Gestura", status="HackHive 2026",
         desc="Computer vision and a 3D digital twin turn gestures into structured clinical data for telehealth.",
         tags=["Flask", "CV", "Three.js"]),
    dict(slug="dungeon", kind="side quest", name="Local-AI-Dungeon", status="open source",
         desc="An offline text adventure that runs on a local LLM. No cloud, no key.",
         tags=["Ollama", "Gemma 3"]),
]

HEADERS = [("research", "RESEARCH", "研究", "papers and posters"), ("projects", "PROJECTS", "作品", "in motion"),
           ("lab", "LAB", "魔術", "code & sorcery"), ("shipped", "SHIPPED", "出荷", "in production"),
           ("stack", "STACK", "道具", "tools and languages")]

PILLS = ["Portfolio", "LinkedIn", "Scholar", "Lab", "CV"]


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    files = {}
    for mode, t in THEMES.items():
        files[f"hero-{mode}"] = hero(t)
        files[f"lab-{mode}"] = lab(t)
        files[f"footer-{mode}"] = footer(t)
        for i, (slug, title, kanji, sub) in enumerate(HEADERS):
            files[f"h-{slug}-{mode}"] = header(t, title, kanji, sub, i + 2)
        for i, name in enumerate(PILLS):
            files[f"pill-{name.lower()}-{mode}"] = pill(t, name, i + 3)
        for i, p in enumerate(PAPERS):
            files[f"paper-{p['slug']}-{mode}"] = paper(t, p, i + 4)
        for i, p in enumerate(PROJECTS):
            files[f"project-{p['slug']}-{mode}"] = project(t, p, i + 6)
    for name, svg in files.items():
        ElementTree.fromstring(svg)  # self-check: every card must be well-formed XML
        with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf8") as handle:
            handle.write(svg)
    print(f"wrote {len(files)} files to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()

[![al@oshawa terminal](https://raw.githubusercontent.com/Al-Scripting/Al-Scripting/main/banner.svg)](https://al-scripting.github.io/about-me/)

**[&#8594; portfolio](https://al-scripting.github.io/about-me/)** &#183; **[&#8594; linkedin](https://www.linkedin.com/in/al-mohamed-shifan-5266b924b)** &#183; **[&#8594; cv](https://al-scripting.github.io/about-me/assets/Al-Shifan-Resume-2026.pdf)**

![CCNA](https://img.shields.io/badge/CCNA-Certified_2024--2027-1BA0D7?style=for-the-badge&logo=cisco&logoColor=white)
![IEEE CoG 2026](https://img.shields.io/badge/IEEE_CoG_2026-Paper_Accepted-00629B?style=for-the-badge&logo=ieee&logoColor=white)
![Dean's List](https://img.shields.io/badge/Dean's_List-2024--2026-B8860B?style=for-the-badge&logo=academia&logoColor=white)
![TryHackMe](https://img.shields.io/badge/TryHackMe-200%2B_hours-212C42?style=for-the-badge&logo=tryhackme&logoColor=white)

```bash
$ ./whoami --verbose

name    : Al Muqshith Shifan
role    : MSc Computer Science (Software Design, AI/RL) @ Ontario Tech
prior   : BIT Networking & Cybersecurity - Dean's List
lab     : SEGAL - researcher, deep RL & LLM-driven NPCs
certs   : CCNA (2024-2027)
tagline : network engineer by trade, dev by obsession, researcher by 2am
domain  : where deep RL, programmable networks, and game dev collide
status  : teaching agents to play games & networks to route themselves
```

I build deep-RL training infrastructure and programmable-network systems — multi-head PPO critics
and custom PyTorch environments on one side, **Intel Tofino P4** data planes on the other. I'm a
graduate researcher in the SEGAL Lab at **Ontario Tech University**, a TA across two networking
courses, and I'm headed toward a PhD in emotion, memory, and reinforcement learning for game
characters.

- **Pronouns:** he/him
- **How to reach me:** [portfolio](https://al-scripting.github.io/about-me/) &#183; [linkedin](https://www.linkedin.com/in/al-mohamed-shifan-5266b924b)

<p align="left">
  <a href="https://github.com/Al-Scripting">
    <img height="165" src="https://github-readme-stats.vercel.app/api?username=Al-Scripting&show_icons=true&include_all_commits=true&count_private=true&theme=github_dark&hide_border=false" alt="Al's GitHub stats" />
  </a>
  <a href="https://github.com/Al-Scripting">
    <img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=Al-Scripting&layout=compact&langs_count=8&theme=github_dark&hide_border=false" alt="Top languages" />
  </a>
</p>

---

## Accepted Papers

**RIDGE: State-Conditioned Reward Blending for Behavioral Coverage in Deep RL Game Agents**
Al Muqshith Shifan, Kevin Christopher Chua
*Accepted at IEEE Conference on Games (CoG) 2026 — Madrid, Spain (September 2026)*

Conceptualized, implemented, written, and accepted in a single 20-hour overnight sprint during our
first month of the MSc. RIDGE (Reactive Inter-persona Dynamic Goal Engine) uses one PPO agent that
dynamically blends Explorer, Survivor, Craftsman, and Warrior persona reward weights via smooth
sigmoid functions conditioned on internal game state, so a single agent shifts its play style
mid-episode. Under the hood: a multi-head PPO critic (shared CNN encoder, persona-specific value
heads) trained jointly with sigmoid weight blending over a 6-dim game-state vector, to handle PPO
non-stationarity under dynamic reward weighting. With gratitude to Cristiano Politowski, Ali
Neshati, and Dr. Loutfouz Zaman for their support and rapid feedback.

## Game Dev & AI Agents

I like building things that *play*. My favourite bugs are the ones where the agent finds a strategy
I never intended.

- **[RIDGE](https://github.com/Code-SorceryLab/RIDGE)** — one PPO agent, four personas
  (Explorer / Survivor / Craftsman / Warrior) blended with smooth sigmoids on the **Crafter**
  environment. Full PyTorch pipeline, TensorBoard logging, YAML configs, a 4-condition × 5-seed ×
  1M-step sweep against fixed-persona baselines. Accepted at **IEEE CoG 2026**. It learns to survive
  by *vibe*.
- **[PEAK](https://github.com/Code-SorceryLab/PEAK-DRL-Tool)** — a deterministic, high-performance
  DRL engine benchmarking agent *adaptability* across 11 custom 2D platformer stages with
  reproducible SMB1-style physics. A **dual spatial hashing** collision system (separate
  static/dynamic grids) hits O(C) per query and sustains **1000+ env steps/sec**, which is what makes
  10M-step runs practical on one machine.
- **[Local-AI-Dungeon](https://github.com/Al-Scripting/Local-AI-Dungeon-Ollama-Python)** — a fully
  offline text-adventure engine: a lightweight Python game loop wired into a local
  **Gemma 3 / Ollama** model. No cloud, no leash.
- **[Procedural-Graph-Tools](https://github.com/Code-SorceryLab/Procedural-Graph-Tools)** —
  procedural generation explored through graph-based data structures, in GDScript.
- **Re;Animate '26** — 1st place. Built a turn-based tactics game in **AMOS BASIC** on an Amiga,
  because constraints breed creativity.

## Networks, Systems & Security

The other half of the brain. Line-rate packet processing and the boring infrastructure that makes
research possible.

- **Intel Tofino P4 research infrastructure** — authored custom data-plane programs extracting
  per-flow header and timing telemetry at line rate; delivered the lab's first working
  Tofino-deployed implementation. Also diagnosed and patched recurring Linux kernel/driver issues
  across the P4 control-plane servers, cutting reported crashes ~30% over three months.
- **Vulnerability assessment @ YYC Beeswax Ltd** — audited a WooCommerce + Stripe stack, found 15
  exploitable issues across customer-facing endpoints, and audited 30+ plugins against CVE
  databases. The hardening checklist I wrote became the team's pre-deploy review gate.
- **Network automation** — Ansible playbooks and scripted Cisco IOS configuration, because
  configuring the same switch by hand twice is a bug.
- **Offensive security tooling** — ethical hacking scripts and lab work; 200+ hours on TryHackMe.
- **[EncryptionProgram](https://github.com/Al-Scripting/EncryptionProgram)** ·
  **[DES-Encryption-Algorithm](https://github.com/Al-Scripting/DES-Encryption-Algorithm)** —
  Caesar, Playfair, substitution, product and transposition ciphers, plus a from-scratch DES
  implementation.

## Data, ML & Full Stack

- **[steam-patch-notes](https://github.com/Code-SorceryLab/steam-patch-notes)** — a large, cleaned
  dataset of Steam patch notes with a reproducible collection pipeline off the Steam API.
- **Gestura** *(HackHive 2026)* — a non-verbal patient intake tool: Flask backend streaming
  real-time hand-tracking state to a **Three.js** 3D "digital twin" frontend, with **Gemini**
  converting gestures into SOAP-style clinician summaries.
- **[Steam-Gift-Helper](https://github.com/Al-Scripting/Steam-Gift-Helper)** — analyses a friend's
  Steam library and wishlist to recommend a gift from actual playtime habits, not guesswork.
- **[Smart-Home-Energy-Prediction](https://github.com/Al-Scripting/Smart-Home-Energy-Prediction)** —
  predicting household energy use from IoT sensor readings and weather data.
- **[Anime-Wiki](https://github.com/Al-Scripting/Anime-Wiki)** — a DevOps exercise in CI/CD,
  automation and containerization, wearing an anime tracker as a disguise.
- **[Database-Project-Amazone](https://github.com/Al-Scripting/Database-Project-Amazone)** ·
  **[PalatePassport](https://github.com/Al-Scripting/PalatePassport)** — full e-commerce and
  restaurant-discovery apps: auth, carts, admin stock management, transaction history.

## Skills

| I have | I'm learning | In the memory banks |
|---|---|---|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=openjdk&logoColor=white) ![C++](https://img.shields.io/badge/C++-00599C?style=flat&logo=cplusplus&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) ![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat&logo=nodedotjs&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) ![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=mysql&logoColor=white) ![Bash](https://img.shields.io/badge/Bash-4EAA25?style=flat&logo=gnubash&logoColor=white) ![P4](https://img.shields.io/badge/P4-EE0000?style=flat) <br> ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white) ![Gymnasium](https://img.shields.io/badge/Gymnasium-0081A5?style=flat) ![Stable Baselines3](https://img.shields.io/badge/Stable_Baselines3-3776AB?style=flat) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white) ![TensorBoard](https://img.shields.io/badge/TensorBoard-FF6F00?style=flat&logo=tensorflow&logoColor=white) ![Hydra](https://img.shields.io/badge/Hydra-54C7EC?style=flat) <br> ![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat&logo=ollama&logoColor=white) ![Gemini](https://img.shields.io/badge/Gemini_API-8E75B2?style=flat&logo=googlegemini&logoColor=white) ![OpenCV](https://img.shields.io/badge/Computer_Vision-5C3EE8?style=flat&logo=opencv&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white) ![Three.js](https://img.shields.io/badge/Three.js-000000?style=flat&logo=threedotjs&logoColor=white) <br> ![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black) ![Kali](https://img.shields.io/badge/Kali-557C94?style=flat&logo=kalilinux&logoColor=white) ![Red Hat](https://img.shields.io/badge/Red_Hat-EE0000?style=flat&logo=redhat&logoColor=white) ![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat&logo=windows&logoColor=white) ![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=flat&logo=ansible&logoColor=white) ![Cisco IOS](https://img.shields.io/badge/Cisco_IOS-1BA0D7?style=flat&logo=cisco&logoColor=white) ![Wireshark](https://img.shields.io/badge/Wireshark-1679A7?style=flat&logo=wireshark&logoColor=white) ![Nmap](https://img.shields.io/badge/Nmap-4682B4?style=flat) | ![macOS](https://img.shields.io/badge/macOS_dev-000000?style=flat&logo=apple&logoColor=white) ![Swift](https://img.shields.io/badge/Swift-FA7343?style=flat&logo=swift&logoColor=white) ![Godot](https://img.shields.io/badge/Godot-478CBF?style=flat&logo=godotengine&logoColor=white) ![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white) ![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white) | ![C](https://img.shields.io/badge/C-A8B9CC?style=flat&logo=c&logoColor=black) ![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat&logo=php&logoColor=white) ![AMOS BASIC](https://img.shields.io/badge/AMOS_BASIC-6A4C93?style=flat) ![GDScript](https://img.shields.io/badge/GDScript-478CBF?style=flat&logo=godotengine&logoColor=white) |

## Research Interests

![Reinforcement Learning](https://img.shields.io/badge/Reinforcement_Learning-0A9396?style=for-the-badge)
![LLM NPCs](https://img.shields.io/badge/LLM_NPCs-005F73?style=for-the-badge)
![Affective Computing](https://img.shields.io/badge/Affective_Computing-9B2226?style=for-the-badge)
![Software Design](https://img.shields.io/badge/Software_Design-354F52?style=for-the-badge)
![Programmable Networks](https://img.shields.io/badge/Programmable_Networks-3A5A40?style=for-the-badge)

## IDE / tools I like

![VS Code](https://img.shields.io/badge/VISUAL_STUDIO_CODE-007ACC?style=flat&logo=visualstudiocode&logoColor=white)
![PyCharm](https://img.shields.io/badge/PYCHARM-000000?style=flat&logo=pycharm&logoColor=white)
![Neovim](https://img.shields.io/badge/NEOVIM-57A143?style=flat&logo=neovim&logoColor=white)
![Obsidian](https://img.shields.io/badge/OBSIDIAN-7C3AED?style=flat&logo=obsidian&logoColor=white)
![Wireshark](https://img.shields.io/badge/WIRESHARK-1679A7?style=flat&logo=wireshark&logoColor=white)

## Software Design & The Stack

I care about clean systems as much as clever ones — the kind you can read six months later without
crying.

```
languages  ########## python java js c++ bash
ml / rl    ########.. pytorch gymnasium sb3 ppo
networking #########. p4 tofino cisco (ccna) ansible
security   ########.. nmap wireshark kali cve-audit
tooling    #######... git docker linux ollama
```

## My down time

![Steam](https://img.shields.io/badge/STEAM-000000?style=flat&logo=steam&logoColor=white)
![Spotify](https://img.shields.io/badge/SPOTIFY-1DB954?style=flat&logo=spotify&logoColor=white)
![Crunchyroll](https://img.shields.io/badge/CRUNCHYROLL-F47521?style=flat&logo=crunchyroll&logoColor=white)
![TryHackMe](https://img.shields.io/badge/TRYHACKME-212C42?style=flat&logo=tryhackme&logoColor=white)

## Reach Me

```bash
$ curl -s al-scripting.github.io/about-me # the full story lives here
$ open ./links --up-top                   # portfolio / linkedin / cv
```

---

*// still convinced the best software feels a little like a game.*

# Copilot skills

Reusable agent skills for GitHub Copilot CLI.

## Available skills

| Skill | Purpose |
| --- | --- |
| [report-spam](skills/report-spam/) | Trace a suspicious email, identify the infrastructure and accounts involved, and report confirmed abuse. It also reports cryptocurrency wallets used in sextortion and blackmail scams. |

## Install a skill

Clone the repository and register its skills directory:

```bash
git clone https://github.com/M1XZG/copilot-skills.git
copilot skill add "$(pwd)/copilot-skills/skills"
```

Alternatively, copy an individual skill directory into `~/.copilot/skills/`,
then run `/skills reload` inside Copilot CLI.

Each skill is self-contained beneath `skills/`.

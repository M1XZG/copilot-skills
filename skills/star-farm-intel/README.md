# Star Farm Intelligence

`star-farm-intel` investigates unsolicited offers for paid GitHub promotion,
stars, forks or repository engagement. It checks the sender's public claims,
then prepares a short reply that asks for concrete details about their process,
identity, evidence and previous work.

The skill uses a polite, inexperienced tone so the sender explains the service
in their own words. It never says the user works at or represents GitHub.

## Requirements

- GitHub Copilot CLI
- Access to Gmail through the Google Workspace MCP server
- Read-only GitHub and web research tools

## Install

```bash
git clone https://github.com/M1XZG/copilot-skills.git
cp -a copilot-skills/skills/star-farm-intel ~/.copilot/skills/
```

Then reload skills inside Copilot CLI:

```text
/skills reload
```

## Use

```text
/star-farm-intel https://mail.google.com/mail/u/0/#inbox/...
```

An invocation reads the identified thread, researches public claims and creates
one Gmail reply draft. It does not send the reply. The user must review and
approve every outgoing message separately.

Each thread also gets a private local evidence ledger under
`~/.local/state/star-farm-intel/cases/`. It preserves raw messages and records
identities, addresses, links, redirect chains, timezone changes, infrastructure,
claims, commercial terms, public research and all draft or send actions. Case
data is never committed to this repository.

The skill will not provide credentials, repository access, private code,
payment or software installation. Requests for those trigger a warning instead
of another draft.

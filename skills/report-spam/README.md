# Report Spam

`report-spam` investigates a suspicious email from a Gmail URL. It retrieves
the original message, traces the actual delivery path, checks authentication
results, identifies infrastructure and account references, and sends
evidence-based reports to verified abuse contacts.

For sextortion or cryptocurrency blackmail, it also extracts and reports wallet
addresses to suitable public abuse databases.

## Requirements

- GitHub Copilot CLI
- Access to Gmail through the Google Workspace MCP server
- Web search and browser tools for finding official contacts and submitting
  reports
- Python 3.10 or newer for the included `.eml` analyser

## Install

```bash
git clone https://github.com/M1XZG/copilot-skills.git
cp -a copilot-skills/skills/report-spam ~/.copilot/skills/
```

Then reload skills inside Copilot CLI:

```text
/skills reload
```

## Use

```text
/report-spam https://mail.google.com/mail/u/0/#spam/...
```

The word `report` authorises the skill to notify verified abuse contacts. If
you ask only to inspect or analyse a message, the skill stops before sending
anything.

National phishing services are not contacted for ordinary spam. They are used
only for credible phishing or fraud when you specifically request it.

The skill does not delete the source email unless you explicitly ask.

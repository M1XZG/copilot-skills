# Private evidence ledger

Keep one private case directory per Gmail thread:

```text
~/.local/state/star-farm-intel/cases/<thread-id>/
├── ledger.json
└── messages/
    └── <UTC timestamp>-<gmail-message-id>.eml
```

Create directories with mode `700` and files with mode `600`. Write updates
atomically through a temporary file followed by replacement.

## Ledger structure

Use this top-level shape and extend it when new indicator types appear:

```json
{
  "thread_id": "",
  "source_urls": [],
  "created_at": "",
  "updated_at": "",
  "participants": [],
  "identities": [],
  "messages": [],
  "timezone_timeline": [],
  "infrastructure": {
    "ips": [],
    "hostnames": [],
    "providers": [],
    "authentication_domains": []
  },
  "contact_indicators": {
    "email_addresses": [],
    "reply_to_addresses": [],
    "postal_addresses": [],
    "telephone_numbers": [],
    "websites": [],
    "social_handles": [],
    "github_accounts": []
  },
  "urls": [],
  "repositories": [],
  "claims": [],
  "commercial_terms": [],
  "access_requests": [],
  "attachments": [],
  "public_research": [],
  "contradictions": [],
  "unanswered_questions": [],
  "actions": []
}
```

Each entry should include `first_seen`, `last_seen`, `source_message_id` and,
where relevant, `confidence` and `notes`. Keep exact spellings, capitalisation
and malformed values. Add normalized values separately rather than replacing
the originals.

## Message records

For every inbound message, record:

- Gmail message ID and RFC Message-ID;
- raw `.eml` relative path and SHA-256;
- visible From, Reply-To, Return-Path and recipients;
- subject;
- original Date header;
- parsed UTC timestamp;
- exact UTC offset such as `-0700` or `+0100`;
- Received chain;
- SPF, DKIM, DMARC and ARC results;
- DKIM signing and Message-ID domains;
- mail client or user-agent headers;
- attachment metadata;
- sender's new unquoted text and a SHA-256 of that text.

The raw MIME file is the canonical record. The ledger is an index for analysis.

## Timezone handling

Append every observed Date-header offset to `timezone_timeline`, including
repeated values. When an offset differs from the previous inbound message, add
a contradiction or observation describing the change.

Never treat the offset as geolocation proof. It can come from device settings,
webmail settings, copied text, an API or deliberately chosen configuration.

## URLs and addresses

Store every supplied URL before inspecting it. Record redirects as an ordered
list without visiting them in an authenticated browser. Keep:

- original URL;
- source message;
- HTTP status and redirect targets;
- final domain and URL;
- domain registration and infrastructure ownership when checked;
- whether it requested authentication, downloads or payment.

Store all supplied physical addresses, email addresses, phone numbers and
payment identifiers exactly. Mark whether each was sender-supplied, header
derived or independently verified.

## Research and actions

For each research pass, record the query, source, timestamp, result summary,
URLs and coverage limitations. Do not turn blocked access or zero indexed
results into proof of absence.

For drafts and sent messages, record the exact body, recipient, thread, reply
target, Gmail ID, timestamp and status. Sending always requires separate user
approval.

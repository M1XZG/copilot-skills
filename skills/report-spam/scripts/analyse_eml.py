#!/usr/bin/env python3
"""Extract trace and abuse indicators from an RFC 822 email."""

from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import re
from email import policy
from email.message import Message
from email.parser import BytesParser
from pathlib import Path
from typing import Iterable


URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+=-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
IPV4_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
BITCOIN_BECH32_RE = re.compile(r"\b(?:bc1|tb1)[ac-hj-np-z02-9]{11,71}\b", re.IGNORECASE)
BITCOIN_BASE58_RE = re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b")
ETHEREUM_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
SENDGRID_ACCOUNT_RE = re.compile(r"\bbounces\+(\d+)(?:-[^@]*)?@sendgrid\.net\b", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(?:script|style)\b.*?</(?:script|style)>", re.IGNORECASE | re.DOTALL)

SEXTORTION_TERMS = (
    "sextortion",
    "webcam",
    "masturbat",
    "explicit",
    "remote access trojan",
    "send the video",
    "recordings of you",
)
EXTORTION_TERMS = (
    "bitcoin",
    "btc",
    "wallet",
    "within 2 days",
    "within two days",
    "pay",
    "publish",
    "shared with",
)


def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def message_text(message: Message) -> str:
    parts: list[str] = []
    for part in message.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() not in {"text/plain", "text/html"}:
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeError):
            payload = part.get_payload(decode=True) or b""
            content = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        if part.get_content_type() == "text/html":
            content = SCRIPT_STYLE_RE.sub(" ", content)
            content = TAG_RE.sub(" ", content)
            content = html.unescape(content)
        parts.append(content)
    return re.sub(r"\s+", " ", "\n".join(parts)).strip()


def valid_ipv4(value: str) -> bool:
    try:
        ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        return False
    return True


def authentication_summary(headers: str) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {"spf": [], "dkim": [], "dmarc": [], "arc": []}
    for key in results:
        matches = re.findall(rf"\b{key}=([a-zA-Z0-9_-]+)", headers, re.IGNORECASE)
        results[key] = unique(match.lower() for match in matches)
    return results


def classify(text: str, wallets: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    categories: list[str] = []
    sextortion_hits = sum(term in lowered for term in SEXTORTION_TERMS)
    extortion_hits = sum(term in lowered for term in EXTORTION_TERMS)
    if sextortion_hits >= 2 and (extortion_hits >= 2 or any(wallets.values())):
        categories.append("sextortion")
    if any(wallets.values()) and extortion_hits >= 2:
        categories.append("cryptocurrency-blackmail")
    return categories


def analyse(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    message = BytesParser(policy=policy.default).parsebytes(raw)
    text = message_text(message)
    header_text = "\n".join(f"{key}: {value}" for key, value in message.raw_items())
    combined = f"{header_text}\n{text}"

    ipv4 = unique(value for value in IPV4_RE.findall(combined) if valid_ipv4(value))
    wallets = {
        "bitcoin": unique(BITCOIN_BECH32_RE.findall(text) + BITCOIN_BASE58_RE.findall(text)),
        "ethereum": unique(ETHEREUM_RE.findall(text)),
    }
    return_path = str(message.get("Return-Path", ""))

    return {
        "file": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "headers": {
            "subject": str(message.get("Subject", "")),
            "from": str(message.get("From", "")),
            "to": str(message.get("To", "")),
            "date": str(message.get("Date", "")),
            "message_id": str(message.get("Message-ID", "")),
            "return_path": return_path,
            "received": [str(value) for value in message.get_all("Received", [])],
            "authentication_results": [str(value) for value in message.get_all("Authentication-Results", [])],
            "arc_authentication_results": [
                str(value) for value in message.get_all("ARC-Authentication-Results", [])
            ],
        },
        "authentication": authentication_summary(header_text),
        "provider_identifiers": {
            "sendgrid_account_ids": unique(SENDGRID_ACCOUNT_RE.findall(return_path)),
        },
        "indicators": {
            "urls": unique(value.rstrip(".,);]") for value in URL_RE.findall(text)),
            "email_addresses": unique(EMAIL_RE.findall(combined)),
            "ipv4_addresses": ipv4,
            "wallets": wallets,
        },
        "classification": classify(text, wallets),
        "body_preview": text[:1000],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eml", type=Path, help="Path to an RFC 822 .eml file")
    args = parser.parse_args()
    print(json.dumps(analyse(args.eml), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

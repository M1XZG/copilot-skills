import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "analyse_eml.py"
SPEC = importlib.util.spec_from_file_location("analyse_eml", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


MESSAGE = b"""\
Received: from outbound.example ([203.0.113.10]) by mx.example
Authentication-Results: mx.example; spf=pass smtp.mailfrom=sendgrid.net;
 dkim=pass header.i=@sendgrid.net; dmarc=fail header.from=gmail.com
Return-Path: <bounces+1234567-test=user.example@sendgrid.net>
From: Forged Sender <noreply@gmail.com>
To: user@example.com
Subject: Hello
Date: Tue, 11 Aug 2026 16:14:46 +0000
Message-ID: <example@provider>
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

I recorded your webcam using a Remote Access Trojan. Pay BTC within two days
or the explicit recordings will be shared with your contacts.
Send it to bc1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq.
"""


class AnalyseEmlTests(unittest.TestCase):
    def test_extracts_spoofing_and_wallet_indicators(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.eml"
            path.write_bytes(MESSAGE)
            result = MODULE.analyse(path)

        self.assertEqual(result["authentication"]["dmarc"], ["fail"])
        self.assertEqual(result["authentication"]["dkim"], ["pass"])
        self.assertEqual(result["provider_identifiers"]["sendgrid_account_ids"], ["1234567"])
        self.assertIn(
            "bounces+1234567-test=user.example@sendgrid.net",
            result["indicators"]["email_addresses"],
        )
        self.assertIn(
            "bc1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
            result["indicators"]["wallets"]["bitcoin"],
        )
        self.assertIn("sextortion", result["classification"])
        self.assertIn("cryptocurrency-blackmail", result["classification"])


if __name__ == "__main__":
    unittest.main()

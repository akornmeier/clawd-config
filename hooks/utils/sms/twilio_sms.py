#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "twilio",
#     "python-dotenv",
# ]
# ///

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def send_twilio_sms(to, message):
    """Send SMS via Twilio REST API."""
    from twilio.rest import Client

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print("Twilio not configured (missing SID, token, or from number)", file=sys.stderr)
        return False

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(body=message, from_=from_number, to=to)
        print(f"SMS sent: {msg.sid}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Twilio error: {e}", file=sys.stderr)
        return False


def send_imessage_fallback(to, message):
    """Fallback: send via iMessage using osascript."""
    safe_message = message.replace("\\", "\\\\").replace('"', '\\"')
    safe_to = to.replace("\\", "\\\\").replace('"', '\\"')
    script = f'tell application "Messages" to send "{safe_message}" to buddy "{safe_to}"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        print("iMessage sent (fallback)", file=sys.stderr)
        return True
    except Exception as e:
        print(f"iMessage fallback failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send SMS notification")
    parser.add_argument("--to", required=True, help="Recipient phone number")
    parser.add_argument("--message", required=True, help="Message text")
    args = parser.parse_args()

    # Load environment variables from .env.local (same pattern as TTS utilities)
    env_file = Path.home() / ".claude" / ".env.local"
    if env_file.exists():
        load_dotenv(env_file)
    load_dotenv()  # Also check standard .env

    if send_twilio_sms(args.to, args.message):
        return

    # Graceful fallback to iMessage
    print("Falling back to iMessage...", file=sys.stderr)
    send_imessage_fallback(args.to, args.message)


if __name__ == "__main__":
    main()

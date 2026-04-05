#!/usr/bin/env python3
"""
signal-queue: Poll signal-cli HTTP JSON-RPC for incoming messages.

Writes each authorized inbound message to two places:
  inbox/{timestamp}_{feed}.json   — trigger file (wakes Cleo via signal-wait)
  history/{feed}.jsonl            — append-only conversation log

Run as a systemd service. Exits cleanly on SIGTERM.
"""

import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).parent
CONFIG_FILE = PROJECT_DIR / "config.yaml"
INBOX = PROJECT_DIR / "inbox"
HISTORY = PROJECT_DIR / "history"
POLL_INTERVAL = 2  # seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] signal-queue: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger("signal-queue")


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------

def is_authorized(sender: str, group_id: str | None, cfg: dict) -> bool:
    """Return True if this sender/group combination is permitted."""
    authorized_senders = set(cfg.get("authorized_senders", []))
    authorized_groups = set(cfg.get("authorized_groups", []))

    if sender in authorized_senders:
        return True
    if group_id and group_id in authorized_groups:
        return True
    return False


# ---------------------------------------------------------------------------
# Feed ID and filename helpers
# ---------------------------------------------------------------------------

def feed_id(sender: str, group_id: str | None) -> str:
    """Canonical feed identifier: phone number for DMs, group.{id} for groups."""
    if group_id:
        return f"group.{group_id}"
    return sender


def safe_name(fid: str) -> str:
    """Filesystem-safe version of a feed ID."""
    return (fid
            .replace("+", "p")
            .replace("/", "_")
            .replace("=", "")
            .replace(".", "_"))


# ---------------------------------------------------------------------------
# Deduplication: track timestamps we've already written
# ---------------------------------------------------------------------------

_seen: set[str] = set()


def already_seen(ts: int, fid: str) -> bool:
    key = f"{ts}_{fid}"
    if key in _seen:
        return True
    _seen.add(key)
    # Limit memory growth
    if len(_seen) > 10_000:
        oldest = sorted(_seen)[:5_000]
        for k in oldest:
            _seen.discard(k)
    return False


# ---------------------------------------------------------------------------
# Message processing
# ---------------------------------------------------------------------------

def process_envelope(envelope: dict, cfg: dict) -> None:
    """Extract a usable message from an envelope and write it to disk."""
    # Sender info
    source = envelope.get("sourceNumber") or envelope.get("source", "")
    source_uuid = envelope.get("sourceUuid", "")
    sender = source or (f"uuid:{source_uuid}" if source_uuid else "")
    sender_name = envelope.get("sourceName", "")

    if not sender:
        return  # can't identify sender

    # Get the actual message content
    data = envelope.get("dataMessage")
    if not data:
        # Synced sent message from one of our own devices — skip
        sync = envelope.get("syncMessage", {})
        if sync.get("sentMessage"):
            return
        return  # typing indicators, receipts, etc.

    text = data.get("message") or ""
    attachments = data.get("attachments", [])

    if not text and not attachments:
        return  # empty / reaction-only

    # Group context
    group_info = data.get("groupInfo") or data.get("groupContext") or {}
    group_id = group_info.get("groupId") or None
    group_name = group_info.get("title", "") or ""

    # Authorization check
    if not is_authorized(sender, group_id, cfg):
        log.debug("Dropping unauthorized message from %s", sender)
        return

    ts = envelope.get("timestamp", int(time.time() * 1000))
    fid = feed_id(sender, group_id)

    if already_seen(ts, fid):
        return

    # Build record
    record = {
        "timestamp": ts,
        "from": sender,
        "from_name": sender_name,
        "feed_id": fid,
        "text": text,
        "attachments": [a.get("filename") or a.get("id", "") for a in attachments],
        "type": "group" if group_id else "dm",
        "group_name": group_name,
    }

    safe = safe_name(fid)

    # Append to history (always)
    HISTORY.mkdir(exist_ok=True)
    history_file = HISTORY / f"{safe}.jsonl"
    with history_file.open("a") as f:
        f.write(json.dumps(record) + "\n")

    # Write inbox trigger (idempotent)
    INBOX.mkdir(exist_ok=True)
    inbox_file = INBOX / f"{ts}_{safe}.json"
    if not inbox_file.exists():
        inbox_file.write_text(json.dumps(record, indent=2))

    preview = text[:60] if text else f"[{len(attachments)} attachment(s)]"
    log.info("%s → %s", fid, preview)


# ---------------------------------------------------------------------------
# Polling loop
# ---------------------------------------------------------------------------

def receive(rpc_url: str, bot_number: str) -> list[dict]:
    resp = requests.post(
        rpc_url,
        json={
            "jsonrpc": "2.0",
            "method": "receive",
            "params": {},
            "id": 1,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        log.warning("receive error: %s", data["error"])
        return []
    result = data.get("result", [])
    # result may be a list of {envelope: ...} dicts
    return result if isinstance(result, list) else []


_running = True


def _handle_sigterm(sig, frame):
    global _running
    log.info("SIGTERM received, shutting down")
    _running = False


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_sigterm)

    cfg = load_config()
    bot_number = cfg["bot_number"]
    rpc_url = cfg.get("signal_rpc_url", "http://127.0.0.1:8080/api/v1/rpc")

    INBOX.mkdir(exist_ok=True)
    HISTORY.mkdir(exist_ok=True)

    log.info("Starting — bot=%s rpc=%s poll=%ds", bot_number, rpc_url, POLL_INTERVAL)

    while _running:
        try:
            messages = receive(rpc_url, bot_number)
            for msg in messages:
                envelope = msg.get("envelope") if isinstance(msg, dict) else None
                if envelope:
                    try:
                        process_envelope(envelope, cfg)
                    except Exception as e:
                        log.exception("Error processing envelope: %s", e)
        except requests.exceptions.ConnectionError:
            log.warning("signal-cli unreachable, will retry")
        except Exception as e:
            log.exception("Poll error: %s", e)

        time.sleep(POLL_INTERVAL)

    log.info("Stopped.")


if __name__ == "__main__":
    main()

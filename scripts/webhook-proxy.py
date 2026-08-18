#!/usr/bin/env python3
"""Basecamp → Hermes webhook signature proxy.

Basecamp 3 sends no HMAC. Hermes requires HMAC V2. This proxy:
  - checks User-Agent == "Basecamp3 Webhook"
  - checks recording.bucket.id == BASECAMP_EXPECTED_BUCKET (PROJECT id, not account)
  - injects X-Webhook-Signature-V2 + X-Webhook-Timestamp
  - injects X-Request-ID=basecamp-{kind}-{recording_id} for Hermes idempotency

Env:
  BASECAMP_WEBHOOK_SECRET   required
  BASECAMP_EXPECTED_BUCKET  required (integer project / bucket id)
  HERMES_WEBHOOK_URL        default http://127.0.0.1:8644/webhooks/basecamp-todo
  PROXY_LISTEN_HOST         default 127.0.0.1  (keep loopback; terminate TLS elsewhere)
  PROXY_LISTEN_PORT         default 9876
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import logging.handlers
import os
from datetime import datetime, timezone

from aiohttp import ClientSession, ClientTimeout, web

EXPECTED_UA = "Basecamp3 Webhook"
HERMES_URL = os.environ.get(
    "HERMES_WEBHOOK_URL", "http://127.0.0.1:8644/webhooks/basecamp-todo"
)
LISTEN_HOST = os.environ.get("PROXY_LISTEN_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("PROXY_LISTEN_PORT", "9876"))
LOG_PATH = os.environ.get("PROXY_LOG_PATH", "/tmp/basecamp-webhook-proxy.log")

logger = logging.getLogger("webhook-proxy")
logger.setLevel(logging.INFO)
_handler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3)
_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(_handler)

_client_session: ClientSession | None = None


def _expected_bucket() -> int:
    raw = os.environ.get("BASECAMP_EXPECTED_BUCKET", "")
    if not raw:
        raise RuntimeError("BASECAMP_EXPECTED_BUCKET is required (Basecamp project id)")
    return int(raw)


async def handle_post(request: web.Request) -> web.Response:
    path = request.path
    raw = await request.read()

    ua = request.headers.get("User-Agent", "")
    if ua != EXPECTED_UA:
        logger.info("%s 403 bad-ua ua=%r", path, ua)
        return web.Response(status=403, text="Forbidden: bad User-Agent")

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        logger.info("%s 400 bad-json", path)
        return web.Response(status=400, text="Bad Request: invalid JSON")

    recording = payload.get("recording") if isinstance(payload, dict) else None
    bucket_id = None
    recording_id = None
    recording_kind = payload.get("kind", "unknown") if isinstance(payload, dict) else "unknown"
    if isinstance(recording, dict):
        bucket = recording.get("bucket")
        if isinstance(bucket, dict):
            bucket_id = bucket.get("id")
        recording_id = recording.get("id")

    try:
        expected = _expected_bucket()
    except Exception as exc:
        logger.error("%s 500 %s", path, exc)
        return web.Response(status=500, text="Server error: bucket not configured")

    if bucket_id != expected:
        logger.info("%s 403 bad-bucket bucket_id=%s expected=%s", path, bucket_id, expected)
        return web.Response(status=403, text="Forbidden: wrong project bucket")

    secret = os.environ.get("BASECAMP_WEBHOOK_SECRET", "")
    if not secret:
        logger.error("%s 500 missing-secret", path)
        return web.Response(status=500, text="Server error: secret not configured")

    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signed_content = timestamp.encode() + b"." + raw
    sig = hmac.new(secret.encode(), signed_content, hashlib.sha256).hexdigest()

    headers = dict(request.headers)
    headers["X-Webhook-Signature-V2"] = sig
    headers["X-Webhook-Timestamp"] = timestamp
    headers.pop("Host", None)
    headers.pop("Content-Length", None)
    if recording_id is not None:
        headers["X-Request-ID"] = f"basecamp-{recording_kind}-{recording_id}"

    assert _client_session is not None
    try:
        async with _client_session.post(HERMES_URL, data=raw, headers=headers) as upstream:
            status = upstream.status
            body = await upstream.read()
            resp_headers = {
                k: v
                for k, v in upstream.headers.items()
                if k.lower()
                not in ("transfer-encoding", "content-encoding", "content-length", "connection")
            }
            logger.info(
                "%s %s forwarded rec_id=%s kind=%s", path, status, recording_id, recording_kind
            )
            return web.Response(status=status, body=body, headers=resp_headers)
    except Exception as exc:
        logger.error("%s 502 upstream-error %s", path, exc)
        return web.Response(status=502, text=f"Bad Gateway: {exc}")


async def health(_request: web.Request) -> web.Response:
    return web.Response(text="ok")


async def on_startup(_app: web.Application) -> None:
    global _client_session
    _client_session = ClientSession(
        timeout=ClientTimeout(total=15),
        headers={"Content-Type": "application/json"},
    )
    logger.info("proxy started on %s:%s", LISTEN_HOST, LISTEN_PORT)


async def on_cleanup(_app: web.Application) -> None:
    global _client_session
    if _client_session and not _client_session.closed:
        await _client_session.close()
    logger.info("proxy stopped")


def main() -> None:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_post("/{tail:.*}", handle_post)
    app.router.add_get("/health", health)
    web.run_app(app, host=LISTEN_HOST, port=LISTEN_PORT, print=lambda *_a: None)


if __name__ == "__main__":
    main()

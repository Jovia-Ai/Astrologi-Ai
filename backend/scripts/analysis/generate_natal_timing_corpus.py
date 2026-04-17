"""Generate a minimal natal timing corpus by calling timing-instrumented endpoints."""
from __future__ import annotations

import argparse
import json
import time
from typing import Any
from urllib import error, request
from uuid import uuid4


DEFAULT_PAYLOAD = {
    "birth_date": "1996-12-28",
    "birth_time": "07:10",
    "birth_place": "Istanbul, TR",
    "locale": "tr",
    "summary_only": False,
}


def _post_json(base_url: str, endpoint: str, payload: dict[str, Any], request_id: str, timeout: float) -> tuple[int, int]:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{base_url.rstrip('/')}{endpoint}",
        data=raw,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
        },
    )
    with request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - local backend endpoint
        body = response.read()
        return int(response.status), len(body)


def _run_series(
    *,
    base_url: str,
    endpoint: str,
    count: int,
    payload: dict[str, Any],
    timeout: float,
    sleep_ms: int,
    request_prefix: str,
) -> tuple[int, int]:
    ok = 0
    failed = 0
    for index in range(count):
        request_id = f"{request_prefix}-{endpoint.strip('/').replace('/', '_')}-{index:03d}-{uuid4().hex[:8]}"
        try:
            status, size = _post_json(base_url, endpoint, payload, request_id, timeout)
        except error.HTTPError as exc:
            failed += 1
            print(f"[{endpoint}] #{index + 1}: HTTP {exc.code} request_id={request_id}")
        except Exception as exc:  # pragma: no cover - network/runtime issues
            failed += 1
            print(f"[{endpoint}] #{index + 1}: ERROR {exc} request_id={request_id}")
        else:
            ok += 1
            print(f"[{endpoint}] #{index + 1}: status={status} bytes={size} request_id={request_id}")
        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)
    return ok, failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL.")
    parser.add_argument("--interpret-ui-count", type=int, default=10, help="Number of /interpret/ui requests.")
    parser.add_argument("--interpret-count", type=int, default=10, help="Number of /interpret requests.")
    parser.add_argument("--profile-fast-count", type=int, default=0, help="Optional number of /profile/fast requests.")
    parser.add_argument("--timeout", type=float, default=60.0, help="Request timeout in seconds.")
    parser.add_argument("--sleep-ms", type=int, default=0, help="Delay between requests.")
    parser.add_argument(
        "--request-prefix",
        default="natal-corpus",
        help="Prefix for generated X-Request-Id values.",
    )
    args = parser.parse_args()

    totals = {"ok": 0, "failed": 0}

    ok, failed = _run_series(
        base_url=args.base_url,
        endpoint="/interpret/ui",
        count=args.interpret_ui_count,
        payload=dict(DEFAULT_PAYLOAD),
        timeout=args.timeout,
        sleep_ms=args.sleep_ms,
        request_prefix=args.request_prefix,
    )
    totals["ok"] += ok
    totals["failed"] += failed

    ok, failed = _run_series(
        base_url=args.base_url,
        endpoint="/interpret",
        count=args.interpret_count,
        payload=dict(DEFAULT_PAYLOAD),
        timeout=args.timeout,
        sleep_ms=args.sleep_ms,
        request_prefix=args.request_prefix,
    )
    totals["ok"] += ok
    totals["failed"] += failed

    if args.profile_fast_count > 0:
        ok, failed = _run_series(
            base_url=args.base_url,
            endpoint="/profile/fast",
            count=args.profile_fast_count,
            payload=dict(DEFAULT_PAYLOAD),
            timeout=args.timeout,
            sleep_ms=args.sleep_ms,
            request_prefix=args.request_prefix,
        )
        totals["ok"] += ok
        totals["failed"] += failed

    print(
        "Corpus generation finished: "
        f"ok={totals['ok']} failed={totals['failed']} "
        f"base_url={args.base_url.rstrip('/')}"
    )


if __name__ == "__main__":
    main()

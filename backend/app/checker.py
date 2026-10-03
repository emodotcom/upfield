import asyncio
import time

import aiohttp


async def check_url(url: str, timeout_seconds: int = 10) -> dict:
    """
    Perform a single HTTP GET health check against *url*.

    Returns a dict with:
        is_up          bool   — True if HTTP status < 400
        status_code    int|None
        response_time_ms float
        error_message  str|None
    """
    start = time.monotonic()

    try:
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout, allow_redirects=True, ssl=False) as resp:
                elapsed_ms = (time.monotonic() - start) * 1000
                return {
                    "is_up": resp.status < 400,
                    "status_code": resp.status,
                    "response_time_ms": round(elapsed_ms, 2),
                    "error_message": None,
                }

    except aiohttp.ClientConnectorError as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "is_up": False,
            "status_code": None,
            "response_time_ms": round(elapsed_ms, 2),
            "error_message": f"Connection error: {exc}",
        }

    except asyncio.TimeoutError:
        return {
            "is_up": False,
            "status_code": None,
            "response_time_ms": timeout_seconds * 1000.0,
            "error_message": f"Timed out after {timeout_seconds}s",
        }

    except Exception as exc:  # noqa: BLE001
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "is_up": False,
            "status_code": None,
            "response_time_ms": round(elapsed_ms, 2),
            "error_message": str(exc),
        }

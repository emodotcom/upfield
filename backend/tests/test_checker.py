"""Tests for the HTTP health checker."""
import pytest
from app.checker import check_url


@pytest.mark.asyncio
async def test_check_valid_url():
    result = await check_url("https://httpbin.org/status/200")
    assert result["is_up"] is True
    assert result["status_code"] == 200
    assert result["response_time_ms"] > 0
    assert result["error_message"] is None


@pytest.mark.asyncio
async def test_check_404_is_down():
    result = await check_url("https://httpbin.org/status/404")
    assert result["is_up"] is False
    assert result["status_code"] == 404


@pytest.mark.asyncio
async def test_check_nonexistent_domain():
    result = await check_url("https://this-domain-does-not-exist-upfield.xyz")
    assert result["is_up"] is False
    assert result["error_message"] is not None


@pytest.mark.asyncio
async def test_check_timeout():
    # httpbin's /delay/15 will exceed our 3s timeout
    result = await check_url("https://httpbin.org/delay/15", timeout_seconds=3)
    assert result["is_up"] is False

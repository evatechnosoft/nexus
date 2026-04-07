"""
Pytest configuration and shared fixtures for Nexus MCP Server tests.

Provides:
- base_url fixture: Nexus server endpoint
- httpx client setup for sync integration tests
"""

import os

import httpx
import pytest

# Override via NEXUS_BASE_URL env var in CI (GitHub Actions sets this)
BASE_URL = os.getenv("NEXUS_BASE_URL", "http://192.168.1.186:8900")
REQUEST_TIMEOUT = float(os.getenv("NEXUS_TIMEOUT", "10.0"))


@pytest.fixture
def base_url() -> str:
    """Nexus MCP Server base URL."""
    return BASE_URL


@pytest.fixture
def client() -> httpx.Client:
    """Synchronous httpx client for Nexus server."""
    with httpx.Client(base_url=BASE_URL, timeout=REQUEST_TIMEOUT) as c:
        yield c


@pytest.fixture(scope="session")
def server_health() -> dict:
    """Verify server is up before running tests."""
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert "status" in data, "Health endpoint missing 'status' field"
        return data
    except Exception as e:
        pytest.skip(f"Nexus server unreachable at {BASE_URL}: {e}")

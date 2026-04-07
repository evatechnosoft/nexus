"""
Integration tests for Nexus Memory CRUD operations.

Tests:
- GET /api/memory/profile → retrieve memory profile
- PUT /api/memory/{key} → store memory value
- GET /api/memory/{key} → retrieve stored value
- DELETE /api/memory/{key} → delete memory entry
- 404 handling for missing keys
"""

import pytest
import httpx


class TestMemoryRead:
    """Memory read operations."""

    def test_memory_profile_returns_200(self, client):
        """GET /api/memory/profile returns 200."""
        response = client.get("/api/memory/profile")
        assert response.status_code == 200

    def test_memory_profile_returns_json(self, client):
        """GET /api/memory/profile returns valid JSON."""
        response = client.get("/api/memory/profile")
        data = response.json()
        assert isinstance(data, dict), "Profile should be a dict"


class TestMemoryWrite:
    """Memory write/create operations."""

    def test_memory_put_returns_200(self, client):
        """PUT /api/memory/{key} returns 200."""
        response = client.put(
            "/api/memory/test_nexus_ci",
            json={"content": "ci-test-value"}
        )
        assert response.status_code == 200

    def test_memory_put_stores_value(self, client):
        """PUT /api/memory/{key} stores value successfully."""
        # Write
        write_response = client.put(
            "/api/memory/test_nexus_store",
            json={"content": "test-storage-value"}
        )
        assert write_response.status_code == 200

        # Read back
        read_response = client.get("/api/memory/test_nexus_store")
        assert read_response.status_code == 200
        data = read_response.json()
        assert "test-storage-value" in str(data), \
            "Stored value should be retrievable"

    def test_memory_put_overwrites_existing(self, client):
        """PUT /api/memory/{key} overwrites previous value."""
        key = "test_nexus_overwrite"

        # Write first value
        client.put(f"/api/memory/{key}", json={"content": "first-value"})

        # Write second value
        response = client.put(
            f"/api/memory/{key}",
            json={"content": "second-value"}
        )
        assert response.status_code == 200

        # Verify second value is stored
        read_response = client.get(f"/api/memory/{key}")
        data = read_response.json()
        assert "second-value" in str(data), "Should have second value"


class TestMemoryRead2:
    """Memory retrieval tests (after write)."""

    def test_memory_get_stored_value(self, client):
        """GET /api/memory/{key} returns stored value."""
        key = "test_nexus_read_verify"
        expected_content = "read-verify-test"

        # Write
        client.put(f"/api/memory/{key}", json={"content": expected_content})

        # Read
        response = client.get(f"/api/memory/{key}")
        assert response.status_code == 200
        data = response.json()
        assert expected_content in str(data), "Should contain stored content"

    def test_memory_get_includes_timestamp(self, client):
        """GET /api/memory/{key} may include timestamp metadata."""
        key = "test_nexus_timestamp"
        client.put(f"/api/memory/{key}", json={"content": "timestamp-test"})

        response = client.get(f"/api/memory/{key}")
        data = response.json()
        # Metadata optional but useful
        assert isinstance(data, dict)


class TestMemoryDelete:
    """Memory deletion operations."""

    def test_memory_delete_returns_200(self, client):
        """DELETE /api/memory/{key} returns 200."""
        key = "test_nexus_delete"

        # Create
        client.put(f"/api/memory/{key}", json={"content": "to-delete"})

        # Delete
        response = client.delete(f"/api/memory/{key}")
        assert response.status_code == 200

    def test_memory_delete_removes_entry(self, client):
        """After DELETE, GET returns 404."""
        key = "test_nexus_delete_verify"

        # Create
        client.put(f"/api/memory/{key}", json={"content": "delete-me"})

        # Delete
        client.delete(f"/api/memory/{key}")

        # Verify deleted
        response = client.get(f"/api/memory/{key}")
        assert response.status_code == 404, "Deleted key should return 404"

    def test_memory_delete_nonexistent_key(self, client):
        """DELETE nonexistent key should return 404 or 200."""
        response = client.delete("/api/memory/nonexistent_key_xyz")
        # Behavior varies: some APIs return 200 (idempotent), others 404
        assert response.status_code in [200, 404]


class TestMemoryNotFound:
    """404 error handling."""

    def test_memory_get_missing_returns_404(self, client):
        """GET /api/memory/{key} returns 404 for missing key."""
        response = client.get("/api/memory/definitely_not_stored_xyz")
        assert response.status_code == 404

    def test_memory_error_response_structure(self, client):
        """404 response includes error details."""
        response = client.get("/api/memory/missing_key")
        assert response.status_code == 404
        # May have error field
        try:
            data = response.json()
            assert "error" in data or "message" in data or "detail" in data
        except ValueError:
            # Not JSON is acceptable for 404
            pass


class TestMemoryIntegration:
    """Full CRUD workflow."""

    def test_memory_crud_workflow(self, client):
        """Complete CRUD cycle: Create → Read → Update → Delete."""
        key = "test_nexus_crud_workflow"

        # Create
        create_resp = client.put(
            f"/api/memory/{key}",
            json={"content": "initial-value"}
        )
        assert create_resp.status_code == 200

        # Read
        read_resp = client.get(f"/api/memory/{key}")
        assert read_resp.status_code == 200
        assert "initial-value" in str(read_resp.json())

        # Update
        update_resp = client.put(
            f"/api/memory/{key}",
            json={"content": "updated-value"}
        )
        assert update_resp.status_code == 200

        # Verify update
        verify_resp = client.get(f"/api/memory/{key}")
        assert "updated-value" in str(verify_resp.json())

        # Delete
        delete_resp = client.delete(f"/api/memory/{key}")
        assert delete_resp.status_code == 200

        # Verify deletion
        final_resp = client.get(f"/api/memory/{key}")
        assert final_resp.status_code == 404

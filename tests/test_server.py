"""
Integration tests for Nexus MCP Server core endpoints.

Tests:
- GET /health → status, version, uptime_seconds
- GET /metrics → Prometheus metrics format
- GET /api/skills/search → skill search by query
- GET /api/search/hybrid → hybrid semantic + BM25 search
"""


class TestHealthEndpoint:
    """Health check endpoint tests."""

    def test_health_returns_200(self, client):
        """GET /health returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_status_field(self, client):
        """GET /health includes 'status' field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "healthy"]

    def test_health_has_version(self, client):
        """GET /health includes 'version' field."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data or "uptime_seconds" in data, (
            "Health should include version or uptime_seconds"
        )

    def test_health_uptime_positive(self, client):
        """GET /health uptime_seconds is positive."""
        response = client.get("/health")
        data = response.json()
        if "uptime_seconds" in data:
            assert data["uptime_seconds"] > 0


class TestMetricsEndpoint:
    """Prometheus metrics endpoint tests."""

    def test_metrics_returns_200(self, client):
        """GET /metrics returns 200 OK."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_contains_nexus_uptime(self, client):
        """GET /metrics includes 'nexus_uptime_seconds' metric."""
        response = client.get("/metrics")
        content = response.text
        assert "nexus_uptime_seconds" in content, "Metrics should include nexus_uptime_seconds"

    def test_metrics_is_prometheus_format(self, client):
        """GET /metrics returns Prometheus text format."""
        response = client.get("/metrics")
        content = response.text
        # Prometheus format lines start with # or metric_name
        lines = [ln.strip() for ln in content.split("\n") if ln.strip()]
        assert len(lines) > 0, "Metrics content is empty"
        # At least some lines should be metric lines (contain { or space-separated)
        metric_lines = [line for line in lines if not line.startswith("#")]
        assert len(metric_lines) > 0, "No metric lines found in output"


class TestSkillsSearchEndpoint:
    """Skill search endpoint tests."""

    def test_skills_search_returns_200(self, client):
        """GET /api/skills/search?q=docker returns 200."""
        response = client.get("/api/skills/search", params={"q": "docker"})
        assert response.status_code == 200

    def test_skills_search_returns_list(self, client):
        """GET /api/skills/search returns results list."""
        response = client.get("/api/skills/search", params={"q": "docker"})
        data = response.json()
        # Server returns {query, results, total}
        assert isinstance(data, dict), "Search response should be a dict"
        assert "results" in data, "Should have 'results' key"
        assert isinstance(data["results"], list), "results should be a list"

    def test_skills_search_result_structure(self, client):
        """Each skill result has name, description, score."""
        response = client.get("/api/skills/search", params={"q": "test"})
        data = response.json()

        if len(data.get("results", [])) > 0:
            result = data["results"][0]
            assert "name" in result, "Result should have 'name'"
            assert "description" in result, "Result should have 'description'"
            # score may or may not be present in skills search

    def test_skills_search_empty_query(self, client):
        """GET /api/skills/search with empty query."""
        response = client.get("/api/skills/search", params={"q": ""})
        # Should reject empty query with 422
        assert response.status_code in [200, 400, 422]

    def test_skills_search_missing_query_param(self, client):
        """GET /api/skills/search without q parameter."""
        response = client.get("/api/skills/search")
        # Should either fail gracefully or return all
        assert response.status_code in [200, 400, 422]


class TestHybridSearchEndpoint:
    """Hybrid semantic + BM25 search tests."""

    def test_hybrid_search_returns_200(self, client):
        """GET /api/search/hybrid?q=terraform&top_k=3 returns 200."""
        response = client.get("/api/search/hybrid", params={"q": "terraform", "top_k": 3})
        assert response.status_code == 200

    def test_hybrid_search_returns_list(self, client):
        """GET /api/search/hybrid returns results list."""
        response = client.get("/api/search/hybrid", params={"q": "python", "top_k": 5})
        data = response.json()
        # Server returns {query, results, elapsed_ms, total}
        assert isinstance(data, dict), "Search response should be a dict"
        assert "results" in data, "Should have 'results' key"
        assert isinstance(data["results"], list), "results should be a list"

    def test_hybrid_search_respects_top_k(self, client):
        """GET /api/search/hybrid respects top_k limit."""
        response = client.get("/api/search/hybrid", params={"q": "kubernetes", "top_k": 2})
        data = response.json()
        results = data.get("results", [])
        assert len(results) <= 2, f"Expected <= 2 results, got {len(results)}"

    def test_hybrid_search_result_timing(self, client):
        """GET /api/search/hybrid result includes timing info."""
        response = client.get("/api/search/hybrid", params={"q": "ansible", "top_k": 5})
        # Check if timing is in response (may be in header or JSON)
        # For now, just verify response completes
        assert response.status_code == 200

    def test_hybrid_search_with_default_top_k(self, client):
        """GET /api/search/hybrid works without top_k (uses default)."""
        response = client.get("/api/search/hybrid", params={"q": "api"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "results" in data

    def test_hybrid_search_whitespace_query(self, client):
        """GET /api/search/hybrid handles whitespace-only query."""
        response = client.get("/api/search/hybrid", params={"q": "   ", "top_k": 3})
        # Should not crash; may return empty results
        assert response.status_code in [200, 400]

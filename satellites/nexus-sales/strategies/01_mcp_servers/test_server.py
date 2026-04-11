import pytest
from server import mcp

@pytest.mark.asyncio
async def test_analyze_site():
    result = await mcp.call_tool("analyze_site", {"url": "https://test.com"})
    # FastMCP ToolResult content listesini kontrol et
    assert any("Analysis triggered" in c.text for c in result.content)
    assert any("test.com" in c.text for c in result.content)

@pytest.mark.asyncio
async def test_collect_lead():
    result = await mcp.call_tool("collect_lead", {"source": "Test", "contact_info": "test@eva.com"})
    assert any("captured successfully" in c.text for c in result.content)

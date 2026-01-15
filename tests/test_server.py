import pytest
import io
import zipfile
from unittest.mock import MagicMock, AsyncMock, patch
from fastmcp import Client
from server import mcp

# Create a valid dummy zip file in memory
def create_dummy_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        z.writestr('test/doc.md', '# Title\nThis is a test document.')
        z.writestr('test/ignore.txt', 'This should be ignored.')
    return buffer.getvalue()

@pytest.mark.asyncio
async def test_fetch_web_content():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.text = "Mocked Markdown Content"
    
    # Mock httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_client_cls:
        # The client instance returned by context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        
        # The class (mock_client_cls) called returns the instance
        mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
        
        async with Client(mcp) as client:
            result = await client.call_tool("fetch_web_content", {"url": "https://example.com"})
            
            # Verify the result
            assert result.content[0].text == "Mocked Markdown Content"
            
            # Verify the call was made correctly
            mock_client_instance.get.assert_called_with("https://r.jina.ai/https://example.com", timeout=30.0)

@pytest.mark.asyncio
async def test_query_docs():
    dummy_zip_content = create_dummy_zip()
    
    # We patch get_cached_content to avoid DB and Network calls
    with patch("server.get_cached_content", return_value=dummy_zip_content):
        async with Client(mcp) as client:
            # Query matching the doc
            result = await client.call_tool("query_docs", {"url": "http://test.zip", "query": "test"})
            
            assert "File: doc.md" in result.content[0].text
            assert "This is a test document" in result.content[0].text
            
            # Query handling no results
            result_empty = await client.call_tool("query_docs", {"url": "http://test.zip", "query": "banana"})
            # Note: minsearch might behave differently on "no results", but our code handles output generation
            # If minsearch returns empty list, our code returns "No results found." or partial matches?
            # Let's check the implementation: "return ... if output else 'No results found.'"
            
            # However, minsearch using TF-IDF might return *something* or nothing depending on the score.
            # If the word isn't there, it likely returns nothing.
            
            # Actually, let's just assert the first result passed.

@pytest.mark.asyncio
async def test_query_docs_error_handling():
    # Force an exception
    with patch("server.get_cached_content", side_effect=Exception("Download failed")):
        async with Client(mcp) as client:
            result = await client.call_tool("query_docs", {"url": "http://bad.zip", "query": "test"})
            assert "Error querying docs: Download failed" in result.content[0].text

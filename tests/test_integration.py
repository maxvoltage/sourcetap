import asyncio
from fastmcp import Client
from server import mcp

async def test_fetch_web_content():
    url = "https://example.com"
    print(f"Fetching content from {url}...")
    
    # Use Client with in-memory transport to test the server directly
    async with Client(mcp) as client:
        try:
            result = await client.call_tool("fetch_web_content", {"url": url})
            content = result.content[0].text
            print("Successfully fetched content!")
            print("-" * 50)
            print(content)
            # Simple assertion for Example Domain content
            if "Example Domain" in content:
                print("✅ Verification Passed: Found 'Example Domain'")
            else:
                print("❌ Verification Failed: 'Example Domain' not found")
            print("-" * 50)
        except Exception as e:
            print(f"Error fetching content: {e}")

async def test_query_docs():
    # specifically use a small, stable repo (Hello-World) to avoid large downloads and timeouts
    url = "https://github.com/maxvoltage/Hello-World/archive/refs/heads/master.zip"
    query = "Hello"
    print(f"\nQuerying docs from {url} with query '{query}'...")
    
    async with Client(mcp) as client:
        try:
            result = await client.call_tool("query_docs", {"url": url, "query": query})
            content = result.content[0].text
            print("Successfully queried docs!")
            print("-" * 50)
            print(content[:500] + "...") # Print preview
            
            # Simple assertion
            if "Hello World" in content:
                print("✅ Verification Passed: Found 'Hello World'")
            else:
                print("❌ Verification Failed: 'Hello World' not found")
            print("-" * 50)
        except Exception as e:
            print(f"Error querying docs: {e}")

async def main():
    print("Running Integration Tests...")
    await test_fetch_web_content()
    await test_query_docs()

if __name__ == "__main__":
    asyncio.run(main())

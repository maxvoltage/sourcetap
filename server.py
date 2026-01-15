# server.py
from fastmcp import FastMCP

mcp = FastMCP("SourceTap 🚰")


@mcp.tool
async def fetch_web_content(url: str) -> str:
    """Download content of any web page using Jina reader.
    
    Args:
        url: The URL of the web page to fetch content from.
    """
    import httpx
    jina_url = f"https://r.jina.ai/{url}"
    async with httpx.AsyncClient() as client:
        response = await client.get(jina_url, timeout=30.0)
        return response.text

def get_cached_content(url: str) -> bytes:
    """Retrieve content from SQLite cache or download and save it."""
    import sqlite3
    import requests
    
    db_name = "cache.db"
    with sqlite3.connect(db_name) as conn:
        # Enable WAL mode and normal synchronization for better performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS downloads (url TEXT PRIMARY KEY, content BLOB)")
        
        cursor.execute("SELECT content FROM downloads WHERE url = ?", (url,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
            
        # Download if not found (using requests for sync capability)
        response = requests.get(url)
        response.raise_for_status()
        content = response.content
        
        cursor.execute("INSERT INTO downloads (url, content) VALUES (?, ?)", (url, content))
        conn.commit()
        return content

@mcp.tool
def query_docs(url: str, query: str) -> str:
    """Index and search documentation from a ZIP archive URL.
    
    Args:
        url: URL to a ZIP file (e.g. GitHub archive)
        query: Search query
    """
    import zipfile
    import io
    from minsearch import Index
    
    try:
        # Get zip content (cached)
        zip_content = get_cached_content(url)
        
        # Extract and Index
        docs = []
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for file_info in z.infolist():
                if file_info.is_dir():
                    continue
                fname = file_info.filename
                if not (fname.endswith('.md') or fname.endswith('.mdx')):
                    continue
                
                parts = fname.split('/', 1)
                if len(parts) < 2:
                    continue
                new_fname = parts[1]
                
                with z.open(file_info) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                
                docs.append({
                    "filename": new_fname,
                    "content": content
                })
        
        index = Index(
            text_fields=["content", "filename"],
            keyword_fields=[]
        )
        index.fit(docs)
        
        # Search
        results = index.search(query, num_results=5)
        
        output = []
        for res in results:
            output.append(f"File: {res['filename']}\nContent Preview:\n{res['content']}...\n")
            
        return "\n---\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Error querying docs: {str(e)}"

if __name__ == "__main__":
    mcp.run()
# SourceTap

SourceTap is an MVP of a Model Context Protocol (MCP server that lets your AI assistant learn and search any library directly from its GitHub repository or documentation URL.

## Features

This project provides two tools:

1.  **`query_docs(url, query)`**: A RAG (Retrieval-Augmented Generation) tool.
    *   **Input**: Takes a URL to a ZIP archive (e.g., a GitHub repo archive) and a search query.
    *   **Process**: 
        *   Downloads the ZIP file (cached via SQLite to prevent redundant downloads).
        *   Extracts `.md` and `.mdx` content.
        *   Indexes the content in-memory using `minsearch` (TF-IDF/Keyword search).
    *   **Output**: Returns the full content of the top 5 most relevant documentation files.
    *   **Use Case**: Helps AI agents understand libraries that are too new, private, or obscure for their base references.

2.  **`fetch_web_content(url)`**: A reader tool.
    *   **Input**: Any webpage URL.
    *   **Process**: Proxies the request through `r.jina.ai` to convert HTML to clean, LLM-friendly Markdown.
    *   **Output**: The text content of the page.
    *   **Use Case**: Inspecting specific documentation pages, blog posts, or issue threads.

## Installation

To use this tool with your AI assistant (e.g., Claude Desktop, Cline), add the following configuration to your **MCP Settings** file:

```json
{
  "mcpServers": {
    "sourcetap": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/sourcetap",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

> **Note**: Replace `/absolute/path/to/sourcetap` with the actual path to this directory on your machine.
> The `uv` command will automatically handle dependency installation and environment setup when the server starts.

## Project Architecture

### The Tech Stack
- **MCP Framework:** FastMCP (Python)
- **Web Scraping:** Jina Reader API (via httpx)
- **Search Engine:** minsearch (TF-IDF/Keyword search)
- **Caching:** SQLite with WAL mode
- **Used MCP:** Context7
- **AI Assistant:** Google Gemini 3 Flash + Antigravity IDE

### Caching Strategy
The project uses **SQLite** for persistent caching of downloaded ZIP files.
- **WAL Mode:** Write-Ahead Logging enabled for better concurrent read/write performance.

### Search Implementation
Uses **minsearch** for in-memory document search.
- **Text Fields:** Indexes both `content` and `filename` for comprehensive search.
- **TF-IDF Scoring:** Ranks documents by term frequency-inverse document frequency.
- **Top-K Retrieval:** Returns the 5 most relevant documents per query.
- **Memory Efficient:** Index is rebuilt per query (no persistent index storage).

### Limitations & Possible Improvements
- **Keyword-Only Search:** Currently uses TF-IDF. Semantic search with embeddings (e.g., `all-MiniLM-L6-v2`) would enable conceptual matching.
- **Full-File Retrieval:** Returns entire files. Smart chunking by headers would improve precision.
- **Markdown-Only:** Only indexes `.md` and `.mdx` files. Code parsing (`.py`, `.ts`) would enable technical implementation queries.
- **ZIP Archives:** Downloads full repositories. GitHub Tree API would enable sparse downloading of only needed files.
- **No Persistent Index:** Index is rebuilt per query. Persistent indexing would improve performance for repeated queries.
- **Single-Threaded Cache:** SQLite cache is synchronous. Async cache operations would improve throughput.

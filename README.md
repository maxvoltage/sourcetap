# SourceTap

Can't find the documentation you need? This MCP server lets your AI assistant instantly learn and search any library directly from its GitHub repository or documentation URL.

## Features

This project provides a Model Context Protocol (MCP) server with two powerful tools:

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

## Future Roadmap

While functional, this system can be significantly improved to become a production-grade context engine:

*   **Semantic Search**: Replace `minsearch` (keyword-based) with local embeddings (e.g., `all-MiniLM-L6-v2`) to allow conceptual matching (e.g., searching for "login" finds "authentication").
*   **Smart Chunking**: Instead of indexing entire files, split documents by headers (`#`, `##`) to retrieve only the specific section relevant to the user's query.
*   **Code Parsing**: Extend indexing beyond Markdown to include code files (`.py`, `.ts`). Parse function signatures and docstrings to allow technically accurate questions about implementation details.
*   **Optimized Downloading**: Switch from downloading full ZIP archives to using the GitHub Tree API. This allows "sparse downloading"—fetching only the text files we need, saving massive amounts of bandwidth and memory.

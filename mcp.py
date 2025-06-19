import os
from typing import List
from fastmcp import FastMCP
from dotenv import load_dotenv

from markdown_cache import MarkdownCache, MarkdownCacheItem

load_dotenv()
MARKDOWN_DIR = os.environ["MARKDOWN_DIR"]

# Initialize FastMCP with server name
mcp = FastMCP("Siv3D Docs Search", debug=True)

# Initialize cache
markdown_cache = MarkdownCache(MARKDOWN_DIR)

@mcp.tool()
def search_markdown(query: str, limit: int = 5) -> List[MarkdownCacheItem]:
    """
    Search from Siv3D documentation for a given query using TF-IDF similarity.

    Args:
        query (str): Query string to search
        limit (int): Maximum number of results (default: 5)

    Returns:
        List[SearchResult]: Matched files with content and relevance score
    """
    return markdown_cache.search(query, limit)

if __name__ == "__main__":
    mcp.run(transport="sse")

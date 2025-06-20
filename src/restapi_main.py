import os
from typing import Annotated, List
from fastapi import FastAPI
from fastapi.params import Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from lib.markdown_cache import MarkdownCache

MARKDOWN_DIR = os.environ["MARKDOWN_DIR"]
EN_BASE_URL = os.environ["EN_BASE_URL"].removesuffix('/') + "/"
JA_BASE_URL = os.environ["JA_BASE_URL"].removesuffix('/') + "/"
OPENAPI_SERVER_URL = os.environ.get("SERVER_URL", "http://localhost")

# Initialize cache
markdown_cache = MarkdownCache(MARKDOWN_DIR)

app = FastAPI(
    title="Siv3D Documentation Search API",
    description="Search Siv3D documentation using TF-IDF similarity.",
    servers=[
        {"url": OPENAPI_SERVER_URL}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchResult(BaseModel):
    url_en: str = Field(..., title="URL of the English documentation")
    url_ja: str = Field(..., title="URL of the Japanese documentation")
    content: str = Field(..., title="Full content of the matched document in Markdown format")
    score: str = Field(
        ...,
        title="Relevance score of the match",
        description="High, Very High, Moderate, Weak, or Low based on TF-IDF similarity"
    )

def build_docs_url(base_url: str, file_path: str, include_anchor_link: bool = True) -> str:
    """
    Build the full URL for a documentation file.
    
    Args:
        base_url (str): Base URL for the documentation
        file_path (str): Relative path of the Markdown file
        include_anchor_link (bool): Whether to include the anchor link in the URL
    
    Returns:
        str: Full URL to the documentation file
    """
    path = file_path.removesuffix('.md').split('/')
    if path[-2] == 'index':
        del path[-2]

    if include_anchor_link:
        return base_url + '/'.join(path[:-1]) + f"#{path[-1]}"
    else:
        return base_url + '/'.join(path[:-1])

@app.post("/search")
def search_docs(
    query: Annotated[
        str,
        Query(
            ...,
            title="Query",
            description="Query string to search. Only English queries are supported"
        )
    ]
) -> List[SearchResult]:
    """
    Search Siv3D documentation for a given query using TF-IDF similarity.
    """

    result = markdown_cache.search(query, 10)

    return [
        SearchResult(
            url_en=build_docs_url(EN_BASE_URL, item.file),
            url_ja=build_docs_url(JA_BASE_URL, item.file, include_anchor_link=False),
            content=item.content,
            score=(
                "High" if item.score >= 0.90 else
                "Very High" if item.score >= 0.75 else
                "Moderate" if item.score >= 0.50 else
                "Weak" if item.score >= 0.30 else
                "Low"
            )
        ) for item in result
    ]

@app.get("/ping")
def ping():
    return PlainTextResponse(content="OK")

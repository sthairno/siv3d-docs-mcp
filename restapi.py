import os
from typing import Annotated, List
from fastapi import FastAPI
from fastapi.params import Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from markdown_cache import MarkdownCache

load_dotenv()
MARKDOWN_DIR = os.environ["MARKDOWN_DIR"]
EN_BASE_URL = os.environ["EN_BASE_URL"]
JA_BASE_URL = os.environ["JA_BASE_URL"]
OPENAPI_SERVER_URL = os.environ.get("SERVER_URL", "http://localhost")

# Initialize cache
markdown_cache = MarkdownCache(MARKDOWN_DIR)

app = FastAPI(servers=[
    {"url": OPENAPI_SERVER_URL}
])

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
    score: float = Field(..., title="Relevance score based on TF-IDF similarity")

@app.post("/search")
def search_docs(
    query: Annotated[
        str,
        Query(
            ...,
            title="Query",
            description="Query string to search. Only English queries are supported"
        )
    ],
    limit: Annotated[
        int,
        Query(
            ...,
            title="Limit",
            description="Maximum number of results to return",
        )
    ] = 10
) -> List[SearchResult]:
    """
    Search Siv3D documentation for a given query using TF-IDF similarity.
    """

    result = markdown_cache.search(query, limit)

    return [
        SearchResult(
            url_en=EN_BASE_URL + item.file.removesuffix('.md'),
            url_ja=JA_BASE_URL + item.file.removesuffix('.md'),
            content=item.content,
            score=item.score
        ) for item in result
    ]

@app.get("/ping")
def ping():
    return PlainTextResponse(content="OK")

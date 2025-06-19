import os
from typing import List
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from markdown_cache import MarkdownCache

load_dotenv()
MARKDOWN_DIR = os.environ["MARKDOWN_DIR"]
EN_BASE_URL = os.environ["EN_BASE_URL"]
JA_BASE_URL = os.environ["JA_BASE_URL"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache
markdown_cache = MarkdownCache(MARKDOWN_DIR)

class SearchResult(BaseModel):
    url_en: str
    url_ja: str = None
    content: str
    score: float

@app.post("/search")
def search_docs(query: str, limit: int = 10) -> List[SearchResult]:
    """
    Search Siv3D documentation for a given query using TF-IDF similarity.

    ## Parameters
    - query (str): Query string to search. Only English queries are supported.
    - limit (int): Maximum number of results (optional, default: 10)

    ## Returns
    - List: list of search results containing:
      - url_en (str): URL of the English documentation
      - url_ja (str): URL of the Japanese documentation
      - content (str): Full content of the matched document in Markdown format
      - score (float): Relevance score based on TF-IDF similarity
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

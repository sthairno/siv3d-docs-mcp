import os
import glob
from typing import List
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class MarkdownCacheItem(BaseModel):
    file: str      # Relative path of the matched file
    content: str   # Full content of the matched file
    score: float   # TF-IDF cosine similarity score

class MarkdownCache:
    def __init__(self, directory: str):
        """
        Load and vectorize Markdown files from the given directory.

        Args:
            directory (str): Path to the directory containing Markdown files
        """
        self.directory = directory
        self.documents = []
        self.metadata = []
        self.vectorizer = None
        self.doc_vectors = None
        self._load_documents()

    def _load_documents(self):
        """
        Read all .md files in the directory, skip empty ones, and compute TF-IDF vectors.
        """
        files = glob.glob(os.path.join(self.directory, "**/*.md"), recursive=True)
        self.documents = []
        self.metadata = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append(content)
                        self.metadata.append(os.path.relpath(file_path, self.directory).replace("\\", "/"))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        if not self.documents:
            print("[WARN] No markdown content found to index. Skipping TF-IDF vectorization.")
            self.vectorizer = TfidfVectorizer()
            self.doc_vectors = None
        else:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.doc_vectors = self.vectorizer.fit_transform(self.documents)

        print(f"[INFO] Loaded {len(self.documents)} Markdown documents from {self.directory}")

    def search(self, query: str, limit: int) -> List[MarkdownCacheItem]:
        """
        Perform a TF-IDF-based search over cached Markdown documents.

        Args:
            query (str): The search term or natural language query
            limit (int): Maximum number of results to return

        Returns:
            List[MarkdownCacheItem]: Ranked search results with file path, snippet, and score
        """
        if not self.documents or self.doc_vectors is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_vectors).flatten()
        ranked_indices = np.argsort(similarities)[::-1][:limit]

        results = []
        for idx in ranked_indices:
            if similarities[idx] > 0:
                results.append(MarkdownCacheItem(
                    file=self.metadata[idx],
                    content=self.documents[idx],
                    score=float(similarities[idx])
                ))

        print(f"[INFO] Found {len(results)} results for query '{query}'")
        return results
    

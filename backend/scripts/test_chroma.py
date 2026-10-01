"""
Verify ChromaDB car documents (Step 5).

Connects to backend/chroma_db/, prints collection count,
and shows 1–2 stored documents (id, document, metadata).

Does NOT perform semantic search.

Run from the backend folder (venv activated):

  python scripts/test_chroma.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.vector_store import (  # noqa: E402
    COLLECTION_NAME,
    get_car_collection,
    get_document_count,
    get_documents_by_ids,
)


def main() -> None:
    collection = get_car_collection()
    count = get_document_count()

    print("=" * 60)
    print("ChromaDB verification")
    print("=" * 60)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Document count: {count}")
    print()

    if count == 0:
        print("No documents found.")
        print("Run: python scripts/ingest_cars.py")
        return

    # Peek at a few IDs already in the collection
    peek = collection.peek(limit=min(2, count))
    sample_ids = peek.get("ids") or []

    if not sample_ids:
        print("Collection reports documents but peek() returned no IDs.")
        return

    data = get_documents_by_ids(sample_ids)
    ids = data.get("ids") or []
    documents = data.get("documents") or []
    metadatas = data.get("metadatas") or []

    for index, doc_id in enumerate(ids):
        print("-" * 60)
        print(f"ID: {doc_id}")
        print()
        print("Document:")
        print(documents[index] if index < len(documents) else "(missing)")
        print()
        print("Metadata:")
        print(metadatas[index] if index < len(metadatas) else "(missing)")
        print()

    print("Done.")


if __name__ == "__main__":
    main()

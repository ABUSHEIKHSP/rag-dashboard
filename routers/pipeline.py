from fastapi import APIRouter
from typing import Literal
from pathlib import Path

from services.chunk_services import (
    load_document,
    join_pages,
    chunk_documents,
    save_chunks
)

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CHUNK_DIR = Path("chunks")
CHUNK_DIR.mkdir(exist_ok=True)


@router.get("/pipeline/chunk", tags=["chunking pipeline"])
async def chunk_pdf(
    document: str,
    pages_to_join: int = 1,
    chunk_size: int = 100,
    chunk_overlap: int = 0,
    text_splitter: Literal[
        "RecursiveCharacterTextSplitter",
        "TokenTextSplitter"
    ] = "RecursiveCharacterTextSplitter"
):
    file_location = UPLOAD_DIR / document
    documents = load_document(file_location)
    print("Original pages:", len(documents))

    pages_to_join = 1 if pages_to_join < 1 else pages_to_join
    documents = join_pages(documents, pages_to_join)
    print("Grouped documents:", len(documents))

    for i, doc in enumerate(documents):
        print(f"Document {i}: {len(doc.page_content)} characters")

    texts = chunk_documents(
        documents,
        chunk_size,
        chunk_overlap,
        text_splitter
    )

    output_file = CHUNK_DIR / f"{Path(document).stem}_chunks.json" # stem extracts the filename without its extension.
    save_chunks(texts, output_file)

    return {
        "total_chunks": len(texts),
        "saved_to": str(output_file)
    }
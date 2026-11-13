from fastapi import APIRouter
from pathlib import Path
from typing import Literal

from services.chunk_services import (
    load_document,
    join_pages,
    chunk_documents
)

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/playground/list_textsplitters", tags=["chunking playground"])
async def list_textsplitters():
    return {
        "available_textsplitter": [
            "RecursiveCharacterTextSplitter",
            "TokenTextSplitter",
        ]
    }


@router.get("/playground/chunk", tags=["chunking playground"])
async def chunk_pdf(
    document: str,
    pages_to_join: int = 1,
    chunk_size: int = 100,
    chunk_overlap: int = 0,
    text_splitter: Literal[
        "RecursiveCharacterTextSplitter",
        "TokenTextSplitter"
    ] = "RecursiveCharacterTextSplitter",
    preview: int = 5
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

    return {
        "chunks": texts[:preview]
    }
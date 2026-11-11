from fastapi import APIRouter
from pathlib import Path
from typing import Literal

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CHUNK_DIR = Path("chunks")
CHUNK_DIR.mkdir(exist_ok=True)

@router.get("/playground/list_textsplitters", tags=["chunking playground"])
async def list_textsplitters():
    return {
        "available_textsplitter": [
            "RecursiveCharacterTextSplitter",
            "TokenTextSplitter",
        ]
    }

@router.get("/playground/chunk", tags=["chunking playground"])
async def chunk_pdf(document: str, 
                    chunk_size: int = 100, 
                    chunk_overlap: int = 0,
                    text_splitter: Literal[
                    "RecursiveCharacterTextSplitter",
                    "TokenTextSplitter"] = "RecursiveCharacterTextSplitter",
                    preview: int = 5):

    SPLITTERS = {
        "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        "TokenTextSplitter": RecursiveCharacterTextSplitter.from_tiktoken_encoder,
    }

    splitter_class = SPLITTERS[text_splitter]

    text_splitter = splitter_class(chunk_size=chunk_size, 
                                        chunk_overlap=chunk_overlap)

    file_location = UPLOAD_DIR / document
    loader = PyMuPDFLoader(file_path=file_location)
    documents = loader.load() 

    texts = text_splitter.split_documents(documents)

    page_content = [[text.page_content] for text in texts[:preview]]
    print(page_content)
    return {
        "chunks": texts[:preview]
    }
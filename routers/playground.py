from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import os
import json
from typing import Literal

from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings

from starlette.concurrency import run_in_threadpool

from services.chunk_services import classify_page_boundary, clean_page_text, join_pages

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
            "SemanticChunker"
        ]
    }

@router.get("/playground/classify-boundary", tags=["chunking playground"])
async def classify_boundary(document):

    file_location = UPLOAD_DIR / document
    # PyMuPDF loads documents really fast
    loader = PyMuPDFLoader(file_path=file_location)
    documents = loader.load()[:6]

    # results = [await run_in_threadpool(classify_page_boundary, 
    #                                    clean_page_text(documents[i].page_content), 
    #                                    clean_page_text(documents[i+1].page_content)) 
    #            for i in range(len(documents) - 1)]

    results = [
        await run_in_threadpool(
            classify_page_boundary,
            clean_page_text(documents[i].page_content)
        )
        for i in range(len(documents))
    ]

    # result = await run_in_threadpool(
    #     classify_page_boundary,
    #     documents.previous_page,
    #     documents.current_page
    # )

    return {
        "results": results
    }

@router.get("/playground/chunk", tags=["chunking playground"])
async def chunk_pdf(document: str, 
                    chunk_size: int = 100, 
                    chunk_overlap: int = 0,
                    text_splitter: Literal[
                    "RecursiveCharacterTextSplitter",
                    "TokenTextSplitter",
                    "SemanticChunker"
                    ] = "RecursiveCharacterTextSplitter",
                    preview: int = 5):

    SPLITTERS = {
        "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        "TokenTextSplitter": RecursiveCharacterTextSplitter.from_tiktoken_encoder,
        "SemanticChunker": SemanticChunker
    }

    splitter_class = SPLITTERS[text_splitter]

    if text_splitter == "SemanticChunker":  
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        text_splitter = splitter_class(embeddings=embeddings,
                                        breakpoint_threshold_type="percentile",
                                        breakpoint_threshold_amount=95)
    else:
        text_splitter = splitter_class(chunk_size=chunk_size, 
                                        chunk_overlap=chunk_overlap)

    file_location = UPLOAD_DIR / document
    # PyMuPDF loads documents really fast
    loader = PyMuPDFLoader(file_path=file_location)
    documents = loader.load() 

    texts = text_splitter.split_documents(documents)

    page_content = [[text.page_content] for text in texts[:preview]]
    print(page_content)
    return {
        # "chunks": page_content
        "chunks": texts[:preview]
    }
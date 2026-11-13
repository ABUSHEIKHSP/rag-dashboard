import json
from pathlib import Path
from typing import Literal

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader

def load_document(file_location: Path):
    loader = PyMuPDFLoader(file_path=file_location)
    return loader.load()

def chunk_documents(
    documents,
    chunk_size: int = 100,
    chunk_overlap: int = 0,
    text_splitter: Literal[
        "RecursiveCharacterTextSplitter",
        "TokenTextSplitter"
    ] = "RecursiveCharacterTextSplitter"
):
    SPLITTERS = {
        "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        "TokenTextSplitter": RecursiveCharacterTextSplitter.from_tiktoken_encoder,
    }

    splitter_class = SPLITTERS[text_splitter]

    splitter = splitter_class(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    return splitter.split_documents(documents)


def save_chunks(chunks, output_file: Path):
    chunks_data = [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in chunks
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, indent=4, ensure_ascii=False)

    return output_file

def join_pages(documents, pages_to_join: int = 1):

    grouped_documents = []
    table = str.maketrans("", "", "\n\t\r\f\v\\\"")

    for i in range(0, len(documents), pages_to_join):

        # Combining pages
        group = documents[i:i + pages_to_join]

        # Cleaning text
        combined_text = " ".join(doc.page_content.translate(table) for doc in group)

        # Creating metadata
        metadata = group[0].metadata.copy()

        metadata.update({
            "page_start": group[0].metadata["page"],
            "page_end": group[-1].metadata["page"],
            "Pages": [doc.metadata["page"] for doc in group]
        })

        # Appening combined text and metadata
        grouped_documents.append(
            Document(
                page_content=combined_text,
                metadata=metadata
            )
        )

    return grouped_documents
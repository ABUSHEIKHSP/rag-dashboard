
from langchain_core.documents import Document

def join_pages(documents, pages_to_join: int = 1):

    grouped_documents = []

    for i in range(0, len(documents), pages_to_join):

        group = documents[i:i + pages_to_join]
        combined_text = "\n\n".join(doc.page_content for doc in group)
        grouped_documents.append(Document(page_content=combined_text))

    return grouped_documents

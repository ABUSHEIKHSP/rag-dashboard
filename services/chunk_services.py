from langchain_core.documents import Document

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
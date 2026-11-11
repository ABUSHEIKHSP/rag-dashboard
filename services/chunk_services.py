
from typesafe_sdk import Choice, TypeSafeClient
from langchain_core.documents import Document

import ftfy
import unicodedata

def clean_page_text(text: str) -> str:
    # Fix common Unicode encoding issues
    text = ftfy.fix_text(text)

    # Normalize Unicode character representations
    text = unicodedata.normalize("NFKC", text)

    return text.strip()


from typesafe_sdk import Noul, TypeSafeClient

def classify_page_boundary(current_page):

    state = {
        "page_ending": current_page[-500:]
    }

    print("#" * 25)
    print(state)
    print("#" * 25)

    questions = {
        "should_continue": Noul(
            instructions=(
                "Is the text ending incomplete and likely "
                "to continue as part of the same content? "
                "Consider unfinished words, sentences, "
                "paragraphs, and list items. "
                "Answer yes if continuation is expected. "
                "Answer no if the content appears complete."
            )
        )
    }

    with TypeSafeClient(timeout=120) as client:
        result = client.system_one(
            state=state,
            questions=questions
        )

    return {
        "text": state,
        "result": result.nouls["should_continue"]
    }

def classify_page_boundary2(current_page, next_page):

    state = {
        "current_page_ending": current_page[-500:],
        "next_page_beginning": next_page[:500]
    }

    print("#" * 25)
    print(state)
    print("#" * 25)

 
    questions = {
        "boundary": Choice(
            instructions=(
                "Determine whether the content on the next page "
                "continues the same content unit from the current page."
            ),
            criteria={
                "merge": (
                    "The content is interrupted at the page boundary "
                    "and continues on the next page. This includes "
                    "words, sentences, paragraphs, list items, and tables "
                    "that continue across pages."
                ),
                "split": (
                    "The previous content unit is complete, and the "
                    "next page starts independent content. For example, "
                    "a completed sentence followed by a new sentence, "
                    "or a completed bullet followed by another bullet."
                ),
                "uncertain": (
                    "The available text does not provide enough evidence "
                    "to determine continuity."
                )
            }
        )
    }


    with TypeSafeClient(timeout=120) as client:
        result = client.system_one(
            state=state,
            questions=questions
        )

    return result


def join_pages(documents, pages_to_join: int = 1):

    grouped_documents = []

    for i in range(0, len(documents), pages_to_join):

        group = documents[i:i + pages_to_join]
        combined_text = "\n\n".join(doc.page_content for doc in group)
        grouped_documents.append(Document(page_content=combined_text))

    return grouped_documents

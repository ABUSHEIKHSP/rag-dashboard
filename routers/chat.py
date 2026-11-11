
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langchain_ollama import ChatOllama

router = APIRouter()

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0
)

@router.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversations = []

    try:
        while True:
            # Recieve msg from client
            user_input = await websocket.receive_text()

            if conversations:
                messages = [
                    (
                        "system",
                        "Use the previous conversation for context. "
                        "Extract information from the latest user input "
                        "and produce JSON as output."
                    )
                ]

            messages = [
                (
                    "system",
                    "Extract information from the latest user input "
                    "and produce JSON as output."
                )
            ]            

            messages.extend(conversations)
            print(messages)
            messages.append(("human", user_input))

            # Invoke LLM
            response = await llm.ainvoke(messages)

            # Send response to client
            await websocket.send_text(response.content)

            # Update conversations
            conversations.append(("human", user_input))
            conversations.append(("ai", response.content))

    except WebSocketDisconnect:
        print("Client disconnected!")
        
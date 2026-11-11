from fastapi import FastAPI
from routers import chat, documents, playground, test

app = FastAPI()

app.include_router(chat.router)
app.include_router(test.router)
app.include_router(documents.router)
app.include_router(playground.router)
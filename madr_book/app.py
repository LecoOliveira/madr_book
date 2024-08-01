from fastapi import FastAPI

from madr_book.routers import contas, token

app = FastAPI()

app.include_router(contas.router)
app.include_router(token.router)
# app.include_router(livros.router)
# app.include_router(romancistas.router)

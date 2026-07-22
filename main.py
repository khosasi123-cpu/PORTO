from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.database import Base, engine
from database.model.document import Document
from database.model.document_image import DocumentImage

from routes.document import router as retriveal_router
from routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(retriveal_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}
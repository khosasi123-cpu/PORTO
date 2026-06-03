from fastapi import FastAPI
from routes.retrieval import router as retriveal_router
from routes.chat import router as chat_router


app = FastAPI()

app.include_router(retriveal_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status" : "ok"}


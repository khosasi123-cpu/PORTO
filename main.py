from fastapi import FastAPI
from routes.retrieval import router as retriveal_router

app = FastAPI()
app.include_router(retriveal_router)



@app.get("/health")
def health():
    return {"status" : "ok"}


from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv(override=True)
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
RERANKER_MODEL = os.getenv("RERANKER_MODEL")
LIMIT = int(os.getenv("LIMIT"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K"))

reranker = CrossEncoder(RERANKER_MODEL, device="cuda")
embedding = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
client = QdrantClient(port=QDRANT_PORT, location=QDRANT_HOST)

collection = COLLECTION_NAME
limit = LIMIT


def retrieval(question : str) -> list[dict]:
    """
    search relevant document from qdrant
    
    Args:
        question : User question

    Returns:
        list[dict]: list of retrivead chunks
    """
    vector = embedding.encode(question, normalize_embeddings=True)
    result = client.query_points(collection_name=COLLECTION_NAME, 
                                 query= vector.tolist(),
                                 with_payload=True,
                                 limit=limit)
    points = result.points
    pairs = [[question, point.payload["text"]] for point in points]
    scores = reranker.predict(pairs)
    scored_docs = list(zip(points, scores))
    ranked_docs = sorted(
        scored_docs,
        key=lambda x : x[1],
        reverse=True
    )
    return ranked_docs[:RERANK_TOP_K]

if __name__ =="__main__" :
    result = retrieval("What should I do during a security incident?")
    print(result)
    
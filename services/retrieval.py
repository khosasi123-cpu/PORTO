from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", device="cuda")
embedding = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
client = QdrantClient(port=6333, location="localhost")

collection = "knowledge-base"
limit = 15


def retrieval(question : str) -> list[dict]:
    """
    search relevant document from qdrant
    
    Args:
        question : User question

    Returns:
        list[dict]: list of retrivead chunks
    """
    vector = embedding.encode(question, normalize_embeddings=True)
    result = client.query_points(collection_name=collection, 
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
    return ranked_docs[:3]

if __name__ =="__main__" :
    result = retrieval("What should I do during a security incident?")
    print(result)
    
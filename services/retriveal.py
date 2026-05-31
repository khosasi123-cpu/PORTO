from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

embedding = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
client = QdrantClient(port=6333, location="localhost")

collection = "knowledge-base"
limit = 5


def retriveal(question : str) -> list[dict]:
    """
    search relevant document from qdrant
    
    Args:
        question : User question

    Returns:
        list[dict]: list of retrivead chunks
    """
    vector = embedding.encode(question, normalize_embeddings=True)
    results = client.query_points(collection_name=collection, 
                                 query= vector.tolist(),
                                 with_payload=True)
    return results.points

if __name__ =="__main__" :
    result = retriveal("how many leave days do employees receive")
    print(type(result[0]))
    
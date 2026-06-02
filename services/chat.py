from openai import OpenAI
from retrieval import retrieval
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI = OpenAI()

SYSTEM_PROMPT = """
You are KnowledgeOps AI, an internal knowledge assistant for company policies, procedures, and documentation.

Your task is to answer questions using ONLY the provided context.

Rules:

Use the retrieved context as the primary source of truth.
Do not invent information that is not present in the context.
If the answer cannot be found in the context, clearly state:
"I could not find enough information in the knowledge base to answer that question."
Be concise but complete.
When possible, cite the document name used to answer the question.
If multiple documents provide relevant information, combine them into a single coherent answer.
Do not mention vector databases, embeddings, retrieval systems, or internal implementation details.
Preserve important numbers, dates, policies, limits, and requirements exactly as written in the context.
If the context contains conflicting information, mention the conflict and identify the relevant documents.
"""

def build_context(results):

    contexts = []

    for point, score in results:

        contexts.append(
            f"""
Source: {point.payload["document_name"]}
Chunk: {point.payload["chunk_id"]}

{point.payload["text"]}
"""
        )

    return "\n\n---\n\n".join(contexts)

def chat(question : str):
    results = retrieval(question)
    context = build_context(results) + f"\n\n this is user question : {question}"
    response = OPENAI.chat.completions.create(model="gpt-5.4-nano", messages=[{"role" : "system", "content" : SYSTEM_PROMPT},
                                                                              {"role" : "user", "content" : context}])
    return response.choices[0].message.content



if __name__ == "__main__":
    print(chat("What should I do during a security incident?"))
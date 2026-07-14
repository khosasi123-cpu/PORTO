from openai import OpenAI
import os
from services.retrieval import retrieval
from services.history import get_history, save_message
from services.router import router
from schemas.chat import ChatRequest
from time import perf_counter
from dotenv import load_dotenv

load_dotenv(override=True)
MODEL = os.getenv("MODEL")
base_url = os.getenv("LLM_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")

OPENAI = OpenAI(base_url=base_url, api_key=api_key)

RAG_SYSTEM_PROMPT = """
You are a retrieval-grounded knowledge base assistant.

Answer the user's question using only the provided context.

Rules:
- Use only information supported by the context.
- Do not use external knowledge, assumptions, or invented information.
- Answer the question directly.
- Include all relevant information supported by the context and avoid unrelated details.
- You may summarize, combine, and clearly rephrase information from multiple context passages.
- Use steps or bullet points when they improve clarity.
- If the context supports only part of the question, answer the supported part and clearly state what could not be determined.
- If the context contains no sufficient information to answer the question, respond:
  "I could not find sufficient information in the knowledge base to answer that question."
- Do not reproduce large portions of the context unnecessarily.

Prioritize factual grounding while providing the most complete answer supported by the available context.
"""


SYSTEM_PROMPT = """
You are a conversational assistant for an internal knowledge assistant.

Use the user's message and conversation history to handle requests that do not require retrieving additional internal documentation.

You may:
- translate, summarize, rewrite, or format provided content
- clarify or simplify previous responses
- explain concepts or technical terms related to the current conversation
- continue the conversation using the available context

Rules:
- Preserve the meaning and technical terminology of provided content.
- You may use general knowledge to explain concepts, but do not present general knowledge as facts about the internal knowledge base, documents, systems, policies, or procedures.
- Do not invent missing details about internal documentation or previously discussed systems.
- If the user asks for a new internal fact that is not available in the conversation, state that the available conversation does not provide that information.
- Be concise unless the user requests more detail.
- Maintain the user's preferred language.
- For translation requests, return the translation directly unless additional explanation is requested.
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

def chat(user_request):
    total_started = perf_counter()
    #1. History
    history_started = perf_counter()
    history = get_history(user_request.session_id)
    history_seconds = perf_counter() - history_started

    #2. Router
    router_started = perf_counter()
    router_result = router(user_request.question, history)
    router_seconds = perf_counter() - router_started
    print({
    "question": user_request.question[:100],
    "use_rag": router_result.use_rag,
    "rewritten_query": router_result.rewritten_query[:100] if router_result.rewritten_query else None
})

    messages = []
    answear = ""
    results = []
    if router_result.use_rag:
        # for RAG, we use the rewritten query if available, otherwise we use the original question.
        query = router_result.rewritten_query or user_request.question
        # 3. Retrieval
        retrieval_started = perf_counter()
        docs = retrieval(query)
        retrieval_seconds = perf_counter() - retrieval_started
        # Build context from retrieved documents and append the user question.
        context = build_context(docs) + f"\n\n this is user question : {user_request.question}"
        messages = [{"role" : "system", "content" : RAG_SYSTEM_PROMPT}] + history + [{"role" : "user", "content" : context}]
        results += list({point.payload["document_name"] for point, score in docs})
    else:
        messages = [{"role" : "system", "content" : SYSTEM_PROMPT}] + history + [{"role" : "user", "content" : user_request.question}]
    
    # 4. LLM
    llm_started = perf_counter()
    response = OPENAI.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=2048,
        temperature=0,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}}
    )
    llm_seconds = perf_counter() - llm_started
    answear = response.choices[0].message.content or ""
    generated_seconds = perf_counter() - total_started
    print({ 
        "history_seconds": round(history_seconds, 2),
        "router_seconds": round(router_seconds, 2),
        "retrieval_seconds": round(retrieval_seconds, 2) if router_result.use_rag else 0,
        "llm_seconds": round(llm_seconds, 2),
        "generated_seconds": round(generated_seconds, 2)
    })
    save_message(user_request.session_id, "user", user_request.question)
    save_message(user_request.session_id, "assistant", answear)
    return {"answear" : answear,
            "source" : results
            }



if __name__ == "__main__":
    chat_req = ChatRequest(session_id="1234", question="Apa target response time P1?")
    print(chat(chat_req))
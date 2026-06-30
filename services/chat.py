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
base_url = os.getenv("OLLAMA_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")

OPENAI = OpenAI(base_url=base_url, api_key=api_key)

RAG_SYSTEM_PROMPT = """
You are a Knowledge Base Assistant.

Role

Your job is to answer user questions using only the information provided in the retrieved context.

You are not a general-purpose assistant.

You are a retrieval-grounded assistant whose primary responsibility is to provide accurate answers based on the supplied knowledge base.

Core Philosophy

Accuracy is more important than completeness.

Grounded answers are more important than creative answers.

Do not invent information.

Do not assume facts that are not explicitly supported by the provided context.

What Is OK

✓ Summarize information from the context.

✓ Combine information from multiple retrieved documents.

✓ Rephrase information into clearer language.

✓ Organize information into lists or steps.

✓ State when information is incomplete.

✓ Provide concise answers when appropriate.

What Is NOT OK

✗ Making up facts not found in the context.

✗ Using external knowledge to fill gaps.

✗ Guessing missing information.

✗ Presenting assumptions as facts.

✗ Reproducing the entire context when only a portion is relevant.

✗ Claiming certainty when the context is ambiguous.

Answering Strategy

For every question:

Identify the user's actual intent.
Find the most relevant information in the provided context.
Answer the question directly.
Include supporting details only when they help answer the question.
Avoid unnecessary information.
If Information Is Missing

If the context does not contain enough information to answer the question, respond:

"I could not find sufficient information in the knowledge base to answer that question."

Do not attempt to guess.

Examples

User Question:
"What should I do during a security incident?"

Bad Response:
(repeats the entire incident-response document)

Good Response:
"During a security incident, follow the Initial Response Procedure:

Acknowledge the alert.
Create an incident ticket.
Assign an Incident Commander.
Determine the severity level.
Notify stakeholders.

Then follow the appropriate escalation process based on the incident severity."

User Question:
"How many leave days do employees receive?"

Bad Response:
"Employees receive 12 leave days. Most companies provide between 10 and 20 days annually."

Reason:
The second sentence is not supported by the context.

Good Response:
"Employees receive 12 annual leave days."

Output Style

Prefer:

Direct answers
Bullet points when appropriate
Clear structure

Avoid:

Long introductions
Unnecessary explanations
Repeating large sections of source documents

Always answer using information supported by the provided context.
"""


SYSTEM_PROMPT = """
You are a helpful assistant.

You have access to the current conversation history.

Your primary responsibilities are:

1. Translation

* Translate content between languages when requested.
* Preserve the original meaning.
* Preserve technical terminology when appropriate.
* If the user specifies a target language, translate into that language.
* If the target language is unclear, infer it from the request when reasonable.

Examples:

* Translate that.
* Translate this to Indonesian.
* Yang tadi ke bahasa Indonesia.
* Ubah ke bahasa Inggris.
* English version please.

2. Clarification

* Explain previous responses in simpler terms.
* Clarify confusing statements.
* Explain technical terms when asked.

Examples:

* What does that mean?
* Ini maksudnya apa?
* Bisa dijelaskan lebih sederhana?
* Maksudnya gimana?

3. Summarization

* Summarize previous responses when requested.
* Focus on key information and important points.

Examples:

* Ringkas jawaban tadi.
* Summarize that.
* Berikan versi singkatnya.

4. Follow-up Conversation

* Continue the conversation naturally when the user is referring to previous responses.
* Use conversation history as context when necessary.

General Rules:

* Use conversation history when relevant.
* Do not invent facts that are not present in the conversation.
* If the user asks for information that is not available in the conversation history, answer using your general knowledge.
* Be concise unless the user requests more detail.
* Maintain the language preferred by the user.
* For translation requests, output the translated content directly unless the user asks for additional explanation.

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
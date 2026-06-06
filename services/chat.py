from openai import OpenAI
from services.retrieval import retrieval
from services.history import get_history, save_message
from services.router import router
from schemas.chat import ChatRequest
from dotenv import load_dotenv

load_dotenv(override=True)

# OPENAI = OpenAI()
# MODEL = "gpt-5.4-nano"

MODEL = "frob/qwen3.5-instruct"
OPENAI = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

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
    history = get_history(user_request.session_id)
    router_result = router(user_request.question, history)
    print({
    "question": user_request.question,
    "use_rag": router_result.use_rag,
    "rewritten_query": router_result.rewritten_query
})
    answear = ""
    results = []
    if router_result.use_rag:
        docs = retrieval(router_result.rewritten_query)
        context = build_context(docs) + f"\n\n this is user question : {user_request.question}"
        messages = [{"role" : "system", "content" : RAG_SYSTEM_PROMPT}] + history + [{"role" : "user", "content" : context}]
        response = OPENAI.chat.completions.create(model=MODEL, messages=messages)
        answear += response.choices[0].message.content
        results += list({point.payload["document_name"] for point, score in docs})
    else:
        messages = [{"role" : "system", "content" : SYSTEM_PROMPT}] + history + [{"role" : "user", "content" : user_request.question}]
        response = OPENAI.chat.completions.create(model=MODEL, messages=messages)
        answear += response.choices[0].message.content
    save_message(user_request.session_id, "user", user_request.question)
    save_message(user_request.session_id, "assistant", answear)
    print(history)
    return {"answear" : answear,
            "source" : results
            }



if __name__ == "__main__":
    chat_req = ChatRequest(session_id="1234", question="Apa target response time P1?")
    print(chat(chat_req))
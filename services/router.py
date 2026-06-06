from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal


load_dotenv(override=True)
OPENAI= OpenAI()
MODEL = "gpt-5.4-nano"

class RouterResponse(BaseModel):
    use_rag: bool
    rewritten_query: str | None = None
    

router_prompt = """
You are a routing and query rewriting system for a Knowledge Assistant.

Your job is to determine whether the user's latest message requires retrieving information from the knowledge base.

If retrieval is required:

- Set use_rag to true.
- Rewrite the user's request into a complete standalone search query.
- Include relevant context from conversation history when needed.
- Resolve references such as:
  - it
  - this
  - that
  - tadi
  - ini
  - itu
- The rewritten query should be suitable for semantic search and retrieval.

If retrieval is NOT required:

- Set use_rag to false.
- Set rewritten_query to null.

Examples of messages that usually do NOT require retrieval:

- Translate that.
- Yang tadi ke bahasa Indonesia.
- Translate this text.
- Ini maksudnya apa?
- Jelaskan kalimat terakhir.
- Bisa dijelaskan lebih sederhana?
- Tolong ubah ke bahasa Inggris.

These requests can usually be answered using conversation history alone.

Examples of messages that usually DO require retrieval:

- Apa itu annual leave?
- Berapa hari maternity leave?
- Siapa yang menyetujui refund di atas $1000?
- Apa target response time untuk P1?
- Bagaimana prosedur refund?

Examples requiring retrieval and history resolution:

History:
Assistant: Maternity leave is 90 calendar days.

User:
Kalau adopsi?

Output:

{{
  "use_rag": true,
  "rewritten_query": "How many days of adoption leave are employees entitled to?"
}}

---

History:
Assistant: Severity 1 incidents require a response within 15 minutes.

User:
Kalau P2?

Output:

{{
  "use_rag": true,
  "rewritten_query": "What is the target response time for Severity 2 incidents?"
}}

---

History:
Assistant: Full-time employees are entitled to 18 days of annual leave.

User:
Kalau part time gimana?

Output:

{{
  "use_rag": true,
  "rewritten_query": "How is annual leave calculated for part-time employees?"
}}

Rules:

- Return valid JSON only.
- Do not explain your reasoning.
- Do not return markdown.
- Do not return extra text.
- If use_rag is false, rewritten_query must be null.
- If use_rag is true, rewritten_query must be a complete standalone query.

Conversation History:
{history}

Latest User Message:
{question}
"""



def router(question, history):
    history = history + [{"role" : "user", "content" : question}]
    messages = [{"role" : "system", "content" : router_prompt.format(history=history, question=question)}]
    response = OPENAI.responses.parse(
    model="gpt-4.1-mini",
    input=messages,
    text_format=RouterResponse
)
    return response.output_parsed

if __name__ == "__main__" :
    history = []
    question = "Berapa hari annual leave untuk karyawan full-time?"
    route_result = router(question, history)
    print(route_result.task_type)

import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal


load_dotenv(override=True)
# OPENAI= OpenAI()
# MODEL = "gpt-5.4-nano"
base_url = os.getenv("OLLAMA_BASE_URL")

OPENAI = OpenAI(base_url=base_url, api_key="ollama")
MODEL = "frob/qwen3.5-instruct"

class RouterResponse(BaseModel):
    use_rag: bool
    rewritten_query: str | None = None
    

router_prompt = """
You are a routing and query rewriting assistant for a HUMS troubleshooting chatbot.
HUMS is an application that monitors system health and provides troubleshooting guidance for the aircraft.

Your responsibilities:

1. Decide whether the user's latest message requires retrieval from HUMS troubleshooting documents.
2. If retrieval is needed:
   - set use_rag = true
   - rewrite the user's query into a concise retrieval-friendly query
3. If retrieval is NOT needed:
   - set use_rag = false
   - keep the query as the original user message

Use RAG when:
- the user asks troubleshooting questions
- the user asks procedural or step-by-step questions
- the user refers to HUMS issues, errors, system behavior, logs, files, services, configuration
- the user asks follow-up questions that depend on prior troubleshooting context

Do NOT use RAG when:
- the user is greeting
- casual conversation
- thanks / acknowledgements
- general knowledge unrelated to HUMS
- open-ended discussion not requiring troubleshooting documents

Rewrite rules:
- preserve original technical terms exactly
- preserve product names, acronyms, filenames, error messages, commands
- use conversation history only when needed to resolve ambiguity
- do not invent missing technical details
- do not answer the question
- keep rewritten_query concise and retrieval-friendly

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
- if uncertain, prefer use_rag = true
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
    messages = [{"role" : "system", "content" : router_prompt.format(history=history, question=question)}, {"role" : "user", "content" : question}]
    response = OPENAI.responses.parse(
    model=MODEL,
    input=messages,
    text_format=RouterResponse
)
    return response.output_parsed

if __name__ == "__main__" :
    history = []
    question = "cara buat resend FSC di HUMS?"
    route_result = router(question, history)
    print(route_result)

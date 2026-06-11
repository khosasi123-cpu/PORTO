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
You are a routing assistant for a HUMS knowledge assistant.

Return JSON only:

{{
  "use_rag": boolean,
  "rewritten_query": string | null
}}

Use RAG when:
- troubleshooting questions
- HUMS procedures
- HUMS features
- HUMS errors
- HUMS logs
- HUMS configuration
- HUMS maintenance tasks
- follow-up questions about previously retrieved HUMS information
- questions that require information from documentation

Do NOT use RAG when:
- greetings
- small talk
- thanks
- translation
- summarization
- rewriting
- markdown conversion
- formatting
- grammar correction
- content generation
- tasks that only use user-provided text or conversation history

Rules:
- If use_rag is true, rewrite the question into a standalone retrieval query.
- Preserve technical terms exactly.
- Do not answer the question.
- If use_rag is false, rewritten_query must be null.
- Return JSON only.

Examples:

User: How to resend FSC in HUMS?
Output:
{{
  "use_rag": true,
  "rewritten_query": "How to resend FSC in HUMS?"
}}

User: Translate this to Bahasa Indonesia.
Output:
{{
  "use_rag": false,
  "rewritten_query": null
}}

User: Convert this document to markdown.
Output:
{{
  "use_rag": false,
  "rewritten_query": null
}}

History:
{history}

User:
{question}
"""




def router(question, history):
    messages = [{"role" : "system", "content" : router_prompt.format(history=history, question=question)}, {"role" : "user", "content" : question}]
    response = OPENAI.responses.parse(
    model=MODEL,
    input=messages,
    text_format=RouterResponse,
    temperature=0
)
    return response.output_parsed

if __name__ == "__main__" :
    history = []
    question = "cara buat resend FSC di HUMS?"
    route_result = router(question, history)
    print(route_result)

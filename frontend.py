import uuid
import requests
import gradio as gr

API_URL = "http://localhost:8000/chat/"

# satu session per browser
SESSION_ID = str(uuid.uuid4())


def chat(message, history):

    response = requests.post(
        API_URL,
        json={
            "session_id": SESSION_ID,
            "question": message
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    answer = data["answear"]

    sources = data.get("source", [])

    if sources:
        source_links = "\n".join( f"- [{doc}](http://localhost:8000/retrieve/documents/{doc})" for doc in sources )
        answer += f"\n\n### Sources\n{source_links}"

    return answer


demo = gr.ChatInterface(
    fn=chat,
    title="KnowledgeOps AI",
    description="Internal Knowledge Assistant"
)

demo.launch(inbrowser=True)
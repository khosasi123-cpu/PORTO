chat_history = {}

def get_history(session_id : str):
    return chat_history.get(session_id,[])

def save_message(
    session_id: str,
    role: str,
    content: str
):

    if session_id not in chat_history:
        chat_history[session_id] = []

    chat_history[session_id].append(
        {
            "role": role,
            "content": content
        }
    )

    chat_history[session_id] = (
        chat_history[session_id][-10:]
    )

if __name__ == "__main__":
    print(chat_history)
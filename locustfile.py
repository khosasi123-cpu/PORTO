import uuid

from locust import HttpUser, between, task
question = """Manage striped icon
  This icon appears when several phases have been recorded on the MDC (even if only one flight has been performed) and HUMS is not able to assign data to the proper phase (MFR / engine files).
Most of the time it’s due to a recording issue on the MDC. An alternative solution might be to edit the flight data manually to “clean” them and then read them to get rid of the striped icon.
tolong buat ke dalam bahasa indonesia"""

# question = "how to create backup flight at HUMS"



class KnowledgeOpsUser(HttpUser):
    # URL FastAPI yang sedang berjalan dari Docker.
    host = "http://127.0.0.1:8000"

    # Jeda setelah request selesai, sebelum virtual user mengirim request berikutnya.
    # Ini mensimulasikan user membaca jawaban, bukan spam request terus-menerus.
    wait_time = between(2, 5)

    @task
    def ask_rag_question(self):
        # Session baru per request agar conversation history tidak bertambah
        # dan hasil benchmark fokus pada performa RAG end-to-end.
        payload = {
            "session_id": str(uuid.uuid4()),
            "question": (
                question
            ),
        }

        with self.client.post(
            "/chat/",
            json=payload,
            name="POST /chat/ RAG",
            timeout=120,
            catch_response=True,
        ) as response:
            # HTTP error, misalnya 500 atau 503.
            if response.status_code != 200:
                response.failure(
                    f"HTTP {response.status_code}: {response.text[:300]}"
                )
                return

            # Pastikan FastAPI mengembalikan JSON.
            try:
                data = response.json()
            except ValueError:
                response.failure("Response is not valid JSON")
                return

            # Field API saat ini memang bernama `answear`.
            # Jangan ubah nama field API sekarang hanya untuk Locust.
            if not data.get("answear"):
                response.failure("Empty answer")
            else:
                response.success()
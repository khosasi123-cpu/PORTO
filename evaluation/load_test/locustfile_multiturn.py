import uuid

from locust import HttpUser, between, task


class ConversationUser(HttpUser):
    host = "http://127.0.0.1:8000"

    # Simulasikan user membaca jawaban sebelum bertanya lagi
    wait_time = between(5, 15)

    def on_start(self):
        # Satu session untuk satu percakapan
        self.session_id = str(uuid.uuid4())

        self.questions = [
            "What is HUMS Server Recovery Procedure?",
            "When should it be used?",
            "Explain step 3.",
            "Can you summarize the procedure?",
            "Translate it to Indonesian."
        ]

        self.index = 0

    @task
    def chat(self):

        # Percakapan selesai
        if self.index >= len(self.questions):
            self.stop()
            return

        payload = {
            "session_id": self.session_id,
            "question": self.questions[self.index],
        }

        with self.client.post(
            "/chat/",
            json=payload,
            name="POST /chat/ Multi Turn",
            timeout=120,
            catch_response=True,
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"HTTP {response.status_code}: {response.text[:300]}"
                )
                return

            try:
                data = response.json()
            except ValueError:
                response.failure("Response is not valid JSON")
                return

            if not data.get("answear"):
                response.failure("Empty answer")
                return

            # Berhasil
            response.success()

        # Pindah ke pertanyaan berikutnya
        self.index += 1
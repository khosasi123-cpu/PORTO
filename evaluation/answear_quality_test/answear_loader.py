import json
from pathlib import Path
from pydantic import BaseModel, Field

TEST_FILE = str(Path(__file__).parent / "output.jsonl")


class TestQuestion(BaseModel):
    """A test question with expected keywords and reference answer."""

    question: str = Field(description="The question to ask the RAG system")
    keywords: list[str] = Field(description="Keywords that must appear in retrieved context")
    reference_answer: str = Field(description="The reference answer for this question")
    category: str = Field(description="Question category (e.g., direct_fact, spanning, temporal)")


def load_tests() -> list[TestQuestion]: # seoerti di fastapi sebaagi responese_model memastikan return dari fungsi itu seperti Testquestion
    """Load test questions from JSONL file."""
    tests = []
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line.strip()) # .strip untuk hilangkan \n
            tests.append(TestQuestion(**data)) # seperti di fastapi jika data memiliki key yang sama otomatis masukan ke atribut kelas
    return tests


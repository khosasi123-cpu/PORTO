from services.router import router
from collections import Counter
from pathlib import Path
import json

TEST_FILE = str(Path(__file__).parent / "router_testset.jsonl")

def load_tests(): 
    """Load test questions from JSONL file."""
    tests = []
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line.strip()) 
            tests.append(data) 
    return tests

def evaluate_router(router_fn, testset):
    results = []

    for sample in testset:

        prediction = router_fn(
            question=sample["question"],
            history=sample["history"]
        )

        results.append({
            "question": sample["question"],
            "expected": sample["expected_use_rag"],
            "predicted": prediction.use_rag,
            "correct": prediction.use_rag == sample["expected_use_rag"]
        })

    accuracy = (
        sum(r["correct"] for r in results)
        / len(results)
    )

    return {
        "accuracy": accuracy,
        "details": results
    }

if __name__ =="__main__":
    print(evaluate_router(router, load_tests()))
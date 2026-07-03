from services.router import router
from collections import Counter
from pathlib import Path
import json
from time import perf_counter

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
    tp = tn = fp = fn = 0

    for sample in testset:
    
        start_time = perf_counter()
        prediction = router_fn(
            question=sample["question"],
            history=sample["history"]
        )
        end_time = perf_counter()
        expected = sample["expected_use_rag"]
        predicted = prediction.use_rag

        if expected and predicted:
            tp += 1
        elif not expected and not predicted:
            tn += 1
        elif not expected and predicted:
            fp += 1
        else:
            fn += 1

        results.append({
            "question": sample["question"],
            "expected": sample["expected_use_rag"],
            "predicted": prediction.use_rag,
            "correct": prediction.use_rag == sample["expected_use_rag"],
            "latency": end_time - start_time
        })

    accuracy = (
        sum(r["correct"] for r in results)
        / len(results)
    )
    latency = sum(r["latency"] for r in results) / len(results)

    return {
        "accuracy": accuracy,
        "details": results,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "latency": latency
    }

if __name__ =="__main__":
    print(evaluate_router(router, load_tests()))
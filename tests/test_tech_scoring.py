import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.tech_scoring_engine import TechScoringEngine


def run_test(label, answer, required, bonus, tier, domain):
    engine = TechScoringEngine()
    result = engine.evaluate_answer(
        question_id="q_test",
        answer=answer,
        required_concepts=required,
        bonus_concepts=bonus,
        difficulty_tier=tier,
        domain=domain,
    )
    print(f"\n--- {label} ---")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    required = ["heap dump", "garbage collection", "memory profiling"]
    bonus = ["thread contention", "connection pool tuning", "JVM flags"]

    # Case 1: Shallow answer – no concepts, very short
    shallow = "I would restart the server and check the logs."
    r1 = run_test("Shallow Answer", shallow, required, bonus, tier=2, domain="java_backend")

    # Case 2: Deep answer – hits required + bonus, structured reasoning
    deep = (
        "First, I would capture a heap dump using jmap to inspect live objects and identify "
        "what is consuming memory. Then I would analyze garbage collection logs with GCViewer "
        "to check if GC pauses are too long. If the issue persists, I would run memory profiling "
        "with JProfiler or VisualVM. I would also check for thread contention since blocked threads "
        "can inflate heap usage. Finally, I would tune connection pool sizes in the database config "
        "because excessive open connections can cause OutOfMemory errors at scale in production."
    )
    r2 = run_test("Deep Answer", deep, required, bonus, tier=2, domain="java_backend")

    # Assertions
    assert r2["scores"]["depth"] > r1["scores"]["depth"], "Deep answer should score higher on depth"
    assert r2["scores"]["accuracy"] > r1["scores"]["accuracy"], "Deep answer should score higher on accuracy"
    assert r2["scores"]["logic"] > r1["scores"]["logic"], "Deep answer should score higher on logic"
    print("\nAll assertions passed.")

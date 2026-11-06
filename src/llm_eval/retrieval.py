"""Ranking quality metrics for a labeled retrieval benchmark.

Each query supplies an ordered list of retrieved document/chunk identifiers
and a nonempty set of relevant identifiers.
"""
from statistics import mean

def evaluate_retrieval(cases: list[dict], k: int = 5) -> dict:
    if not cases:
        raise ValueError("At least one retrieval case is required")
    if not isinstance(k, int) or not 1 <= k <= 100:
        raise ValueError("k must be between 1 and 100")
    recalls, reciprocal_ranks, precisions = [], [], []
    for case in cases:
        expected = set(case["relevant_ids"])
        if not expected or not all(isinstance(value,str) and value for value in expected):
            raise ValueError("Every query requires relevant IDs")
        ranked = list(case["retrieved_ids"])[:k]
        if any(not isinstance(value,str) or not value for value in ranked):
            raise ValueError("Retrieved IDs must be nonempty strings")
        if len(set(ranked)) != len(ranked):
            raise ValueError("Duplicate IDs in a ranked retrieval result")
        relevant = [index for index,chunk_id in enumerate(ranked,1) if chunk_id in expected]
        recalls.append(len(relevant) / len(expected))
        reciprocal_ranks.append(1 / relevant[0] if relevant else 0.0)
        precisions.append(len(relevant) / k)
    return {
        "queries":len(cases), "k":k,
        "recall_at_k":mean(recalls),
        "mrr_at_k":mean(reciprocal_ranks),
        "precision_at_k":mean(precisions),
    }

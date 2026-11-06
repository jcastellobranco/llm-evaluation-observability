from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable
import json
import re

@dataclass(frozen=True)
class Evaluation:
    case_id: str
    exact_match: bool
    token_f1: float
    latency_ms: float

def token_f1(prediction: str, reference: str) -> float:
    from collections import Counter
    p = Counter(re.findall(r"\w+", prediction.lower()))
    r = Counter(re.findall(r"\w+", reference.lower()))
    if not p and not r:
        return 1.0
    common = sum((p & r).values())
    return 2 * common / (sum(p.values()) + sum(r.values())) if p or r else 0.0

def evaluate(case_id: str, prompt: str, reference: str, predict: Callable[[str], str]) -> Evaluation:
    start = perf_counter()
    output = predict(prompt)
    elapsed = (perf_counter() - start) * 1000
    return Evaluation(case_id, output.strip().casefold() == reference.strip().casefold(), token_f1(output, reference), round(elapsed, 3))

def append_event(path: Path, event: Evaluation) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

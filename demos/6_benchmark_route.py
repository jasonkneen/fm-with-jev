"""Jev classifies the request, then OpenRouter's own benchmark data picks the model.

Jev answers two questions in one call:
  need       which benchmark matters (coding, agentic, website, dataviz, ...)
  difficulty 0-3, which sets a price cap
Code then picks the highest-scoring model on that benchmark under the cap.
No model names are ever shown to Jev or fm.
"""
import json, sys, time, urllib.request
from common import jev

# need -> (benchmark source, key). "aa" = Artificial Analysis index, "da" = Design Arena ELO.
NEEDS = {
    "chat":      (("aa", "intelligence_index"), "small talk, trivia, quick facts, jokes"),
    "reasoning": (("aa", "intelligence_index"), "math, proofs, analysis, planning, hard questions"),
    "coding":    (("aa", "coding_index"),       "writing, fixing or reviewing code"),
    "agentic":   (("aa", "agentic_index"),      "multi-step tasks with tools, browsing, automation"),
    "website":   (("da", "website"),            "build a web page or landing page"),
    "ui":        (("da", "uicomponent"),        "build a UI component"),
    "dataviz":   (("da", "dataviz"),            "charts, graphs, data visualisation"),
    "svg":       (("da", "svg"),                "SVG graphics or icons"),
    "3d":        (("da", "3d"),                 "3D scenes, three.js"),
    "gamedev":   (("da", "gamedev"),            "make a game"),
    "image":     (("da", "image"),              "generate or edit a picture"),
}
DIFFICULTY = ["trivial", "simple", "moderate", "hard"]
# what Jev sees for each level; the words matter (a bare "simple/hard" scale rated a Lean proof "simple")
DIFFICULTY_SCALE = [
    "trivial: greeting, one fact, one-line answer, tiny edit",
    "simple: short routine task any decent model gets right",
    "moderate: multi-step work needing care, but well understood",
    "hard: proofs, formal verification, architecture, unknown-cause debugging, expert-level reasoning",
]
# max $ per 1M output tokens for each difficulty; None = no cap
PRICE_CAP = [1, 5, 20, None]


def load_models():
    d = json.loads(urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30).read())["data"]
    return [m for m in d if ":" not in m["id"] and not m["id"].startswith(("stealth/", "~", "openrouter/", "typesafe/"))]


def score(m, src):
    kind, key = src
    b = m.get("benchmarks") or {}
    if kind == "aa":
        return (b.get("artificial_analysis") or {}).get(key)
    elos = [e["elo"] for e in b.get("design_arena", []) if e.get("category") == key]
    return max(elos) if elos else None


def price(m):
    return float(m["pricing"].get("completion") or 0) * 1e6


def pick(models, need, diff):
    src = NEEDS[need][0]
    wants_image = need == "image"
    cands = []
    for m in models:
        if wants_image != ("image" in m["architecture"]["output_modalities"]):
            continue
        s = score(m, src)
        if s is None or price(m) < 0:
            continue
        cands.append((s, -price(m), m))
    cap = PRICE_CAP[diff]
    under = [c for c in cands if cap is None or -c[1] <= cap]
    pool = under or cands  # nothing under the cap: take best overall
    if not pool:
        return None, None, None
    s, _, m = max(pool, key=lambda c: (c[0], c[1]))
    return m["id"], s, price(m)


QUERIES = [
    "hi how are you",
    "tell me a joke",
    "what's the capital of peru",
    "write a python function to dedupe a list",
    "our kafka consumers deadlock under rebalance, find root cause",
    "prove there are infinitely many primes and formalize it in Lean",
    "browse three sites and compare laptop prices",
    "build me a landing page for a coffee shop",
    "make a bar chart of monthly revenue",
    "draw an SVG icon of a rocket",
    "make a three.js scene of a rotating planet",
    "make a snake game in the browser",
    "generate a photo of a fox in a spacesuit",
]

if __name__ == "__main__":
    t = time.time(); models = load_models(); load_ms = int((time.time() - t) * 1000)
    print(f"loaded {len(models)} models in {load_ms}ms (cache this in real use)\n")
    for q in ([sys.argv[1]] if len(sys.argv) > 1 else QUERIES):
        a, ms = jev({"user_message": q}, {
            "need": {"type": "choice", "instructions": "What kind of work is this request?",
                     "criteria": {k: v[1] for k, v in NEEDS.items()}},
            "difficulty": {"type": "score", "instructions": "How hard is this request to do well?",
                           "criteria": DIFFICULTY_SCALE},
        })
        need, diff = a["need"]["choice"], int(a["difficulty"]["score"])
        mid, s, p = pick(models, need, diff)
        ps = f"${p:.2f}/M" if p is not None else "-"
        print(f"{ms:4}ms  {need:9} {DIFFICULTY[diff]:8} -> {str(mid):38} score={s} {ps:>10}  | {q}")

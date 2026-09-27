"""Shared helpers: fm (local Apple model) and Jev (OpenRouter decisions API). No dependencies."""
import json, os, subprocess, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "~typesafe/jev-latest"


def fm(instructions, text, timeout=5):
    """Ask the on-device model. Returns (answer, ms). Timeout matters: fm can hang."""
    t = time.time()
    try:
        out = subprocess.run(
            ["fm", "respond", "--no-stream", "-g", "-i", instructions, text],
            capture_output=True, text=True, timeout=timeout, env={**os.environ, "NO_COLOR": "1"},
        ).stdout.strip()
    except subprocess.TimeoutExpired:
        out = None
    return out, int((time.time() - t) * 1000)


def jev(state, questions):
    """Ask Jev typed questions about a state. Returns (answers, ms)."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("Set OPENROUTER_API_KEY")
    body = json.dumps({"model": JEV_MODEL, "state": state, "questions": questions}).encode()
    req = urllib.request.Request(JEV_URL, body, {"content-type": "application/json", "authorization": "Bearer " + key})
    t = time.time()
    answers = json.loads(urllib.request.urlopen(req, timeout=30).read())["answers"]
    return answers, int((time.time() - t) * 1000)


def choice(state, options, instructions="Pick the best option"):
    """One Jev choice question. options = {id: description}. Returns (id, confidence, ms)."""
    a, ms = jev(state, {"pick": {"type": "choice", "instructions": instructions, "criteria": options}})
    return a["pick"]["choice"], a["pick"]["confidence"], ms


def prompt(name):
    return (ROOT / "prompts" / f"{name}.md").read_text()

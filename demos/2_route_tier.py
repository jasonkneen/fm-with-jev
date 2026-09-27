"""Jev picks haiku / sonnet / opus for a message."""
import sys
from common import choice

TIERS = {
    "haiku": "greetings, trivia, one-line facts, typos, tiny edits",
    "sonnet": "normal coding, explaining code, writing, emails, config, UI features",
    "opus": "system design, architecture, proofs, root-cause debugging of complex systems",
}
QUERIES = ["hi how are you", "write a python function to dedupe a list",
           "draft an email declining a meeting", "plan the migration of our monolith to microservices"]
for q in ([sys.argv[1]] if len(sys.argv) > 1 else QUERIES):
    tier, conf, ms = choice({"user_message": q}, TIERS, "Pick the model tier that should handle this message")
    print(f"{ms:5}ms  {tier:6} p={conf:.2f}  {q}")

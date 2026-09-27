"""Both together on one thread: fm titles it, Jev routes it. Run in parallel."""
import sys
from concurrent.futures import ThreadPoolExecutor
from common import fm, choice, prompt

TIERS = {
    "haiku": "greetings, trivia, one-line facts, typos, tiny edits",
    "sonnet": "normal coding, explaining code, writing, emails, config, UI features",
    "opus": "system design, architecture, proofs, root-cause debugging of complex systems",
}
thread = sys.argv[1] if len(sys.argv) > 1 else (
    "USER: our kafka consumers deadlock under rebalance\nASSISTANT: Can you share logs?\n"
    "USER: attached, it happens only when a partition moves during a commit")
with ThreadPoolExecutor() as ex:
    t = ex.submit(fm, prompt("title"), thread)
    r = ex.submit(choice, {"conversation": thread}, TIERS, "Pick the tier for the latest user message")
    (title, tms), (tier, conf, rms) = t.result(), r.result()
print(f"title: {title} ({tms}ms, fm)\nroute: {tier} p={conf:.2f} ({rms}ms, jev)")

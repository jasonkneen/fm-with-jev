"""fm writes a conversation title. Jev can't write text, so this is fm's job."""
import sys
from common import fm, prompt

THREADS = [
    "USER: hey can you help me fix the CORS error on my express server when calling from localhost:5173",
    "USER: my electron app crashes after upgrading to electron 33, Cannot find module better-sqlite3.node\n"
    "ASSISTANT: Run npx @electron/rebuild.\nUSER: now electron-builder notarization fails on the .node file",
    "USER: I want to plan a trip to Japan in April with kids, 10 days",
]
for t in ([sys.argv[1]] if len(sys.argv) > 1 else THREADS):
    title, ms = fm(prompt("title"), t)
    print(f"{ms:5}ms  {title}")

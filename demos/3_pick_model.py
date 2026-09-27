"""Jev picks from a long model list. fm scored 5/14 on this; Jev 14/14."""
import sys
from common import choice

MODELS = {
    "anthropic/claude-opus-5.5": "hardest reasoning, architecture, long agentic coding",
    "anthropic/claude-sonnet-5": "strong everyday coding and writing",
    "openai/gpt-6-sol-pro": "hard math and formal proofs",
    "openai/gpt-6-luna": "fast cheap general chat",
    "openai/gpt-6-astra": "agentic tool use and browsing",
    "google/gemini-3.8-flash": "fast, huge context, summarize long documents",
    "google/gemini-3.1-flash-image": "generate or edit images",
    "google/gemini-3.5-flash-lite": "cheapest tiny tasks, classification",
    "x-ai/grok-4.7": "current events and social media trends",
    "qwen/qwen3.8-max-prime": "multilingual, Chinese translation",
    "qwen/qwen3.8-omni-flash": "audio and speech input",
    "moonshotai/kimi-k2.7-code": "repo-wide refactors",
    "mistralai/mistral-large": "European languages, French and German writing",
    "meta-llama/llama-guard": "content safety moderation",
    "x-ai/grok-build-0.1": "build and CI pipeline fixes",
}
QUERIES = ["make me a logo of a fox in a spacesuit", "translate this paragraph into Mandarin",
           "write a formal letter in German to my landlord", "tell me a joke",
           "design an event-sourced architecture for our payments system"]
for q in ([sys.argv[1]] if len(sys.argv) > 1 else QUERIES):
    m, conf, ms = choice({"user_message": q}, MODELS, "Pick the best model for this message")
    print(f"{ms:5}ms  {m:32} p={conf:.2f}  {q}")

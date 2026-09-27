# fm-with-jev

Small, fast decisions without calling a big model.

- **fm**: Apple's on-device Foundation Model (`/usr/bin/fm`, macOS 27). Free, offline, no API key. Writes short text.
- **Jev**: TypeSafe's decision model on OpenRouter (`~typesafe/jev-latest`). Picks from a list and returns a confidence. Doesn't write text.

**Short version:** use fm for titles and Jev for anything that means picking from a list.

## Which to use

| Job | Use | Why |
|---|---|---|
| Name a conversation | **fm** | Jev can't write text |
| Route to haiku / sonnet / opus | **Jev** | 10/10, faster |
| Pick a model from a long list | **Jev** | fm falls apart on long lists |
| Pick a tool | **Jev** | Both 15/15; Jev is faster and gives a confidence |
| Offline fallback | **fm** | Runs with no network |

## Test results

Tested 2026-09-27 on an Apple Silicon Mac running macOS 27. fm ran with greedy sampling, so its answers are repeatable.

### Summary

| Test | fm | Jev |
|---|---|---|
| Tier: haiku / sonnet / opus (10 queries) | 9/10 | **10/10** |
| Pick from 20 models (14 queries) | 5/14, 1 hang | **14/14** |
| Pick from 40 tools (15 queries) | **15/15** | **15/15** |
| Average speed per decision | ~0.45s | **~0.31s** |
| Confidence score | no | yes (0–1) |
| Cost | free | fractions of a cent |
| Works offline | yes | no |

### Tier routing

| Query | Expected | fm | Jev (confidence) |
|---|---|---|---|
| hi how are you | haiku | ✅ haiku | ✅ haiku (1.00) |
| what's the capital of peru | haiku | ✅ haiku | ✅ haiku (1.00) |
| rename variable x to count | haiku | ❌ sonnet | ✅ haiku (0.65) |
| write a python function to dedupe a list | sonnet | ✅ | ✅ (0.91) |
| how do I center a div | sonnet | ✅ | ✅ (0.97) |
| draft an email declining a meeting | sonnet | ✅ | ✅ (1.00) |
| add pagination to my API endpoint | sonnet | ✅ | ✅ (1.00) |
| prove infinitely many primes, formalize in Lean | opus | ✅ | ✅ (0.98) |
| kafka consumers deadlock under rebalance | opus | ✅ | ✅ (1.00) |
| plan monolith → microservices migration | opus | ✅ | ✅ (1.00) |

### Picking from 20 models

| Query | Expected | fm | Jev |
|---|---|---|---|
| make a logo of a fox in a spacesuit | gemini flash-image | ✅ | ✅ |
| translate into Mandarin | qwen max-prime | ❌ qwen omni (audio model) | ✅ |
| what's trending on X today | grok-4.7 | ✅ | ✅ |
| prove a Riemann zeta result | gpt-6-sol-pro | ❌ answered "3" | ✅ |
| summarize a 400 page PDF | gemini-3.8-flash | ✅ | ✅ |
| is this comment hate speech | llama-guard | ❌ refused | ✅ |
| formal letter in German | mistral-large | ❌ hung (20s timeout) | ✅ |
| rename a class across the repo | kimi-k2.7-code | ✅ | ✅ |
| classify a ticket | gemini flash-lite | ❌ claude-sonnet-5 | ✅ |
| transcribe a voice memo | qwen omni-flash | ❌ dropped the `qwen/` prefix | ✅ |
| browse sites, compare prices | gpt-6-astra | ✅ | ✅ |
| event-sourced payments architecture | claude-opus-5.5 | ❌ claude-sonnet-5 | ✅ (0.77) |
| GitHub Actions cache step fails | grok-build | ❌ claude-sonnet-5 | ✅ |
| tell me a joke | gpt-6-luna | ❌ claude-sonnet-5 | ✅ |

With a long list of model names, fm falls back to one default answer. Tool names describe what they do; model names don't.

### Picking from 40 tools

Both scored 15/15: git_commit, kube_logs, calendar_create, weather, grep, image_generate, slack_post, db_query, memory_save, deploy_vercel, transcribe_audio, maps_directions, create_pr, calculator, open_app. Jev's lowest confidence was 0.81, on "ship the frontend to production" → deploy_vercel.

### Titles (fm)

| Thread | Title |
|---|---|
| Fix CORS on an express server | CORS Error Fix for Express |
| Electron 33 + better-sqlite3 + notarization (5 turns) | Electron Build Error |
| Japan trip with kids | Japan Family Trip Planning |
| Kafka deadlock (3 turns) | Kafka Consumer Deadlock During Rebalance |

### Speed

| | First call | Warm |
|---|---|---|
| `fm respond` (CLI) | ~0.95s (up to ~4s after a reboot, while the model loads) | ~0.45s |
| `fm serve` (HTTP) | ~0.44s | ~0.38–0.44s |
| Jev decisions API | ~0.4s | ~0.28–0.42s |
| fm title + Jev route in parallel | | ~0.9s total |

### Routing by OpenRouter benchmarks (`6_benchmark_route.py`)

OpenRouter's `/api/v1/models` includes a `benchmarks` field for many models: Artificial Analysis intelligence, coding and agentic indexes (189 models), and Design Arena ELO by category, such as website, dataviz, svg, 3d, gamedev and image (251 models).

1. One Jev call answers two questions: what kind of work this is, and how hard it is (0–3).
2. Code picks the top-scoring model on the matching benchmark, under a price cap set by the difficulty: $1, $5 or $20 per 1M output tokens, or no cap for hard work.

Neither fm nor Jev ever sees a model name. Loading the model list takes about 160ms; cache it.

| Query | Jev: type, difficulty | Picked | Score | $/M out |
|---|---|---|---|---|
| hi how are you | chat, trivial | xiaomi/mimo-v2.6-pro | 46.3 | 0.87 |
| write a python function to dedupe a list | coding, trivial | z-ai/glm-5.3-flash | 71.5 | 0.14 |
| kafka consumers deadlock, find root cause | reasoning, moderate | anthropic/claude-opus-5.5 | 57.6 | 20.00 |
| prove infinite primes, formalize in Lean | reasoning, moderate | anthropic/claude-opus-5.5 | 57.6 | 20.00 |
| browse three sites, compare laptop prices | agentic, simple | z-ai/glm-5.3 | 53.1 | 4.40 |
| landing page for a coffee shop | website, simple | meta/muse-spark-1.3 | 1362 | 4.25 |
| bar chart of monthly revenue | dataviz, simple | z-ai/glm-5.1 | 1366 | 3.03 |
| SVG icon of a rocket | svg, simple | meta/muse-spark-1.3 | 1361 | 4.25 |
| three.js rotating planet | 3d, simple | meta/muse-spark-1.3 | 1417 | 4.25 |
| snake game in the browser | gamedev, simple | z-ai/glm-5.3 | 1355 | 4.40 |
| photo of a fox in a spacesuit | image, simple | google/gemini-3.1-flash-image-preview | 1279 | 3.00 |

Jev put all 13 test queries in a sensible category, at about 0.3s per call. The wording of the difficulty scale matters. With bare labels (trivial / simple / moderate / hard), Jev rated the Lean proof "simple" and sent it to a cheap model. Describing each level fixed it (`DIFFICULTY_SCALE` in the demo).

## Run

```bash
export OPENROUTER_API_KEY=...
cd demos
python3 1_title.py          # fm: conversation titles
python3 2_route_tier.py     # jev: haiku / sonnet / opus
python3 3_pick_model.py     # jev: pick from 15 models
python3 4_pick_tool.py      # jev: pick from 40 tools
python3 5_combined.py       # both at once on one thread
python3 6_benchmark_route.py  # jev + OpenRouter benchmark data picks the model
python3 2_route_tier.py "your own message"
```

No dependencies. Python 3.9+. fm needs macOS 27 with Apple Intelligence on.

## Layout

```
prompts/title.md    fm instructions for titles
prompts/route.md    fm instructions for tier routing (fm fallback)
demos/common.py     fm() and jev() helpers
demos/1-5_*.py      demos
```

## Calling Jev

```json
POST https://openrouter.ai/api/alpha/decisions
{
  "model": "~typesafe/jev-latest",
  "state": { "user_message": "..." },
  "questions": {
    "pick": { "type": "choice", "instructions": "Pick the best option",
              "criteria": { "id_a": "description", "id_b": "description" } }
  }
}
```

Question types are `choice`, `score` and `noul`. One request can ask several questions at once.

## Gotchas

- **fm can hang** on some prompts. Always set a timeout; the demos use 5s.
- **One hung `fm serve` request blocks the whole server** for about 10 minutes. Use the CLI, or restart the server when a request times out.
- **`fm serve` streams by default.** Send `"stream": false` to get plain JSON.
- **fm's instructions must be one file per task.** With a combined file and a `title ::` prefix, long threads lost the prefix and fm returned a model name instead of a title.
- **fm is unreliable about itself.** Asked about its own context size, it made things up.
- **`typesafe/jev-router` on chat completions is a different product.** It runs your request on a model it picks, ignores `reasoning` and `models` parameters, and errors on image requests. Use the decisions API for classification.

## Related

- [gargpratyush/jev-router](https://github.com/gargpratyush/jev-router): per-turn Jev routing for Claude Code and Codex
- [kerpopule/hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills): Jev skills for routing, memory, compaction, triage, computer and browser use
- [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction): Jev helper tools for compaction, ranking and routing
- [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast): browser agent driven by Jev decisions
- [CTNicholas/jev-workflow-builder](https://github.com/CTNicholas/jev-workflow-builder): multiplayer Jev workflow builder

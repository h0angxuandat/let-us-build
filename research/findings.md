# Research findings — let-us-build (2026-06-30)

Grounded research backing the architecture decisions. Sources cited inline.

## A. agentmemory (memory subsystem)
**Naming collision — important:**
- `rohitg00/agentmemory` = **TypeScript MCP/REST memory server**, SQLite-backed, 4-tier
  consolidation (working→episodic→semantic→procedural), Ebbinghaus decay, hybrid **RRF** retrieval
  (BM25 + vector + knowledge-graph), embeddings default `all-MiniLM-L6-v2` (pluggable). REST on
  **:3111**; ~7 core MCP tools (`memory_recall`, `memory_smart_search`, `memory_save`,
  `memory_sessions`, `memory_export`, `memory_audit`, `memory_governance_delete`). Apache-2.0.
  **This is the repo the user named, and it is already running in this environment** (`mcp__agentmemory__*`).
- `elizaOS/agentmemory` (PyPI `agentmemory`) = **different** Python lib, ChromaDB/Postgres, with the
  `create_memory/search_memory/get_memories/...` CRUD API. MIT. We are NOT using this for the store.

**Decision (revised 2026-07-01)**: **build our own** `lub_memory` in Python on Postgres+pgvector
rather than run the Node sidecar — memory is core IP and a Python+CLI product should stay
single-runtime. We borrow agentmemory's 4-tier model conceptually and add first-class `ticketId`
scope + role-permission matrix + consolidation as native. Phased retrieval (vector → +RRF →
+graph) behind a stable `MemoryClient`. See `decisions.md` D4-rev / `system-design.md` §5.
Sources: github.com/rohitg00/agentmemory · pypi.org/project/agentmemory (elizaOS).

## B. sia (self-improvement)
`hexo-ai/sia` — Python 3.11+, MIT. Paper "SIA: Self Improving AI with Harness & Weight Updates"
(arXiv 2605.27276). Two levers driven by a **fixed verifier**:
- **Harness lever**: rewrite scaffold (system prompt, tool dispatch, retry, parsing).
- **Weight lever**: LoRA (rank 32) fine-tune; RL recipe chosen by reward signal.
Loop = **Meta-Agent** (build target) → **Target Agent** (attempt, log trajectory) → **Feedback
Agent** (score trajectory, pick ONE action per generation). Artifacts per generation on disk
(`runs/run_id/gen_n/`: evolved agent, trajectory, `improvement.md`). Backends: Claude Agent SDK,
OpenAI, Pydantic-AI, OpenHands.
**Stated risk**: both levers optimize the same verifier → "coupled Goodhart effects."

**Decision**: adopt the **harness lever + scored-feedback** backbone per role; defer LoRA. The crux
is a **per-role verifier** (Dev: tests pass + review + CI; QE: defects caught vs escaped; BA:
requirement churn; Designer: a11y/visual-regression + design acceptance; TL: ADR reversal rate; PM:
estimate accuracy). Goodhart guard = cross-role review + held-out checks (sia lacks this).
Sources: github.com/hexo-ai/sia · arxiv.org/abs/2605.27276.

## C. Orchestration framework
Compared LangGraph, CrewAI, AutoGen/AG2, OpenAI Agents SDK, roll-your-own (pydantic-ai/litellm).
Discriminator = **durable, long-running, pausable/resumable state with HITL**.
- **LangGraph (MIT)** — best durability: Postgres checkpointers + `interrupt()` = exact pause/
  resume = the `human needed` lane. Per-node model config + LiteLLM = per-agent provider. Steepest
  learning curve. `astream_events` → WebSocket → Solid. **CHOSEN.**
- CrewAI — ergonomic role agents, weak durable pause/resume.
- AutoGen/AG2 — richest debate (GroupChat) but in-memory state + fork-maturity risk → borrow its
  GroupChat pattern *inside* a LangGraph node.
- OpenAI Agents SDK — clean handoffs but no durable execution (needs Temporal/DBOS).
- pydantic-ai + Temporal — strongest true durability but all orchestration hand-rolled → kept as
  future upgrade path.
**LLM abstraction = LiteLLM** (per-agent model string, centralized keys/cost/rate/fallback).
Sources: docs.langchain.com/oss/python/langgraph/durable-execution · diagrid.io (checkpoints≠durable
execution) · openai.github.io/openai-agents-python/models/litellm · ai.pydantic.dev/durable_execution/temporal.

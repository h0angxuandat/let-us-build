# let-us-build

> An **AI software company in a box**. Run a CLI, open a web UI, describe the product you want, and
> a team of role-based AI agents (BA · Designer · Tech Lead · Dev · QE · PM) builds it end-to-end —
> tracked live on a 4-lane Kanban board, with shared memory and agents that improve over time.

## Status
🧭 **Planning complete — implementation not yet started.** This repo currently contains the
architecture & plan. Code lands milestone by milestone (see `document/backlog.md`).

## What it does (vision)
1. `let-us-build start` boots the core + web UI.
2. Create a project, feed requirements / designs / files.
3. Agents auto-pick tickets from the `plan` lane and move them through the SDLC:
   `plan → processing → testing → done`, pausing into `human needed` only when a human
   decision is required.
4. The run is **done/paused** when every ticket is `done` or `human needed`.

## Stack
- **Core**: Python 3.12 · FastAPI · **LangGraph** (durable, resumable orchestration + HITL)
- **LLM**: **LiteLLM** — per-agent provider/model (Anthropic + OpenAI at MVP)
- **Web**: **SolidJS / SolidStart** · WebSocket realtime
- **DB**: Postgres (+pgvector) · **Memory**: `rohitg00/agentmemory` sidecar (REST/MCP)
- **Self-improvement**: sia-inspired harness lever (north-star)

## Docs
- Product: [`product/PRD.md`](product/PRD.md)
- Architecture: [`document/system-design.md`](document/system-design.md)
- Agents & SDLC: [`document/agent-sdlc-flow.md`](document/agent-sdlc-flow.md)
- Repo layout: [`document/monorepo-layout.md`](document/monorepo-layout.md)
- Build plan: [`document/backlog.md`](document/backlog.md)
- Research: [`research/findings.md`](research/findings.md)

## MVP scope
Milestones **M0–M6 + M8** (a usable agent team that builds + tests code with memory). Self-
improvement (M7) and git/PR integration are north-star. See `document/backlog.md`.

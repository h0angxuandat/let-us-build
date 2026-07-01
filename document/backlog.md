# Build Backlog — let-us-build

> Status: DRAFT for review · Date: 2026-06-30.
> This is the plan to BUILD the platform itself (not tickets the platform generates). Organized
> into milestones with dependency-ordered tickets. Each ticket = roughly one PR. Keys: `LUB-###`.

## Milestone map (build order)

| # | Milestone | Goal | Depends on |
|---|---|---|---|
| **M0** | Foundations | Monorepo skeleton, DB, sidecar, CLI boots an empty app. | — |
| **M1** | Domain + persistence | Projects/tickets/agents data model + repositories + migrations. | M0 |
| **M2** | Web shell + Kanban | SolidJS app, 4-lane board, intake, ticket detail (read), WS feed. | M1 |
| **M3** | LLM + agents (single) | LiteLLM router; one agent (BA) runs a ticket end-to-end. | M1 |
| **M4** | Orchestrator + lanes | LangGraph per-ticket graph, scheduler/auto-pick, HITL interrupt. | M3 |
| **M5** | Full roster + Agile/DDD | All six agents; DDD strategic+tactical; sprint/ceremony engine; discussion; Agile SDLC flow. | M4 |
| **M6** | Memory | agentmemory sidecar client + scoping + consolidation. | M3 |
| **M7** | Self-improvement | Lessons + per-role verifiers + feedback loop (harness lever). | M5, M6 |
| **M8** | Sandbox + code prod | Workspace manager + Docker sandbox; QE runs tests. | M5 |
| **M9** | Hardening | Cost caps, observability, e2e demo, docs, packaging. | M2–M8 |

> MVP = **M0–M6 + M8** (a usable team that builds and tests code with memory). M7 (self-improve)
> and parts of M9 are north-star. Confirm MVP cut at review.

---

## M0 — Foundations
- **LUB-001** Monorepo skeleton: folders per `monorepo-layout.md`, `pyproject.toml` workspace, READMEs, lint/type/test config. *(plan)*
- **LUB-002** `docker-compose.yml`: Postgres+pgvector + agentmemory sidecar; `.env.example`. *(plan, deps: 001)*
- **LUB-003** CLI scaffold (Typer): `init` (scaffold `.env`), `start` (boot core+web, health, open browser), graceful shutdown. *(plan, deps: 001)*
- **LUB-004** Core-api skeleton: FastAPI app factory, `/health`, settings loader. *(plan, deps: 001)*

## M1 — Domain + persistence
- **LUB-010** SQLAlchemy models for the full domain model (Project, Requirement, Agent, **Sprint**, Ticket [Epic/Story/Task via parent_id, with bounded_context/aggregate], TicketEvent, Discussion, Message, Artifact, HumanRequest, Lesson, Run). Organized as DDD bounded contexts. *(plan, deps: 004)*
- **LUB-011** Alembic migrations + seed of 6 default agent configs. *(plan, deps: 010)*
- **LUB-012** Repository-pattern data access per aggregate. *(plan, deps: 010)*
- **LUB-013** REST CRUD: projects, requirements, agents config. *(plan, deps: 012)*

## M2 — Web shell + Kanban
- **LUB-020** SolidStart app scaffold, routing, design tokens, API/WS clients. *(plan, deps: 013)*
- **LUB-021** Dashboard + create-project form. *(plan, deps: 020)*
- **LUB-022** Requirement intake (rich text + file upload + links). *(plan, deps: 021)*
- **LUB-023** Kanban board: 4 lanes, ticket cards, realtime via WS. *(plan, deps: 020)*
- **LUB-024** Ticket detail (read): description, history, artifacts, discussion transcript. *(plan, deps: 023)*
- **LUB-025** Per-agent config UI (provider/model/skills/enabled). *(plan, deps: 013)*
- **LUB-026** WS gateway in core-api + event contracts. *(plan, deps: 013)*

## M3 — LLM + first agent
- **LUB-030** `lub_llm` LiteLLM router + `AgentLLMConfig` + budget/rate caps + fallback. *(plan, deps: 004)*
- **LUB-031** `Agent` base (config, skill loading, `run()`) + registry. *(plan, deps: 030)*
- **LUB-032** BA agent + requirements skills; produces BRD/user-stories artifact for one ticket. *(plan, deps: 031, 012)*
- **LUB-033** Wire one ticket: create → BA runs → artifact persisted → visible in web. *(plan, deps: 032, 024)*

## M4 — Orchestrator + lanes
- **LUB-040** LangGraph per-ticket graph + `AsyncPostgresSaver` checkpoints. *(plan, deps: 033)*
- **LUB-041** Lane state machine + transition rules; derive lane from stage/block. *(plan, deps: 040)*
- **LUB-042** Scheduler / auto-pick loop (deps satisfied + role match + concurrency caps). *(plan, deps: 041)*
- **LUB-043** HITL `interrupt()` → `human_needed`; `/tickets/{id}/answer` resumes thread. *(plan, deps: 040, 026)*
- **LUB-044** `start project` → PM seeds initial backlog tickets. *(plan, deps: 042)*
- **LUB-045** Run stop-condition evaluation (all done / done+human_needed). *(plan, deps: 042)*

## M5 — Full roster + Agile/DDD flow + discussion
- **LUB-050** Designer, Tech Lead, Developer, QE, PM agents + their skill packs (incl. DDD + Agile skills). *(plan, deps: 031)*
- **LUB-051** DDD strategic: BA ubiquitous-language glossary + TL bounded contexts + context map artifacts (stored in memory semantic tier). *(plan, deps: 050, 062)*
- **LUB-052** DDD tactical: TL domain model (aggregates/entities/VOs/domain events) → slice stories into per-aggregate tasks (bounded_context/aggregate tagged). *(plan, deps: 051)*
- **LUB-053** Sprint + ceremony engine: Sprint entity, sprint planning, review/demo, retrospective→Lessons; board = sprint board. *(plan, deps: 042, 045)*
- **LUB-054** Discussion subgraph (bounded multi-turn, chair summarizes decision+rationale). *(plan, deps: 040, 050)*
- **LUB-055** Agile SDLC wired: inception → per-sprint Design/Tech-design→Impl→Test→Review→Done with deps + bug loop + max-retry. *(plan, deps: 052, 053, 054)*

## M6 — Memory (own `lub_memory`, Python-native)
- **LUB-060** `MemoryRecord` model + migration (tiers, scoping, embedding, tsvector, metadata) on Postgres+pgvector. *(plan, deps: 010)*
- **LUB-061** `MemoryClient` API: `remember()` / `recall()` (vector similarity + metadata filters) over repositories. *(plan, deps: 060, 030)*
- **LUB-062** Scoping + role-permission matrix (project/ticket/role; shared vs role-private tiers), enforced in client. *(plan, deps: 061)*
- **LUB-063** Retrieval-augmented agent context: every `run()` opens with `recall()`. *(plan, deps: 062, 031)*
- **LUB-064** Consolidation on ticket close (working → episodic summary) as background task. *(plan, deps: 062)*
- **LUB-065** *(Phase 2)* Hybrid retrieval: `tsvector` keyword search + RRF fusion with vector. *(plan, deps: 061)*
- **LUB-066** *(Phase 3, optional)* Salience decay/strengthening + lightweight graph links. *(plan, deps: 061)*

## M7 — Self-improvement (north-star)
- **LUB-070** `Lesson` capture: post-ticket feedback step reads trajectory + score → lesson. *(plan, deps: 053, 062)*
- **LUB-071** Per-role verifiers (Dev/QE/BA/Designer/TL/PM reward signals). *(plan, deps: 053)*
- **LUB-072** Lesson retrieval into future same-role/type tickets (reflexion). *(plan, deps: 070)*
- **LUB-073** Goodhart guard: cross-role review + held-out checks. *(plan, deps: 071)*
- **LUB-074** (stub) Weight-update lever interface (LoRA) — deferred, behind interface. *(plan, deps: 071)*

## M8 — Sandbox + code production
- **LUB-080** Workspace manager: `./workspaces/<project>` lifecycle; Dev edits real files. *(plan, deps: 050)*
- **LUB-081** Docker-per-project sandbox (subprocess fallback) test runner. *(plan, deps: 080)*
- **LUB-082** QE runs tests in sandbox → `test_result` artifact → pass/fail drives lane. *(plan, deps: 081, 053)*
- **LUB-083** Diff view in ticket detail (web). *(plan, deps: 082, 024)*

## M9 — Hardening
- **LUB-090** Cost/budget dashboard + per-agent caps surfaced in UI. *(plan, deps: 030, 025)*
- **LUB-091** Observability: structured logs, agent activity stream, traces. *(plan, deps: 040)*
- **LUB-092** E2E demo: one-paragraph brief → running, tested artifact. *(plan, deps: MVP set)*
- **LUB-093** Docs + packaging: `pip install`/`uvx let-us-build`, quickstart. *(plan, deps: 092)*
- **LUB-094** Git/PR integration for generated code (post-MVP, OQ2). *(plan, deps: 080)*

---

## Initial board state (when we start building)
All tickets above begin in **plan**. We (you + me) act as the human team for the *platform's own*
build, picking tickets in dependency order, milestone by milestone. Each completed ticket ships as
its own PR per the orchestrator workflow.

## Confirm at review
- MVP cut = M0–M6 + M8? (defer M7 self-improvement + M9.094 git/PR.)
- OQ1 SolidJS vs React · OQ2 code prod (workspace vs git/PR) · OQ3 providers day-one ·
  OQ4 sandbox (Docker vs subprocess) · OQ5 single vs multi-user. (See PRD §9.)

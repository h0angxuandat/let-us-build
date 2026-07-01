# System Design — let-us-build

> Status: DRAFT for review · Date: 2026-06-30 · Companion to `product/PRD.md`.
> This document defines the architecture, component boundaries, data model, orchestration,
> memory, and self-improvement design. Agent/SDLC detail is in `agent-sdlc-flow.md`;
> folder layout in `monorepo-layout.md`; work plan in `backlog.md`.

## 1. Architecture at a glance

```
                          ┌─────────────────────────────────────────────┐
   `let-us-build start`   │                 let-us-build                 │
        (CLI)  ──────────▶│  boots core + web, opens browser, health     │
                          └─────────────────────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼──────────────────────────────────┐
        ▼                                  ▼                                  ▼
┌───────────────┐   WebSocket / REST  ┌─────────────────────┐
│  Web (Solid)  │◀───────────────────▶│   Core (FastAPI)    │           ┌──────────────────┐
│  - dashboard  │   realtime events   │  - REST API         │  LiteLLM  │ LLM providers     │
│  - intake     │                     │  - WS gateway       │──────────▶│ Anthropic/OpenAI/ │
│  - Kanban x4  │                     │  - Orchestrator     │           │ local/...         │
│  - ticket view│                     │    (LangGraph)      │           └──────────────────┘
│  - agent cfg  │                     │  - Agent runtime    │
└───────────────┘                     │  - LLM router       │
                                       │    (LiteLLM)        │
                                       │  - Memory (lub_     │   ALL OF CORE IS PYTHON —
                                       │    memory, native)  │   NO Node sidecar.
                                       │  - Improvement loop │
                                       │  - Workspace mgr    │
                                       └─────────────────────┘
                                          │            │
                                          ▼            ▼
                                  ┌────────────┐  ┌────────────────────┐
                                  │ Postgres   │  │ Project workspace   │
                                  │ + pgvector │  │ ./workspaces/<proj> │
                                  │ app state  │  │ generated code, run │
                                  │ + memory   │  │ in sandbox          │
                                  │ + LG ckpt  │  └────────────────────┘
                                  └────────────┘
```

### Component responsibilities
- **CLI** (`let-us-build`): single entrypoint. `init` (config/keys), `start` (boot core+web, health
  checks, open browser), graceful shutdown. Thin wrapper over the core process.
- **Web (SolidJS / SolidStart)**: project dashboard, requirement intake (text + files + links),
  the 4-lane Kanban, ticket detail (discussion transcript, artifacts, diffs, human-answer box),
  per-agent config UI, live activity stream. Pure client of the core API + WS.
- **Core (FastAPI, Python)**: the brain. REST API + WebSocket gateway + the LangGraph
  orchestrator + agent runtime + LiteLLM router + memory client + improvement loop + workspace
  manager.
- **Memory** (`lub_memory`, native Python): our own memory subsystem on Postgres + pgvector. No
  Node sidecar. Conceptually borrows agentmemory's 4-tier model; see §5.
- **Postgres (+ pgvector)**: application state (projects, tickets, agents, discussions,
  artifacts), the **memory store** (records + embeddings), AND LangGraph checkpoints for
  durable/resumable orchestration — one store, one runtime.
- **Project workspace + sandbox**: where generated code lives and is built/tested.

## 2. Technology decisions (with rationale)

| Concern | Choice | Why |
|---|---|---|
| Core language | **Python 3.12** | User-chosen; best AI/agent ecosystem; matches sia + LangGraph. |
| Orchestrator | **LangGraph** | Only option giving durable, pausable/resumable long-running state + `interrupt()` HITL out of the box — maps 1:1 to the `human needed` lane (thread = ticket). MIT. |
| LLM abstraction | **LiteLLM** | Per-agent provider+model behind one interface; centralizes keys/cost/rate-limit/fallback across 6 agents. Plugs into LangGraph nodes. |
| Web framework | **SolidJS / SolidStart** | User-chosen. Fine-grained reactivity suits a realtime Kanban; SolidStart gives routing + server endpoints if needed. |
| Realtime | **WebSocket** | Push orchestrator/ticket/discussion events to the board. LangGraph `astream_events` → WS. |
| App DB | **Postgres + pgvector** | Relational app state + LangGraph `AsyncPostgresSaver` checkpoints in one store; pgvector available if we ever co-locate embeddings. |
| Memory | **Own Python package `lub_memory` on Postgres + pgvector** | Memory is core IP for an AI-first product; keep the platform single-runtime (no Node sidecar in a Python+CLI app); native ticket/role scoping. Borrows agentmemory's tier model conceptually, phased retrieval (see §5). |
| Self-improvement | **sia-inspired harness-lever loop** (custom, Python) | Adopt the prompt/skill/lesson + scored-feedback backbone; defer LoRA weight updates. MIT reference. |
| Code sandbox | **Docker-per-project (default), local subprocess fallback** | Isolate generated code execution/tests. (OQ4 — confirm.) |

**Upgrade path preserved**: keep agent definitions thin/provider-agnostic so we can later move the
durability layer to **pydantic-ai + Temporal** if we need infra-grade crash-safe execution beyond
LangGraph checkpoint-resume.

## 3. Domain model (app DB)

```
Project        id, name, description, target_platform, constraints, status, created_at
Requirement    id, project_id, kind(brief|design|file|link), content/text, file_ref, created_at
Agent          id, project_id|null(global default), role(enum), display_name, enabled,
               provider, model, temperature, system_prompt, skill_ids[], config_json
Sprint         id, project_id, index, goal, status(planned|active|review|done),
               batch_limit, started_at, closed_at            (Agile iteration)
Ticket         id, project_id, sprint_id|null, key(LUB-123), title, description, type(enum),
               lane(enum), status, priority, story_points|null, acceptance_criteria|null,
               bounded_context|null, aggregate|null, assignee_role|null, depends_on[],
               parent_id|null, created_by(user|agent), sdlc_stage, created_at, updated_at
TicketEvent    id, ticket_id, kind(lane_change|assign|comment|artifact|human_request|answer),
               actor(agent_id|user), payload_json, created_at
Discussion     id, ticket_id, topic, participants(role[]), status(open|resolved),
               decision, rationale, transcript_ref, created_at
Message        id, discussion_id, agent_role, content, created_at
Artifact       id, ticket_id, type(BRD|PRD|epic|user_story|ubiquitous_language|context_map|
               domain_model|wireframe|tech_design|code|test_plan|test_result|adr|retro),
               path|inline, version, produced_by(role), created_at
HumanRequest   id, ticket_id, question, options_json|null, status(open|answered),
               answer, answered_at
Lesson         id, project_id|global, role, ticket_type, context, what_happened, lesson,
               score, source_ticket_id, created_at      (self-improvement)
Run            id, project_id, status(running|paused|done), stop_reason, started_at, ...
```

`lane ∈ {plan, human_needed, processing, testing, done}`.
`role ∈ {ba, designer, tech_lead, developer, qe, pm}`.
`ticket.type ∈ {epic, user_story, task, design, tech_design, bug, chore, decision, spike}`.
Epic→Story→Task hierarchy uses `parent_id`. `bounded_context`/`aggregate` tie a ticket to the
DDD model so implementation stays aligned with the domain (see §3.2).

### 3.1 Methodology in the model: Agile + DDD
- **Agile**: `Sprint` groups tickets into iterations; the 4-lane board is the sprint board;
  ceremonies are agent activities (see `agent-sdlc-flow.md` §10); the retrospective emits
  `Lesson`s (§6). Sprint length = a configurable work-batch, not wall-clock.
- **DDD applies to two domains**:
  1. **The product being built** — agents produce `ubiquitous_language`, `context_map`, and
     `domain_model` artifacts; each implementation ticket carries `bounded_context` + `aggregate`
     so generated code mirrors the business domain. The glossary lives in memory's semantic tier
     so all agents share one language.
  2. **This platform** — see §3.2.

### 3.2 This platform's own bounded contexts (DDD strategic)
Our packages are organized as bounded contexts with clear aggregates (roots in **bold**):
| Bounded context | Aggregate roots | Package |
|---|---|---|
| Project & Delivery | **Project**, **Sprint**, **Ticket** (Epic/Story/Task) | `store` + `core-api` |
| Agent Runtime | **Agent**, **Discussion** | `agents` |
| Orchestration | **Run** (+ LangGraph thread per Ticket) | `orchestrator` |
| Memory | **MemoryRecord** | `memory` |
| Knowledge/Improvement | **Lesson** | `improvement` |
| Workspace | **Workspace** (generated code) | `workspace` |

Context relationships: Orchestration drives Project & Delivery; Agent Runtime consumes Memory
(shared kernel = ubiquitous language); Improvement subscribes to Delivery domain events
(ticket/sprint closed) to mint Lessons. Cross-context communication is via domain events, not
reaching into each other's tables (boundary discipline, SR-7).

## 4. Orchestration design (LangGraph)

### Mapping
- **Thread = Ticket.** Each ticket runs as a LangGraph thread with its own checkpointed state.
- **Lane = derived status** from the ticket's stage + whether it's blocked on a human.
- **`interrupt()` = `human needed`.** When an agent needs a human decision it calls `interrupt`
  with a structured `HumanRequest`; the thread persists and the ticket moves to `human_needed`.
  The user's answer resumes the exact node. Other tickets keep running.
- **Auto-pick**: a scheduler loop scans `plan` for tickets whose `depends_on` are satisfied and
  dispatches each to the agent graph for its `sdlc_stage`. Idle-agent / concurrency limits apply.
- **Durable**: `AsyncPostgresSaver` checkpoints every node → survives restart (pause/resume).

### Per-ticket graph (conceptual)
```
 enter → classify(stage) → [role node runs work] → produce artifact(s)
        → need human? ──yes──▶ interrupt(HumanRequest)  → (resume on answer)
        → need cross-role decision? ──yes──▶ discussion subgraph → decision
        → advance lane (processing→testing→done) per stage transition rules
        → on test stage: QE node runs tests in sandbox → pass? done : back to dev (bug ticket)
```

### Discussion subgraph
A bounded multi-turn exchange among the relevant roles (e.g. TL + Dev + QE on an
implementation approach). Round-robin / debate with a max-turns cap; a designated chair (PM or
TL) summarizes into `decision + rationale`, persisted to the ticket and to memory. Implemented as
a loop subgraph inside one node (borrowing the AutoGen GroupChat pattern *inside* LangGraph so we
keep durability).

### Stop condition (LOCKED)
The **Run** is evaluated after every lane change: if **every ticket ∈ {done, human_needed}** the
run is `paused` (if any `human_needed`) or `done` (all `done`). Answering a `human_needed` ticket
re-activates the scheduler.

## 5. Memory design (own `lub_memory` package — build, don't swallow)

**Decision**: we build our own memory subsystem in Python rather than running the
`rohitg00/agentmemory` Node sidecar. Rationale: memory is core IP for an AI-first product; a
Python+CLI product should stay single-runtime (no extra Node service to boot/health-check/package);
and the scoping/permission/consolidation logic we need is custom work either way. We *borrow
agentmemory's tier model conceptually* — standing on the shoulders of their design without coupling
to their server. (See ADR in `decisions.md` D4-rev.)

### Data model (in Postgres + pgvector)
```
MemoryRecord  id, project_id, ticket_id|null, role|null, tier(working|episodic|semantic|procedural),
              type(observation|decision|fact|lesson|artifact_ref), content(text),
              embedding(vector), keywords(tsvector), metadata(jsonb), visibility(shared|role_private),
              salience(float), source_refs[], created_at, last_accessed_at, access_count, expires_at|null
```
- `tier`: **working** (raw ticket activity) → **episodic** (ticket summary on close) → **semantic**
  (project facts/specs) → **procedural** (workflows/decisions). Our own consolidation logic.
- **Scoping is first-class** (not bolted on): `project_id`, `ticket_id`, `role`. A
  **role-permission matrix** governs read/write (e.g. PM/TL read all; Dev writes its own tier;
  semantic/procedural are team-visible; working memory is mostly role-private). Enforced in the
  `MemoryClient` API, not left to caller discipline.

### Retrieval — phased (interface stable across phases)
- **MVP (M6)**: pgvector cosine similarity + metadata filters (`project_id [+ ticket_id] [+ role +
  tier]`). Covers ~80% of the value. Every agent `run()` opens with a `recall()` to assemble context.
- **Phase 2**: add keyword search via Postgres `tsvector`/BM25-style ranking, fused with vector
  results using **Reciprocal Rank Fusion (RRF, k=60)** — matching agentmemory's hybrid quality.
- **Phase 3 (if needed)**: lightweight knowledge-graph traversal (entity/relation links) + decay
  (Ebbinghaus-style salience decay + strengthening on access) for long-lived projects.

### Consolidation
- On **ticket close**: collapse the ticket's `working` records into one `episodic` summary
  (artifact + decision + outcome).
- On **milestone**: promote recurring facts to `semantic`; promote reusable decisions/workflows to
  `procedural`. Consolidation runs as a background task (own logic, LLM-summarized).

### Interface
A single `MemoryClient` (in `packages/memory`) exposes `remember()`, `recall()`, `consolidate()`,
`forget()` over the repository layer. Because it's our code on our DB, there is **no sidecar
availability risk** and no separate fallback path — Postgres being up is already a hard dependency.
The interface is intentionally agentmemory-shaped so we could swap in their server later if ever
desired, but that is not the plan.

## 6. Self-improvement design (sia-inspired, harness lever)

- **Backbone**: per role, after a ticket reaches a verifiable outcome, a **Feedback** step reads
  the ticket trajectory + score and writes a **Lesson** (what worked/failed + the fix). Lessons are
  retrieved into future tickets of the same role/type (reflexion-style). This is the *harness
  lever* — we tune prompts/skills/checklists, not weights.
- **Per-role verifier (the crux)** — define a concrete reward per role:
  - Developer → tests pass + (later) review-approval + sandbox build green.
  - QE → defects caught vs. escaped; test coverage on changed code.
  - BA → requirement churn / rework rate on its tickets.
  - Designer → a11y/visual-regression pass + design-review acceptance.
  - Tech Lead → architecture-decision reversal rate.
  - PM → estimate accuracy / scope-creep.
- **Storage**: Lessons in app DB + promoted to agentmemory procedural tier. (sia's
  `runs/gen_n/improvement.md` ≈ our `Lesson` + memory.)
- **Goodhart guard**: per-role verifiers are gameable (e.g. Dev weakening tests to pass). Use
  cross-role review (QE reviews artifacts) + held-out checks as the perturbation guard sia lacks.
- **MVP**: capture + retrieve lessons + the verifier signals. **Defer**: LoRA weight updates
  (sia's expensive lever) to a later milestone, behind the same interface.

## 7. Realtime & API surface (sketch)

- **REST** (FastAPI): `/projects` CRUD, `/projects/{id}/requirements`, `/projects/{id}/tickets`
  CRUD, `/tickets/{id}` detail, `/tickets/{id}/answer` (resolve human_needed),
  `/agents` config CRUD, `/projects/{id}/start`, `/runs/{id}`.
- **WebSocket** `/ws/projects/{id}`: server→client events `ticket.lane_changed`,
  `ticket.updated`, `discussion.message`, `agent.activity`, `human.requested`, `run.status`.
  Client→server is minimal (subscribe/ack). All mutations go through REST.
- **Auth (MVP)**: single-user local, no auth (or a local token). Multi-user is post-MVP (OQ5).

## 8. Sandbox & code production
- Generated code lives under `./workspaces/<project>/` (a real folder the Dev agent edits).
- Builds/tests run in **Docker per project** (default) or local subprocess (fallback) — isolated
  from the host. QE agent drives tests there; results become `test_result` artifacts.
- **MVP**: write to workspace folder + run tests in sandbox. **Post-MVP**: git init + PR
  integration (OQ2).

## 9. Key risks & mitigations
- **Runaway LLM cost** across 6 agents → LiteLLM budget/rate caps; per-agent model tiering
  (cheap models for routine roles); concurrency limits in the scheduler.
- **Orchestration deadlock / cycles** (Dev↔QE ping-pong) → max-retry per ticket, then auto-route
  to `human_needed`.
- **Goodhart on verifiers** → cross-role review + held-out checks (see §6).
- **Sidecar coupling** → MemoryClient interface + Postgres fallback (see §5).
- **Generated code executing on host** → sandbox isolation (see §8).
- **Scope explosion** → MVP slice in `backlog.md`; north-star features gated behind milestones.

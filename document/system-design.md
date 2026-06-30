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
┌───────────────┐   WebSocket / REST  ┌─────────────────────┐   sidecar  ┌──────────────────┐
│  Web (Solid)  │◀───────────────────▶│   Core (FastAPI)    │───────────▶│  agentmemory      │
│  - dashboard  │   realtime events   │  - REST API         │  REST/MCP  │  service (Node,    │
│  - intake     │                     │  - WS gateway       │  :3111     │  rohitg00) :3111   │
│  - Kanban x4  │                     │  - Orchestrator     │            └──────────────────┘
│  - ticket view│                     │    (LangGraph)      │
│  - agent cfg  │                     │  - Agent runtime    │───────────▶┌──────────────────┐
└───────────────┘                     │  - LLM router       │  LiteLLM   │ LLM providers     │
                                       │    (LiteLLM)        │            │ Anthropic/OpenAI/ │
                                       │  - Memory client    │            │ local/...         │
                                       │  - Improvement loop │            └──────────────────┘
                                       │  - Workspace mgr    │
                                       └─────────────────────┘
                                          │            │
                                          ▼            ▼
                                  ┌────────────┐  ┌────────────────────┐
                                  │ Postgres   │  │ Project workspace   │
                                  │ + pgvector │  │ ./workspaces/<proj> │
                                  │ app state  │  │ generated code, run │
                                  │ + LG ckpt  │  │ in sandbox          │
                                  └────────────┘  └────────────────────┘
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
- **agentmemory sidecar** (rohitg00, Node, port 3111): memory store consumed over REST/MCP.
  Already available in this environment. We do NOT reimplement it.
- **Postgres (+ pgvector)**: application state (projects, tickets, agents, discussions,
  artifacts) AND LangGraph checkpoints for durable/resumable orchestration.
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
| Memory | **agentmemory sidecar (rohitg00) over REST/MCP** | Tiered consolidation + hybrid retrieval + scoping for free; we add ticket scope + role policy. Apache-2.0. |
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
Ticket         id, project_id, key(LUB-123), title, description, type(enum), lane(enum),
               status, priority, assignee_role|null, depends_on[], parent_id|null,
               created_by(user|agent), sdlc_stage, created_at, updated_at
TicketEvent    id, ticket_id, kind(lane_change|assign|comment|artifact|human_request|answer),
               actor(agent_id|user), payload_json, created_at
Discussion     id, ticket_id, topic, participants(role[]), status(open|resolved),
               decision, rationale, transcript_ref, created_at
Message        id, discussion_id, agent_role, content, created_at
Artifact       id, ticket_id, type(BRD|PRD|wireframe|tech_design|code|test_plan|test_result|adr),
               path|inline, version, produced_by(role), created_at
HumanRequest   id, ticket_id, question, options_json|null, status(open|answered),
               answer, answered_at
Lesson         id, project_id|global, role, ticket_type, context, what_happened, lesson,
               score, source_ticket_id, created_at      (self-improvement)
Run            id, project_id, status(running|paused|done), stop_reason, started_at, ...
```

`lane ∈ {plan, human_needed, processing, testing, done}`.
`role ∈ {ba, designer, tech_lead, developer, qe, pm}`.
`ticket.type ∈ {requirement, design, tech_design, implementation, test, bug, chore, decision}`.

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

## 5. Memory design (agentmemory sidecar + our scoping)

- **Consume rohitg00/agentmemory over REST** (`POST /agentmemory/remember`, `/smart-search`,
  `/observe`, `session/start`, `graph/query`). A thin Python `MemoryClient` wraps it.
- **Tiers (native)**: working (raw ticket activity) → episodic (ticket summary on close) →
  semantic (project facts/specs) → procedural (workflows/decisions). Decay + strengthening native.
- **Scoping we add on top**:
  - native: `projectId`, `agentId` (= role), shared/isolated visibility.
  - **add `ticketId`** as a first-class metadata/facet dimension (`ticket:LUB-123`) so retrieval
    can filter per ticket.
  - **role-permission matrix**: e.g. PM/TL read all; Dev writes its own tier; semantic/procedural
    are team-visible, working memory is mostly role-private. Enforced in `MemoryClient`.
- **Consolidation trigger**: on ticket close, collapse its working memory into one episodic
  summary (artifact + decision + outcome). On project milestones, promote recurring facts to
  semantic.
- **Retrieval**: every agent run starts by `smart_search` over (project_id [+ ticket_id] [+ role])
  to assemble context; hybrid RRF (keyword + vector + graph) is provided by the sidecar.
- **Fallback**: if the sidecar is unavailable, degrade to a minimal Postgres-backed
  `MemoryClient` (vector via pgvector) so the platform still runs. (Interface-first.)

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

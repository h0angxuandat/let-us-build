# PRD — let-us-build

> Status: DRAFT for review · Owner: user (dat.xhoang) · Date: 2026-06-30
> Scope of this document: product requirements for the MVP and the north-star vision. Technical
> design lives in `document/system-design.md`.

## 1. One-liner
An **AI software company in a box**: run a CLI, open a web UI, describe the product you want, and a
team of role-based AI agents (BA, Designer, Tech Lead, Dev, QE, PM) builds it end-to-end — tracked
live on a 4-lane Kanban board, with shared memory and agents that improve over time.

## 2. Problem & motivation
Building software still requires assembling and coordinating a human team across the SDLC. Existing
"AI coding" tools focus on a single dev-assistant loop. **let-us-build** instead models the *whole
team* as collaborating agents that move tickets through a real SDLC, pausing only when a human
decision is genuinely required. The user acts as product sponsor, not project manager.

## 3. Goals / Non-goals
### Goals (MVP)
- G1. Local-first: one CLI command boots the entire platform (`let-us-build start`).
- G2. Project creation + requirement intake via web UI (text, design refs, file attachments).
- G3. A working agent team that takes a requirement and produces tickets, then executes them
      through the SDLC into running code in a project workspace.
- G4. Live Kanban (4 lanes) reflecting real ticket state, updated in realtime.
- G5. Per-agent configurable LLM provider + model + role skills.
- G6. Inter-agent discussion to resolve per-ticket decisions, with the transcript visible.
- G7. Shared, retrievable memory across agents, scoped per project/ticket.
- G8. Human-in-the-loop: agents route a ticket to `human needed` and resume after the user answers.
- G9. Run reaches a stable stop when every ticket is `done` or `human needed`.

### Goals (north-star, post-MVP)
- N1. Self-improvement loop: agents accumulate lessons and measurably improve over time.
- N2. Multi-project, multi-tenant, remote/hosted deployment.
- N3. Git/PR integration so the agent team ships PRs into a real repo.
- N4. Pluggable agent roster (add custom roles/skills).

### Non-goals (MVP)
- Not a hosted SaaS yet (local-first first).
- Not fine-tuning models (self-improvement is prompt/skill/lesson-based, not weight updates).
- Not a replacement for human final review on production-bound code.

## 4. Personas
- **Solo founder / PM (primary)** — has a product idea, limited eng capacity; wants a team to build it.
- **Developer / tech lead (power user)** — wants to configure agents/models, inspect decisions,
  and intervene on `human needed` tickets.
- **Operator (self-host)** — runs the CLI, manages provider API keys and resource limits.

## 5. Core user flow
1. User runs `let-us-build start` → core + web UI come up; browser opens to the dashboard.
2. User **creates a project** (name, description, target platform, constraints).
3. User **provides requirements**: free-text brief, design references/links, uploaded files (PRD,
   PSD, screenshots, API specs).
4. User clicks **Start project**.
5. **PM agent** + **BA agent** turn the brief into an initial backlog of tickets in the `plan` lane.
6. Agents **auto-pick** tickets from `plan` per SDLC ordering and dependencies; tickets move
   `plan → processing → testing → done`, or to `human needed` when blocked on a human decision.
7. User can **add tickets to `plan` anytime**; agents pick them up automatically.
8. User watches progress on the **Kanban**, opens any ticket to read the agent **discussion**,
   artifacts, and produced code/diffs.
9. When a ticket lands in **`human needed`**, the user answers; the agent resumes.
10. Run is **done/paused** when all tickets are `done` or `human needed`.

## 6. Functional requirements
### 6.1 CLI
- FR-CLI-1: `let-us-build start` boots API/orchestrator + web, with health checks.
- FR-CLI-2: `let-us-build init` scaffolds config (provider keys, default models).
- FR-CLI-3: `--port`, `--no-open`, `--config <path>` flags. Graceful shutdown.

### 6.2 Web UI (SolidJS)
- FR-WEB-1: Dashboard listing projects; create-project form.
- FR-WEB-2: Requirement intake (rich text + file upload + links), attached to a project.
- FR-WEB-3: Kanban board, 4 lanes (`plan | human needed | processing | testing | done`), realtime.
- FR-WEB-4: Manual ticket creation into `plan`; drag is allowed only where the engine permits.
- FR-WEB-5: Ticket detail: description, status history, assigned agent(s), discussion transcript,
  artifacts, produced code/diff, and (for `human needed`) an answer box.
- FR-WEB-6: Agent settings: per-agent provider/model/skills/enabled toggle.
- FR-WEB-7: Live activity/log stream of agent actions.

### 6.3 Agents
- FR-AGT-1: Six roles ship by default: BA, UI/UX Designer, Technical Lead, Developer, QE, PM.
- FR-AGT-2: Each agent has independent config: provider, model, temperature, system prompt,
  role-specific skill set, enabled flag.
- FR-AGT-3: Agents can hold a bounded multi-turn **discussion** to decide a ticket; output is a
  decision + rationale persisted to the ticket and to memory.
- FR-AGT-4: Agents read/write shared **memory** (retrieval-augmented) scoped by project + ticket.
- FR-AGT-5: Agents emit structured **artifacts** (BRD, PRD, wireframe spec, tech design, code,
  test plan, test results).

### 6.4 Orchestration / SDLC (Agile + DDD)
- FR-ORC-0: The team works **Agile/iteratively**: Epics → User Stories → Tasks, planned into
  **Sprints**, delivered as increments, re-planned each sprint; ceremonies are agent activities
  and the retrospective feeds the self-improvement loop. Sprint length = configurable work-batch.
- FR-ORC-0b: The team applies **DDD**: BA owns the ubiquitous language; TL defines bounded
  contexts + context map + tactical domain model (aggregates/entities/VOs/domain events); each
  implementation ticket is tied to a `bounded_context` + `aggregate` so generated code tracks the
  business domain. (Applies to the product built AND to this platform's own architecture.)
- FR-ORC-1: PM agent owns ticket lifecycle, sprints, and lane transitions.
- FR-ORC-2: Dependency-driven flow (see system-design): inception (requirements + DDD strategic)
  then per-sprint Design/Tech-design → Implement → Test → Review → Done, with `depends_on`
  enforced (independent stories run in parallel).
- FR-ORC-3: Auto-pick: idle agents claim eligible `plan` tickets matching their role.
- FR-ORC-4: Any agent can move a ticket to `human needed` with a specific question; the run does
  not block other independent tickets.
- FR-ORC-5: Durable state — orchestration survives restart (pause/resume).
- FR-ORC-6: Stop condition — all tickets in `done` or `human needed`.

### 6.5 Memory
- FR-MEM-1: Store episodic (events/decisions) + semantic (facts/specs) memory with embeddings.
- FR-MEM-2: Retrieval by similarity + metadata filters (project_id, ticket_id, agent_role, type).
- FR-MEM-3: Memory is shared across agents within a project; ticket-scoped where relevant.

### 6.6 Self-improvement (north-star, scaffolded in MVP)
- FR-SIA-1: After ticket completion/test outcome, capture a **lesson** (what worked / failed / fix).
- FR-SIA-2: Lessons are retrieved into future tickets of the same role/type (reflexion-style).
- FR-SIA-3: An evaluation signal (tests pass/fail, QE score, human accept/reject) feeds the loop.

## 7. Success metrics
- Time-to-first-ticket after "Start project" (target: < 60s).
- % of tickets completed without `human needed` (higher over time = self-improvement working).
- QE pass rate on first attempt; trend upward across a project's life.
- A non-technical user can take a one-paragraph brief to a running artifact without editing code.

## 8. Definition of done / pause (LOCKED)
A project run is **DONE/PAUSED** when **every ticket is in `done` or `human needed`**. If any ticket
sits in `human needed`, the run is *paused* awaiting the user; once answered, agents resume until
the condition holds again with all tickets in `done`.

## 9. Open questions (resolve at review)
- OQ1: Confirm SolidJS (vs React) for web.
- OQ2: How does the agent team actually produce/persist *code* in MVP — write into a workspace
  folder only, or also git-commit/PR? (Recommend: workspace folder in MVP, git/PR post-MVP.)
- OQ3: Which LLM providers must MVP support day one (Anthropic only, or Anthropic+OpenAI+local)?
- OQ4: Sandbox for running/testing generated code (local subprocess vs Docker per project)?
- OQ5: Single-user local MVP, or multi-user auth from the start? (Recommend: single-user local.)

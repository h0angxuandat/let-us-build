# Agent Roster & SDLC Flow — let-us-build

> Status: DRAFT for review · Date: 2026-07-01 · Companion to `system-design.md`.
> Defines the six agents, their skills, the **Agile** SDLC, the ticket lifecycle across the
> 4 lanes, auto-pick rules, discussion protocol, and the done/pause condition.

## 0. Methodology (LOCKED)
- **Agile / iterative.** Work is organized as **Epics → User Stories → Tasks**, planned into
  **Sprints (iterations)**, delivered as working increments, and re-planned each sprint. The 4-lane
  board is the **sprint board**. Agent ceremonies replace human ones (§10). Retrospective output
  feeds the self-improvement lessons loop (see `system-design.md` §6).
- **Domain-Driven Design (DDD).** Agents model the **business domain** first and keep the design +
  code tied to it. This applies to BOTH:
  1. **the product being built** — BA owns the *ubiquitous language*; TL defines *bounded contexts*,
     a *context map*, and the *tactical model* (aggregates, entities, value objects, domain events,
     repositories, domain services); Dev implements per-aggregate.
  2. **this platform itself** — our own packages are organized as bounded contexts (see
     `system-design.md` §3.1).
  DDD artifacts are first-class (glossary, context map, domain model) and are stored in memory's
  semantic tier so every agent shares one vocabulary.

## 1. The four lanes (board contract)

| Lane | Meaning | Who moves tickets in |
|---|---|---|
| **plan** | Backlog of work not yet started. Dependencies may be unmet. | PM/BA (auto) + the **user** (manual add). |
| **processing** | An agent has claimed the ticket and is actively working it. | Scheduler (auto-pick) / the working agent. |
| **testing** | Work produced; QE is verifying it (tests, review, a11y, etc.). | Working agent → QE. |
| **human needed** | Blocked on a human decision/input. Run pauses for this ticket. | Any agent via `interrupt()`. |
| **done** | Verified complete. | QE / PM after acceptance. |

Lane is **derived** from `sdlc_stage` + block state; the UI may allow manual drag only where the
engine permits (e.g. user can add to `plan`; user cannot drag `processing → done`).

## 2. The six agents

Each agent has independent config: `provider`, `model`, `temperature`, `system_prompt`,
`skill_ids[]`, `enabled`. Skills are reusable expert prompt/tool bundles (see §6).

| Role | Mandate | Primary inputs | Primary outputs (artifacts) | Default model tier |
|---|---|---|---|---|
| **Project Manager (PM)** | Product-owner + scrum-master: owns backlog + sprints; refines/prioritizes; runs planning/review/retro; enforces DoD + stop condition; chairs decisions. | Project + requirements; all artifacts. | Product backlog, sprint plan, increment/retro notes, status. | strong |
| **Business Analyst (BA)** | Elicits & documents requirements; writes **epics + user stories** + acceptance criteria; owns the **ubiquitous language** glossary; clarifies ambiguity (→ human_needed). | Requirement intake. | BRD, epics/user stories, acceptance criteria, **ubiquitous-language glossary**. | mid |
| **UI/UX Designer** | Wireframes, design system spec, UX flows; a11y direction. | BRD/PRD, stories, design refs. | Wireframe spec, design tokens, UX flow. | mid |
| **Technical Lead (TL)** | System analysis + **DDD**: defines **bounded contexts + context map** and the **tactical domain model** (aggregates, entities, value objects, domain events); tech design, ADRs; breaks stories into per-aggregate tasks; chairs technical debates. | BRD/PRD, stories, glossary, design specs. | **Context map, domain model (DDD)**, tech design doc, ADRs, impl task graph. | strong |
| **Developer (Dev)** | Implements a task per the domain model (one aggregate/slice); writes unit tests; uses ubiquitous language in code. | Domain model, tech design, one task. | Code (workspace diff), unit tests. | strong |
| **QE Engineer** | Test plan + cases from acceptance criteria; runs tests in sandbox; cross-artifact review; **sprint-review/demo** acceptance. | All artifacts, produced code, acceptance criteria. | Test plan, test results, review report. | mid |

> Roster is pluggable post-MVP (custom roles/skills). MVP ships these six, all toggle-able.

## 3. Agile SDLC (iterative, DDD-driven)

Instead of a single waterfall pass, the team works in **sprints** over a **product backlog**. Each
sprint delivers a working, tested increment; the backlog is re-refined afterward. Within a sprint,
work is still **dependency-driven** (not phase-locked) so independent stories run in parallel.

### 3.1 Inception (sprint 0 — done once per project, refined continually)
```
 Requirement intake
        │
        ▼
 BA: elicit → epics + user stories + acceptance criteria + UBIQUITOUS LANGUAGE glossary
        │
        ▼
 TL: DDD strategic design → BOUNDED CONTEXTS + CONTEXT MAP  (which contexts, how they relate)
        │
        ▼
 PM: shape product backlog (epics/stories) + first sprint plan
```

### 3.2 Per-sprint loop (repeats until backlog empty / user stops)
```
 Sprint planning (PM+TL)   select stories for the sprint, slice into tasks by aggregate
        │
        ▼
 ┌──────────────┐   ┌───────────────────────────────┐
 │ Design (UX)  │   │ TL: DDD tactical model         │   (parallel where independent)
 │ per story    │   │ aggregates/VOs/domain events   │
 └──────┬───────┘   └───────────────┬───────────────┘
        └───────────────┬───────────┘
                        ▼
             Dev: implement task (one aggregate/slice) + unit tests
                        │
                        ▼
                  QE: test in sandbox  ──fail──▶ bug story → backlog ──┐
                        │ pass                                          │
                        ▼                                               │
              Sprint review/demo (QE+PM) vs acceptance criteria         │
                        │ accepted                                      │
                        ▼                                               │
                  Story Done ◀──────────────────────────────────────────┘ (re-test on fix)
                        │
                        ▼
              Retrospective (PM+all) → LESSONS → self-improvement loop + backlog re-refine
```

- **PM** seeds inception then, each sprint, selects backlog items and runs the ceremonies (§10).
- **TL** does DDD strategic design once (contexts/map) and tactical design per story
  (aggregates), then slices stories into per-aggregate implementation tasks.
- Dependencies (`depends_on`) gate auto-pick so ordering is respected without a rigid phase lock;
  an increment is only "done" when its stories pass QE against acceptance criteria.
- The **retrospective** is not decorative: its output is written as **Lessons** (see
  `system-design.md` §6) — Agile's retro and sia's feedback loop are the same mechanism here.

## 4. Ticket lifecycle (state machine)

```
        (created in) plan
              │  deps satisfied + matching idle agent
              ▼
         processing ───────────────┐ agent needs human decision
              │ work produced        ▼
              ▼                  human needed ──(user answers)──▶ (resume previous lane)
           testing
        ┌─────┴─────┐
     pass│           │fail
        ▼            ▼
       done     (spawn bug ticket → plan, linked) 
```

- Any lane → **human needed** via `interrupt(HumanRequest)`; on answer, returns to the lane it
  left. The run pauses only with respect to *that* ticket.
- **testing fail** spawns a linked bug ticket back into `plan` (Dev re-picks); avoids infinite
  ping-pong via a per-ticket max-retry, after which it routes to `human needed`.

## 5. Auto-pick rules (scheduler)
1. Scan `plan` for tickets where all `depends_on` are `done`.
2. For each eligible ticket, find the agent whose role matches `ticket.type`/`sdlc_stage` and is
   `enabled` and under its concurrency limit.
3. Claim → move to `processing` → dispatch to the LangGraph thread for that stage.
4. User-added `plan` tickets are picked the same way (no special path).
5. Global concurrency + per-provider rate caps bound parallelism (cost control).

## 6. Skills (per-role expert bundles)
Skills are versioned prompt/checklist/tool packs attached to a role. Examples:
- BA: `requirements-elicitation`, `user-story-writing`, `acceptance-criteria`,
  `ubiquitous-language` (DDD), `event-storming` (DDD discovery).
- Designer: `wireframing`, `design-tokens`, `a11y-wcag`, `ux-flow`.
- TL: `ddd-strategic` (bounded contexts + context map), `ddd-tactical` (aggregates/entities/VOs/
  domain events/repositories), `system-design`, `adr-authoring`, `task-decomposition`, `api-design`.
- Dev: `tdd`, `ddd-implementation` (aggregate/repository patterns), `code-implementation`,
  `refactoring`, stack-specific packs.
- QE: `test-planning`, `test-case-design`, `cross-artifact-review`, `e2e`, `sprint-review`.
- PM: `agile-backlog` (epics/stories/refinement), `sprint-planning`, `dependency-mapping`,
  `retrospective`, `decision-chairing`.

Skills feed the agent's system prompt + available tools. Self-improvement (sia harness lever)
updates these skill packs and accumulates **lessons** that are retrieved alongside them.

## 7. Discussion protocol (per-ticket decisions)
Full mechanism in `agent-discussion-protocol.md`; UX for watching it in `../design/ui-ux-spec.md` §5.
In short:
- Triggered only for **multi-role decisions** (e.g. TL+Dev+QE on an approach, BA+Designer on a UX
  trade-off) — not routine work.
- A **shared append-only transcript** ("blackboard"); each turn = one agent reads the transcript +
  its memory/glossary and appends a message. Runs inside a durable LangGraph subgraph.
- **Chair by ticket type** (D13): business/product → PM, technical → TL. Chair picks next speaker,
  judges convergence, and writes a **structured Decision** (decision + rationale + alternatives +
  dissent + follow-ups).
- Bounded (max-turns + budget). No convergence → escalate to `human needed` with a crisp question.
- Decision + transcript persisted to the ticket and to memory (procedural tier) as precedent.

## 8. Human-in-the-loop contract
- A `HumanRequest` carries: `ticket_id`, a specific `question`, optional `options[]`, and the
  context needed to answer. Surfaced in the ticket detail with an answer box.
- On answer, the LangGraph thread resumes from the exact interrupt point. The answer is recorded
  as a `TicketEvent` and added to memory.

## 9. Definition of done / pause (LOCKED, restated)
- **Story DoD**: code implemented + unit tests pass + QE tests pass in sandbox + accepted at
  sprint review against acceptance criteria + ubiquitous language honored in code.
- **Sprint DoD**: all committed stories meet Story DoD; increment demoed; retrospective produced
  (→ Lessons).
- A **Run** is **DONE** when **all tickets are `done`** (backlog empty, all sprints complete).
- A **Run** is **PAUSED** when **all tickets are `done` or `human needed`** and at least one is
  `human needed`. Answering re-activates the scheduler; the cycle repeats until all are `done`.
- No ticket may sit in `plan`/`processing`/`testing` for the run to be considered done/paused.

## 10. Agile ceremonies (agent-run)
Ceremonies are automated agent activities, not calendar meetings. Sprint length is a **work-batch**
(configurable N stories / token budget), not wall-clock time.

| Ceremony | Driven by | What happens | Output |
|---|---|---|---|
| Backlog refinement | BA + PM | Clarify/split stories, estimate, order; keep glossary current. | Groomed backlog |
| Sprint planning | PM + TL | Select stories into the sprint; TL slices into per-aggregate tasks. | Sprint scope + tasks |
| Standup (tick) | PM (scheduler) | Reconcile board, unblock, reassign; emit status event to UI. | `run.status` events |
| Sprint review / demo | QE + PM | Verify increment vs acceptance criteria; user may inspect/accept. | Accepted increment |
| Retrospective | PM + all | What worked / failed / fix per role. | **Lessons** → self-improve loop |

- Any ceremony can escalate to `human needed` (e.g. story too ambiguous to refine, or user
  acceptance required at review).
- The retrospective is the bridge to `system-design.md` §6: its per-role findings ARE the lessons
  the harness-lever self-improvement consumes.

# Agent Roster & SDLC Flow — let-us-build

> Status: DRAFT for review · Date: 2026-06-30 · Companion to `system-design.md`.
> Defines the six agents, their skills, the SDLC ordering, the ticket lifecycle across the
> 4 lanes, auto-pick rules, discussion protocol, and the done/pause condition.

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
| **Project Manager (PM)** | Owns the board; decomposes the brief into tickets; sets dependencies/priority; enforces stop condition; chairs decisions. | Project + requirements; all artifacts. | Backlog (tickets), milestone plan, status. | strong |
| **Business Analyst (BA)** | Elicits & documents requirements; writes BRD + user stories; clarifies ambiguity (→ human_needed). | Requirement intake. | BRD, user stories, acceptance criteria. | mid |
| **UI/UX Designer** | Wireframes, design system spec, UX flows; a11y direction. | BRD/PRD, design refs. | Wireframe spec, design tokens, UX flow. | mid |
| **Technical Lead (TL)** | System analysis, tech design, ADRs, task breakdown into implementation tickets; chairs technical debates. | BRD/PRD, design specs. | Tech design doc, ADRs, impl task graph. | strong |
| **Developer (Dev)** | Implements an implementation ticket in the workspace; writes unit tests. | Tech design, one impl ticket. | Code (workspace diff), unit tests. | strong |
| **QE Engineer** | Test plan + test cases; runs tests in sandbox; reviews artifacts cross-cutting; accepts/rejects. | All artifacts, produced code. | Test plan, test results, review report. | mid |

> Roster is pluggable post-MVP (custom roles/skills). MVP ships these six, all toggle-able.

## 3. SDLC ordering (the work sequence agents follow)

Reference: classic SDLC (Requirements → Design → Architecture/Tech-design → Implementation →
Testing → Done), adapted to tickets and made dependency-driven rather than strictly phased so
independent tickets run in parallel.

```
 Requirements (BA)
        │  produces user stories → spawns design + tech-design tickets
        ▼
 ┌──────────────┐        ┌─────────────────────┐
 │ Design (UX)  │        │ Tech design (TL)    │   (can run in parallel)
 └──────┬───────┘        └─────────┬───────────┘
        └──────────────┬───────────┘
                       ▼
            Implementation (Dev)   ← TL breaks tech design into impl tickets
                       │
                       ▼
                 Testing (QE)  ──fail──▶ Bug ticket (Dev)  ──┐
                       │ pass                                 │
                       ▼                                      │
                     Done ◀───────────────────────────────────┘ (re-test on fix)
```

- The **PM** seeds the initial `plan` tickets (often a single "Requirements" ticket for the BA,
  which then spawns the rest). The **TL** explodes tech design into implementation tickets with a
  dependency graph. Dependencies (`depends_on`) gate auto-pick so ordering is respected without a
  rigid global phase lock.

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
- BA: `requirements-elicitation`, `user-story-writing`, `acceptance-criteria`.
- Designer: `wireframing`, `design-tokens`, `a11y-wcag`, `ux-flow`.
- TL: `system-design`, `adr-authoring`, `task-decomposition`, `api-design`.
- Dev: `tdd`, `code-implementation`, `refactoring`, stack-specific packs.
- QE: `test-planning`, `test-case-design`, `cross-artifact-review`, `e2e`.
- PM: `backlog-decomposition`, `dependency-mapping`, `decision-chairing`.

Skills feed the agent's system prompt + available tools. Self-improvement (sia harness lever)
updates these skill packs and accumulates **lessons** that are retrieved alongside them.

## 7. Discussion protocol (per-ticket decisions)
- Triggered when a ticket needs a cross-role decision (e.g. TL+Dev+QE on an approach, or
  BA+Designer on a UX trade-off).
- Bounded multi-turn exchange (max-turns cap) among the relevant roles; a **chair** (PM or TL)
  summarizes to `decision + rationale`.
- The decision + transcript are persisted to the ticket (`Discussion`/`Message`) and to memory
  (procedural tier) so future tickets retrieve precedent.
- If the group cannot converge within the cap, the chair escalates the ticket to `human needed`
  with a crisp question + options.

## 8. Human-in-the-loop contract
- A `HumanRequest` carries: `ticket_id`, a specific `question`, optional `options[]`, and the
  context needed to answer. Surfaced in the ticket detail with an answer box.
- On answer, the LangGraph thread resumes from the exact interrupt point. The answer is recorded
  as a `TicketEvent` and added to memory.

## 9. Definition of done / pause (LOCKED, restated)
- A **Run** is **DONE** when **all tickets are `done`**.
- A **Run** is **PAUSED** when **all tickets are `done` or `human needed`** and at least one is
  `human needed`. Answering re-activates the scheduler; the cycle repeats until all are `done`.
- No ticket may sit in `plan`/`processing`/`testing` for the run to be considered done/paused.

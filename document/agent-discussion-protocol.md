# Agent Discussion Protocol — let-us-build

> Status: DRAFT for review · Date: 2026-07-01 · Companion to `system-design.md` (§4) and
> `agent-sdlc-flow.md` (§7). Defines how agents talk to and discuss with each other to make
> per-ticket decisions. UX for watching discussions is in `../design/ui-ux-spec.md` §5.

## 1. Model: a shared "blackboard", not real-time chat
Agents do not stream tokens at each other. Each agent is an independent LLM call (own
provider/model/system-prompt). The shared state is an **append-only transcript** (`Message[]`) — a
blackboard. One **turn** = build one agent's context (its role prompt + skills + recalled memory +
the ticket + the transcript so far) → call its LLM → append its message. Repeat. "Agent A talks to
agent B" means B reads A's message in the transcript on a later turn. This is the GroupChat pattern,
run **inside a LangGraph subgraph** so every turn is checkpointed and the discussion is durable and
resumable.

## 2. Where it runs
A `discussion` subgraph nested in the per-ticket LangGraph graph:
```
per-ticket graph
  … → node: needs_decision? ──yes──▶ [ discussion subgraph ] ──▶ Decision ──▶ continue ticket
```
Because it's LangGraph, an `interrupt()` mid-discussion pauses to the user (ticket → `human_needed`)
and resumes at the exact turn after they answer. Survives process restart.

## 3. Trigger
Discussions are expensive, so they run only for **multi-role decisions**, not routine work. An agent
(or the orchestrator, for a `decision`-type ticket) emits:
```json
{ "topic": "How to store the cart",
  "participants": ["tech_lead", "developer", "qe"],
  "chair": "tech_lead",
  "question": "Event-sourced vs snapshot state for the cart aggregate?",
  "context_refs": ["ticket:LUB-142", "artifact:domain_model#Cart"] }
```

## 4. Chair (moderator) — default by ticket type (LOCKED, D13)
The chair selects the next speaker, judges convergence, and writes the final decision.
- **Business/product ticket** (requirement, UX, scope) → chair = **PM**.
- **Technical ticket** (tech_design, implementation, architecture) → chair = **Tech Lead**.
- Overridable per-discussion via the `chair` field; falls back to PM if unset.

## 5. The loop (bounded)
```python
def run_discussion(spec, ticket):
    transcript = []
    for turn in range(MAX_TURNS):                        # hard cap, e.g. 8
        speaker = chair_select_next(spec.chair, transcript, spec.participants)
        ctx = build_context(speaker,
            system   = role_prompt(speaker) + skills(speaker),
            memory   = memory.recall(ticket.project, ticket.id, role=speaker),  # precedent + glossary
            ticket   = ticket,
            question = spec.question,
            transcript = transcript)
        msg = llm(speaker).invoke(ctx)
        transcript.append(Message(role=speaker, content=msg))
        emit_ws("discussion.message", msg)               # live to UI
        if chair_converged(spec.chair, transcript):      # consensus reached?
            break
        if budget_exceeded(ticket): break
    if not converged:                                    # no consensus in budget
        return escalate_to_human(spec, transcript)       # interrupt() → human_needed
    return chair_summarize(spec.chair, transcript)       # structured Decision
```

## 6. Speaker-selection modes
| Mode | How | When |
|---|---|---|
| **Chair-directed** (default) | Chair picks the next speaker based on the open question, and decides when converged | Normal decisions |
| Round-robin | Cycle participants in order | Simple / fallback |
| **Adversarial (debate)** | One agent proposes, another must critique/refute, chair adjudicates | High-stakes decisions — forces diverse perspectives, guards against false consensus |

## 7. Termination & escalation
Bounded to avoid infinite/expensive loops:
- **Max turns** (e.g. 8) · **token/cost budget cap** · **chair detects convergence**.
- If not converged within budget → **escalate to `human needed`**: the chair packages a crisp
  question + the alternatives debated for the user (`human.requested` event; `interrupt()`).

## 8. Output: a structured Decision (schema-validated)
The chair returns structured output, not prose (retried on schema mismatch):
```json
{ "decision": "Use snapshot state for the MVP.",
  "rationale": "Fastest to ship; low risk for the current scope.",
  "alternatives_considered": ["Event-sourced cart (rejected: 3-day effort, needs a library)"],
  "dissent": "QE: change-history will be harder to test.",
  "follow_up_tickets": [{ "title": "Spike event-sourcing for cart", "type": "spike" }] }
```
Persisted to `Discussion` + `Message` (full transcript), attached to the ticket (`decision` +
`rationale`), and written to **memory (procedural tier)** so future tickets `recall()` the precedent
instead of re-litigating it. Follow-up tickets are created in `plan`.

## 9. Memory integration
- **Before** speaking, each agent recalls relevant memory: prior decisions on the topic, the
  **ubiquitous-language glossary** (so everyone uses the same terms), project facts.
- **After** the decision, it's consolidated into procedural memory as reusable precedent.

## 10. Observability & realtime
Every message streams to the web UI (`discussion.message`); progress via `discussion.turn`;
start/end via `discussion.started` / `discussion.decided`. The user watches live and reads the
pinned Decision (see `../design/ui-ux-spec.md` §5).

## 11. Cost & safety controls
- Only invoke a discussion for genuine multi-role decisions (routine work = single agent, no meeting).
- Participants may use cheaper models; the **chair uses a stronger model** (adjudication + summary).
- Max-turns + budget cap per discussion; global cap on concurrent discussions.
- Adversarial mode for high-stakes items provides a Goodhart/false-consensus guard (ties into the
  self-improvement cross-role review, `system-design.md` §6).

## 12. Concurrency
Each ticket's discussion is its own subgraph thread — many discussions run in parallel across
tickets. Within a single discussion, turns are sequential (each builds on the transcript).

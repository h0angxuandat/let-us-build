# UI/UX Spec — let-us-build

> Status: DRAFT for review · Date: 2026-07-01 · Companion to `../document/agent-sdlc-flow.md`
> and `../document/agent-discussion-protocol.md`.
> Guiding directive (from user): the UI must be **simple, easy to understand, easy to use, and
> accessible**. Everything below is subordinate to that.

## 1. Design principles (LOCKED — see solid SR-10)
1. **Simple** — few screens, shallow navigation, one primary action per screen. No feature until a
   real need exists (YAGNI). Progressive disclosure: advanced options are hidden until asked for.
2. **Easy to understand** — plain language (no jargon in the UI; "Needs you" not "HITL interrupt").
   Every state is self-explanatory: what happened, why, what to do next.
3. **Easy to use** — the happy path is obvious and reachable in the fewest clicks. Sensible
   defaults everywhere; the user should be able to start a project without configuring anything.
4. **Accessible** — WCAG 2.2 AA is a hard requirement, not a nice-to-have (see §7). Keyboard-first,
   screen-reader friendly, high contrast, respects reduced-motion. **Never rely on color alone.**

> Anti-template note (web rules): calm, restrained, opinionated productivity aesthetic — clean is
> the point here, but not a generic dashboard-by-numbers. Hierarchy through scale + spacing, one
> accent color, real empty/loading/error states.

## 2. Visual direction & tokens
- **Theme**: light default, calm and neutral; dark mode is post-MVP (don't auto-default to dark).
- **Palette**: neutral surfaces + a single accent for primary actions; **semantic** status colors
  paired ALWAYS with an icon + text label (a11y). Lane colors are cues, never the sole signal.
- **Type**: one readable sans for UI + one mono for code/diffs. Strong size contrast for hierarchy.
- **Motion**: subtle, `transform`/`opacity` only; **disabled under `prefers-reduced-motion`**.
- Tokens live in `apps/web/src/styles/tokens.css` (CSS custom properties — color/space/type/motion).

Role identity (color + icon + short label, used consistently everywhere an agent appears):
`PM ◆` · `BA ✎` · `Designer ✍` · `Tech Lead ⌘` · `Dev ⌥` · `QE ✓`. Colors chosen for AA contrast;
the icon+label carry the meaning so colorblind users lose nothing.

## 3. Information architecture (shallow on purpose)
```
Dashboard (projects)
├── + New project            (short wizard, 3 steps)
└── Project
    ├── Board                 (the 4-lane Kanban — the home of a project)
    │   └── Ticket detail     (drawer/side-panel: Overview · Discussion · Artifacts · Diff · History)
    ├── Requirements          (intake: text + files + links)
    ├── Activity              (live feed of what agents are doing)
    └── Agents                (per-agent settings — advanced, tucked away)
```
Two clicks from anywhere to the board. No deep trees.

## 4. Screen-by-screen (with the "easy" affordances)

### 4.1 Dashboard
List of projects as calm cards: name, one-line status ("3 tickets need you", "Sprint 2 · 60%"),
last activity. One primary button: **New project**. Empty state = a friendly single CTA + one line
explaining what the app does.

### 4.2 New project (3-step wizard, not a wall of fields)
`Name & goal` → `What to build` (the brief; can paste, upload, or link) → `Review & Start`.
Everything optional except name + brief. Agent/model config is NOT here (uses good defaults) — a
"Advanced" link for power users. One primary button per step; Back always available.

### 4.3 Requirements intake
A single, forgiving input: rich text + drag-drop files + paste links, all in one place. Shows what
was attached as removable chips. No format requirements imposed on the user.

### 4.4 Board (the 4 lanes) — the heart
```
┌ Sprint 2 ·  ▓▓▓▓▓░░░ 60% ─────────────────────────── [ + Add ticket ]┐
│  PLAN          NEEDS YOU 🙋    PROCESSING        TESTING     DONE      │
│ ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐   ┌────────┐  │
│ │ LUB-140 │   │ LUB-138  │   │ LUB-142  │   │ LUB-135│   │ LUB-130│  │
│ │ ✎ BA    │   │ 🙋 answer │   │💬 discuss │   │ ✓ QE   │   │ done   │  │
│ └─────────┘   └──────────┘   └──────────┘   └────────┘   └────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```
- **Lanes read left→right as flow.** "Needs you" is visually distinct (not just color — icon +
  label + a subtle count badge on the lane header) so the user instantly sees where they're needed.
- Card shows: key, title, the role currently on it (icon+label), and status badges
  (`💬 discussing`, `🙋 needs you`). Live-updates via WebSocket.
- **User can add a ticket to `plan`** with one button; that's the only drag/create the user does.
  The board explains (empty lane hint) that agents pick up `plan` tickets automatically.

### 4.5 Ticket detail (side drawer, doesn't lose board context)
Tabs: **Overview · Discussion · Artifacts · Diff · History**. Overview = plain-language summary,
current lane, who's on it, acceptance criteria. Discussion = §5. If the ticket **needs you**, a
clear banner + a single answer box appears at the top of Overview (and inside Discussion if that's
where it paused) — the user is never hunting for what to do.

### 4.6 Agents (advanced, tucked away)
Simple list of the 6 agents with on/off toggles and, behind "Configure", the provider/model/skills.
Defaults work out of the box; a non-technical user never has to open this.

## 5. Following agent discussions (the requested feature)
Goal: a non-technical user can **watch agents decide, in plain terms, and step in only when asked.**

### 5.1 Where
Three levels, so the user can follow at whatever depth they want:
- **Board card** → `💬 discussing` badge (icon+label) when a discussion is live.
- **Ticket → Discussion tab** → the full live conversation + the final decision.
- **Activity feed** → project-wide stream: "TL, Dev, QE are discussing LUB-142", "Decision made".

### 5.2 Discussion tab (the main view)
```
┌ Discussion · LUB-142 "How to store the cart"        ● live · turn 5/8 ┐
├────────────────────────────────────────────────────────────────────────┤
│ ⌘ Tech Lead (chair)   Proposes an event-sourced cart…          0:01     │
│ ⌥ Developer           Too complex for the MVP — snapshot…      0:04     │
│ ✓ QE                  Snapshots make change-history hard to…   0:07     │
│ ⌘ Tech Lead (chair)   @Developer how much effort for events?   0:09     │
│ ⌥ Developer           ~3 days, needs a library…                0:12     │
│ ⌘ Tech Lead is summarizing…                                             │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ Decision                                                             │
│ Use snapshots for the MVP; revisit event-sourcing later.                │
│ Why: fastest to ship, low risk.   Not chosen: event-sourcing (why: …)   │
│ One concern noted (QE): harder change-history.  → follow-up: spike       │
└────────────────────────────────────────────────────────────────────────┘
```
- **Reads like a chat.** Each message: role **icon + name + color** (icon+name carry meaning;
  color is decoration), plain content, relative time. Chair clearly marked.
- **Plain-language framing.** A one-line header explains what's being decided. No internal jargon.
- **Live but calm.** Messages appear one at a time; a gentle "…is thinking" indicator. A small
  `turn 5/8` shows progress so it never feels stuck. Motion is minimal / reduced-motion safe.
- **Decision is the hero.** Pinned card in plain words: the decision, why, what wasn't chosen,
  concerns, and follow-up tickets (clickable). A user who only reads this still understands.
- **If it needs the user**: the discussion shows a clear banner "The team needs your input" + one
  question + (optional) suggested options as buttons + a free-text box. Answering resumes it.
- **After it's done**: collapsed by default to the Decision; expand to read the full transcript;
  filter by speaker; jump-to-decision.

### 5.3 States the user sees (no dead ends)
`Not started` · `Live (turn n/N)` · `Needs you` · `Decided` · `Escalated to you`. Each state names
itself and says what happens next.

## 6. Realtime events (web ↔ core, over WebSocket)
`ticket.lane_changed` · `ticket.updated` · `discussion.started` · `discussion.message` ·
`discussion.turn` (typing/progress) · `discussion.decided` · `human.requested` · `agent.activity`
· `run.status`. The client keeps a reactive store; the UI is a pure function of these events.

## 7. Accessibility (WCAG 2.2 AA — hard requirement)
- **Keyboard**: every action reachable and operable by keyboard; visible focus rings; logical tab
  order; the board is navigable with arrow keys; drawers trap focus and close on Esc.
- **Screen readers**: semantic HTML (nav/main/section/headings); ARIA labels on icon-only controls;
  the lane a ticket is in is announced; the Kanban uses an accessible list semantics fallback.
- **Live regions**: incoming discussion messages and "needs you" alerts use polite `aria-live` so
  screen-reader users are informed without being flooded.
- **Contrast**: text ≥ 4.5:1, large text/UI ≥ 3:1. Status/role **never conveyed by color alone** —
  always icon + text.
- **Motion**: honor `prefers-reduced-motion`; provide non-animated equivalents; no motion required
  to understand state.
- **Targets & zoom**: ≥ 24×24px targets; layout works at 200% zoom and 320px width without loss.
- **Forms**: labels tied to inputs, clear inline errors, no reliance on placeholder as label.
- Automated a11y checks + keyboard pass are part of QE for every web ticket.

## 8. Empty / loading / error states (part of "easy to use")
Every screen defines all three: an inviting empty state with one next step; skeletons (not spinners)
while loading; plain-language errors that say what went wrong and how to recover (never a raw stack
trace). A user is never left staring at a blank or a cryptic message.

## 9. What MVP ships vs defers
- **MVP**: dashboard, 3-step new-project wizard, intake, board with live updates + "needs you",
  ticket detail with **Discussion tab + Decision card**, answer box, agent settings (defaults),
  full WCAG 2.2 AA pass, empty/loading/error states.
- **Defer**: dark mode, activity-feed advanced filtering, discussion replay/timeline scrubber,
  multi-user presence.

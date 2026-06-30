# Monorepo Layout — let-us-build

> Status: DRAFT for review · Date: 2026-06-30.
> Documents the intended repo structure. This session produces the LAYOUT (folders + READMEs +
> interface stubs), NOT working logic. Implementation happens in later milestones.

## 1. Top-level

```
let-us-build/
├── README.md                      # what it is, quickstart
├── pyproject.toml                 # uv/poetry workspace for Python packages
├── docker-compose.yml             # postgres(+pgvector) + (dev) services  — no Node sidecar
├── .env.example                   # provider keys, ports, DB url (no secrets committed)
├── Makefile / justfile            # dev tasks: up, migrate, test, lint, web
│
├── apps/
│   ├── cli/                       # `let-us-build` CLI (Python, Typer)
│   │   ├── pyproject.toml
│   │   └── src/let_us_build_cli/
│   │       ├── __main__.py        # entrypoint
│   │       ├── commands/          # init.py, start.py
│   │       └── bootstrap.py       # boot core + web, health checks, open browser
│   │
│   └── web/                       # SolidJS / SolidStart frontend
│       ├── package.json
│       ├── src/
│       │   ├── routes/            # dashboard, project/[id], settings
│       │   ├── components/
│       │   │   ├── kanban/        # Board, Lane, TicketCard (4 lanes)
│       │   │   ├── intake/        # requirement form + uploads
│       │   │   ├── ticket/        # detail, discussion transcript, diff, human-answer box
│       │   │   └── agents/        # per-agent config UI
│       │   ├── lib/
│       │   │   ├── api.ts         # REST client
│       │   │   └── ws.ts          # WebSocket client + event store
│       │   └── styles/            # tokens.css, global.css
│       └── ...
│
├── packages/                      # Python core, split by concern (many small packages)
│   ├── core-api/                  # FastAPI app: REST + WS gateway
│   │   └── src/lub_api/
│   │       ├── main.py            # app factory
│   │       ├── routes/            # projects, tickets, agents, runs, ws
│   │       ├── schemas/           # pydantic request/response models
│   │       └── deps.py
│   │
│   ├── orchestrator/              # LangGraph orchestration
│   │   └── src/lub_orchestrator/
│   │       ├── graph.py           # per-ticket graph definition
│   │       ├── scheduler.py       # auto-pick loop
│   │       ├── lanes.py           # lane state machine + transitions
│   │       ├── discussion.py      # discussion subgraph
│   │       ├── interrupts.py      # HumanRequest / resume
│   │       └── checkpoint.py      # AsyncPostgresSaver wiring
│   │
│   ├── agents/                    # the six role agents
│   │   └── src/lub_agents/
│   │       ├── base.py            # Agent base: config, run(), skill loading
│   │       ├── roles/             # ba.py, designer.py, tech_lead.py, developer.py, qe.py, pm.py
│   │       ├── skills/            # versioned skill packs (prompts/checklists/tools)
│   │       └── registry.py        # role → agent factory
│   │
│   ├── llm/                       # provider abstraction (LiteLLM)
│   │   └── src/lub_llm/
│   │       ├── router.py          # per-agent provider/model routing
│   │       ├── config.py          # AgentLLMConfig
│   │       └── budget.py          # cost/rate caps, fallback
│   │
│   ├── memory/                    # OWN memory subsystem (Python, on Postgres+pgvector)
│   │   └── src/lub_memory/
│   │       ├── client.py          # MemoryClient: remember/recall/consolidate/forget
│   │       ├── records.py         # MemoryRecord model (tiers, scoping, embedding, tsvector)
│   │       ├── scope.py           # project/ticket/role scoping + permission matrix
│   │       ├── retrieval.py       # pgvector similarity (MVP); +tsvector/RRF (phase 2)
│   │       └── consolidate.py     # ticket-close → episodic; milestone → semantic/procedural
│   │
│   ├── improvement/               # sia-inspired self-improvement (harness lever)
│   │   └── src/lub_improvement/
│   │       ├── feedback.py        # read trajectory + score → Lesson
│   │       ├── verifiers/         # per-role verifier definitions
│   │       ├── lessons.py         # store/retrieve lessons
│   │       └── weights.py         # (stub) future LoRA lever, behind interface
│   │
│   ├── workspace/                 # generated-code workspace + sandbox
│   │   └── src/lub_workspace/
│   │       ├── manager.py         # ./workspaces/<project> lifecycle
│   │       └── sandbox.py         # Docker-per-project / subprocess test runner
│   │
│   └── store/                     # persistence
│       └── src/lub_store/
│           ├── models.py          # SQLAlchemy models (domain model)
│           ├── migrations/        # alembic
│           └── repositories/      # repository-pattern data access
│
├── workspaces/                    # (gitignored) generated projects live here at runtime
├── docs/                          # generated/internal docs (mirrors product/ + document/)
└── tests/                         # cross-package integration + e2e
```

## 2. Package boundaries (dependency direction)
```
cli ─▶ core-api ─▶ orchestrator ─▶ agents ─▶ {llm, memory, improvement, workspace}
                         └─▶ store (all persist through repositories)
web ─▶ (HTTP/WS) ─▶ core-api
```
- `store` is the only package that talks to Postgres; everything else goes through repositories.
- `llm` is the only package that talks to LLM providers (via LiteLLM).
- `memory` owns the memory subsystem; it persists through `store`/pgvector like everything else.
- Agents depend on capabilities (llm/memory/...) via injected interfaces — testable, swappable.

## 3. Conventions
- Python: `ruff` + `mypy` + `pytest`; repository pattern; immutable DTOs (pydantic) at boundaries;
  files ≤ 800 lines; functions ≤ 50 lines.
- Web: SolidJS components by feature; CSS custom-property tokens; WebSocket events into a reactive
  store; no business logic in components.
- Config: all secrets via env (`.env`, never committed); `init` scaffolds `.env` from
  `.env.example`.
- Tests: unit per package + integration (API+DB) + e2e (a tiny demo project run end-to-end).

## 4. What this session delivers vs. defers
- **This session**: this layout document. (Optionally, on your go-ahead, the empty folder
  skeleton + READMEs + interface stubs — no logic.)
- **Deferred to implementation milestones** (see `backlog.md`): all real code.

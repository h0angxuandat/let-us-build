import { A, useParams } from "@solidjs/router";
import { createResource, createSignal, onMount, Show } from "solid-js";
import { Board } from "~/components/kanban/Board";
import { TicketDrawer } from "~/components/TicketDrawer";
import { api } from "~/lib/api";
import type { Ticket } from "~/lib/types";
import { subscribeProject } from "~/lib/ws";

// Project board: 4-lane Kanban fed by the API, live-updated over WebSocket.
export default function ProjectBoard() {
  const params = useParams();
  const pid = (): string => params.id ?? "";
  const [project] = createResource(pid, (id) => api.getProject(id));
  const [tickets, { refetch }] = createResource(pid, (id) => api.listTickets(id));
  const [open, setOpen] = createSignal<Ticket | null>(null);
  const [title, setTitle] = createSignal("");

  onMount(() => subscribeProject(pid(), () => void refetch()));

  async function addToPlan(e: Event): Promise<void> {
    e.preventDefault();
    if (!title().trim()) return;
    await api.addTicket(pid(), { title: title().trim() });
    setTitle("");
    await refetch();
  }

  function focusAdd(): void {
    document.getElementById("new-ticket")?.focus();
  }

  return (
    <section aria-labelledby="board-title">
      <div class="board-head">
        <div>
          <A href="/" class="muted back-link">
            ← Projects
          </A>
          <h1 id="board-title">{project()?.name ?? "Board"}</h1>
        </div>
        <form class="add-inline" onSubmit={addToPlan}>
          <label for="new-ticket" class="sr-only">
            New ticket title
          </label>
          <input
            id="new-ticket"
            value={title()}
            onInput={(e) => setTitle(e.currentTarget.value)}
            placeholder="Add a ticket to Plan…"
          />
          <button type="submit">Add</button>
        </form>
      </div>

      <Show
        when={!tickets.error}
        fallback={
          <p class="error" role="alert">
            Couldn't load tickets. Is the core API running at {api.base}?
          </p>
        }
      >
        <Board tickets={tickets() ?? []} onOpen={setOpen} onAddToPlan={focusAdd} />
      </Show>

      <Show when={open()}>
        {(t) => (
          <TicketDrawer
            ticket={t()}
            onClose={() => setOpen(null)}
            onChanged={() => void refetch()}
          />
        )}
      </Show>
    </section>
  );
}

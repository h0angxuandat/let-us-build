import { createSignal, onCleanup, onMount, Show } from "solid-js";
import type { Ticket } from "~/lib/types";

// Ticket detail drawer. Overview is live; the Discussion tab is a placeholder until M5
// (the live transcript + Decision card land with the discussion subgraph).
export function TicketDrawer(props: { ticket: Ticket; onClose: () => void }) {
  const [tab, setTab] = createSignal<"overview" | "discussion">("overview");

  onMount(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && props.onClose();
    window.addEventListener("keydown", onKey);
    onCleanup(() => window.removeEventListener("keydown", onKey));
  });

  return (
    <div class="drawer-overlay" onClick={props.onClose}>
      <aside
        class="drawer"
        role="dialog"
        aria-modal="true"
        aria-label={`Ticket ${props.ticket.key}`}
        onClick={(e) => e.stopPropagation()}
      >
        <header class="drawer__header">
          <div>
            <span class="ticket-card__key">{props.ticket.key}</span>
            <h2>{props.ticket.title}</h2>
          </div>
          <button class="drawer__close" onClick={props.onClose} aria-label="Close">
            ✕
          </button>
        </header>

        <div class="tabs" role="tablist" aria-label="Ticket sections">
          <button
            role="tab"
            aria-selected={tab() === "overview"}
            class="tab"
            classList={{ "tab--active": tab() === "overview" }}
            onClick={() => setTab("overview")}
          >
            Overview
          </button>
          <button
            role="tab"
            aria-selected={tab() === "discussion"}
            class="tab"
            classList={{ "tab--active": tab() === "discussion" }}
            onClick={() => setTab("discussion")}
          >
            Discussion
          </button>
        </div>

        <div class="drawer__body">
          <Show when={tab() === "overview"}>
            <dl class="detail">
              <dt>Lane</dt>
              <dd>{props.ticket.lane}</dd>
              <dt>Type</dt>
              <dd>{props.ticket.type}</dd>
              <dt>Status</dt>
              <dd>{props.ticket.status}</dd>
            </dl>
            <p>{props.ticket.description || "No description yet."}</p>
          </Show>
          <Show when={tab() === "discussion"}>
            <p class="placeholder">
              Agents will discuss decisions here — the live transcript and the plain-language
              Decision card arrive in milestone M5.
            </p>
          </Show>
        </div>
      </aside>
    </div>
  );
}

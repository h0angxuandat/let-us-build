import { createResource, createSignal, For, onCleanup, onMount, Show } from "solid-js";
import { api } from "~/lib/api";
import type { Ticket } from "~/lib/types";

// Ticket detail drawer. Overview + Artifacts are live; Discussion is a placeholder until M5.
export function TicketDrawer(props: {
  ticket: Ticket;
  onClose: () => void;
  onChanged?: () => void;
}) {
  const [tab, setTab] = createSignal<"overview" | "artifacts" | "discussion">("overview");
  const [artifacts, { refetch }] = createResource(
    () => props.ticket.id,
    (id) => api.listArtifacts(id),
  );
  const [running, setRunning] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  onMount(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && props.onClose();
    window.addEventListener("keydown", onKey);
    onCleanup(() => window.removeEventListener("keydown", onKey));
  });

  async function runBA(): Promise<void> {
    setRunning(true);
    setError(null);
    try {
      await api.runTicket(props.ticket.id);
      await refetch();
      setTab("artifacts");
      props.onChanged?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed");
    } finally {
      setRunning(false);
    }
  }

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
            aria-selected={tab() === "artifacts"}
            class="tab"
            classList={{ "tab--active": tab() === "artifacts" }}
            onClick={() => setTab("artifacts")}
          >
            Artifacts
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
            <button onClick={runBA} disabled={running()}>
              {running() ? "Running BA…" : "Run Business Analyst"}
            </button>
            <Show when={error()}>
              <p class="error" role="alert">
                {error()}
              </p>
            </Show>
          </Show>

          <Show when={tab() === "artifacts"}>
            <For
              each={artifacts()}
              fallback={<p class="placeholder">No artifacts yet. Run an agent to produce one.</p>}
            >
              {(a) => (
                <article class="artifact">
                  <h3 class="artifact__type">
                    {a.type}
                    <Show when={a.produced_by}>
                      <span class="muted"> · by {a.produced_by}</span>
                    </Show>
                  </h3>
                  <pre class="artifact__body">{a.inline}</pre>
                </article>
              )}
            </For>
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

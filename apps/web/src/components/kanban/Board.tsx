import { For, Show } from "solid-js";
import { LANES, type Lane, type Ticket } from "~/lib/types";
import { TicketCard } from "./TicketCard";

export function Board(props: {
  tickets: Ticket[];
  onOpen: (t: Ticket) => void;
  onAddToPlan: () => void;
}) {
  const byLane = (lane: Lane) => props.tickets.filter((t) => t.lane === lane);

  return (
    <div class="board" role="list" aria-label="Kanban board">
      <For each={LANES}>
        {(lane) => (
          <section class="lane" role="listitem" aria-label={`${lane.label} lane`}>
            <header class="lane__header">
              <h2 class="lane__title">{lane.label}</h2>
              <span class="lane__count" aria-label={`${byLane(lane.id).length} tickets`}>
                {byLane(lane.id).length}
              </span>
              <Show when={lane.id === "plan"}>
                <button class="lane__add" onClick={props.onAddToPlan}>
                  + Add
                </button>
              </Show>
            </header>
            <div class="lane__cards">
              <For
                each={byLane(lane.id)}
                fallback={<p class="lane__empty">Nothing here yet.</p>}
              >
                {(ticket) => <TicketCard ticket={ticket} onOpen={props.onOpen} />}
              </For>
            </div>
          </section>
        )}
      </For>
    </div>
  );
}

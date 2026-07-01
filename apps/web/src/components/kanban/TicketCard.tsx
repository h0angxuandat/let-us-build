import { Show } from "solid-js";
import { ROLE_META } from "~/lib/roles";
import type { Ticket } from "~/lib/types";

export function TicketCard(props: { ticket: Ticket; onOpen: (t: Ticket) => void }) {
  const role = () => (props.ticket.assignee_role ? ROLE_META[props.ticket.assignee_role] : null);
  return (
    <button
      class="ticket-card"
      onClick={() => props.onOpen(props.ticket)}
      aria-label={`Open ticket ${props.ticket.key}: ${props.ticket.title}`}
    >
      <span class="ticket-card__key">{props.ticket.key}</span>
      <span class="ticket-card__title">{props.ticket.title}</span>
      <span class="ticket-card__meta">
        <Show when={role()} fallback={<span class="badge">{props.ticket.type}</span>}>
          {(r) => (
            <span class="badge" style={{ "border-color": r().color }}>
              <span aria-hidden="true">{r().icon}</span> {r().label}
            </span>
          )}
        </Show>
        <Show when={props.ticket.lane === "human_needed"}>
          <span class="badge badge--attention">🙋 Needs you</span>
        </Show>
      </span>
    </button>
  );
}

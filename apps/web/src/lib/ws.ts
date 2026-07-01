// WebSocket subscription to a project's realtime event stream.
import { onCleanup } from "solid-js";
import { api } from "./api";

export interface ProjectEvent {
  type: string;
  ticket?: unknown;
}

/** Open a project WS; invokes `onEvent` for each message. Auto-closes on cleanup. */
export function subscribeProject(projectId: string, onEvent: (e: ProjectEvent) => void): void {
  const url = api.base.replace(/^http/, "ws") + `/ws/projects/${projectId}`;
  let socket: WebSocket | null = null;
  try {
    socket = new WebSocket(url);
    socket.onmessage = (msg) => {
      try {
        onEvent(JSON.parse(msg.data) as ProjectEvent);
      } catch {
        /* ignore malformed frames */
      }
    };
  } catch {
    /* WS unavailable — the board still works via manual refetch */
  }
  onCleanup(() => socket?.close());
}

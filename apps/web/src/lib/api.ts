// Typed REST client for the core API.
import type { Agent, Project, Ticket } from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8300";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export const api = {
  base: BASE,
  listProjects: () => request<Project[]>("/projects"),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (body: { name: string; description?: string }) =>
    request<Project>("/projects", { method: "POST", body: JSON.stringify(body) }),

  listTickets: (projectId: string) => request<Ticket[]>(`/projects/${projectId}/tickets`),
  addTicket: (projectId: string, body: { title: string; description?: string }) =>
    request<Ticket>(`/projects/${projectId}/tickets`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  moveTicket: (ticketId: string, lane: string) =>
    request<Ticket>(`/tickets/${ticketId}`, { method: "PATCH", body: JSON.stringify({ lane }) }),

  listAgents: () => request<Agent[]>("/agents"),
};

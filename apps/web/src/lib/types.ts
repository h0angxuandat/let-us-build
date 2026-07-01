// Shared API types (mirror of the core-api schemas).

export type Role = "pm" | "ba" | "designer" | "tech_lead" | "developer" | "qe";
export type Lane = "plan" | "human_needed" | "processing" | "testing" | "done";

export interface Project {
  id: string;
  name: string;
  description: string;
  target_platform: string | null;
  status: string;
}

export interface Ticket {
  id: string;
  project_id: string;
  key: string;
  title: string;
  description: string;
  type: string;
  lane: Lane;
  status: string;
  priority: number;
  assignee_role: Role | null;
  created_by: string;
}

export interface Agent {
  id: string;
  project_id: string | null;
  role: Role;
  display_name: string;
  enabled: boolean;
  provider: string;
  model: string;
  temperature: number;
  skill_ids: string[];
}

// Lanes in board order. Note: the board shows all five lane states.
export const LANES: { id: Lane; label: string }[] = [
  { id: "plan", label: "Plan" },
  { id: "human_needed", label: "Needs you" },
  { id: "processing", label: "Processing" },
  { id: "testing", label: "Testing" },
  { id: "done", label: "Done" },
];

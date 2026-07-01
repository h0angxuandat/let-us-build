// Role identity: icon + label + color. Icon + label carry meaning (a11y: never color alone).
import type { Role } from "./types";

export const ROLE_META: Record<Role, { icon: string; label: string; color: string }> = {
  pm: { icon: "◆", label: "PM", color: "var(--role-pm)" },
  ba: { icon: "✎", label: "BA", color: "var(--role-ba)" },
  designer: { icon: "✍", label: "Designer", color: "var(--role-designer)" },
  tech_lead: { icon: "⌘", label: "Tech Lead", color: "var(--role-tech-lead)" },
  developer: { icon: "⌥", label: "Dev", color: "var(--role-developer)" },
  qe: { icon: "✓", label: "QE", color: "var(--role-qe)" },
};

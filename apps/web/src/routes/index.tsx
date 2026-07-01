import { A } from "@solidjs/router";
import { createResource, createSignal, For, Show } from "solid-js";
import { api } from "~/lib/api";

// Dashboard: list projects + create a new one (simple form; a 3-step wizard is a later polish).
export default function Dashboard() {
  const [projects, { refetch }] = createResource(() => api.listProjects());
  const [name, setName] = createSignal("");
  const [busy, setBusy] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  async function create(e: Event): Promise<void> {
    e.preventDefault();
    if (!name().trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api.createProject({ name: name().trim() });
      setName("");
      await refetch();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="dash-title">
      <h1 id="dash-title">Your projects</h1>

      <form class="create-form" onSubmit={create}>
        <label for="project-name">New project</label>
        <div class="create-form__row">
          <input
            id="project-name"
            value={name()}
            onInput={(e) => setName(e.currentTarget.value)}
            placeholder="e.g. Todo app"
            required
          />
          <button type="submit" disabled={busy()}>
            {busy() ? "Creating…" : "Create project"}
          </button>
        </div>
        <Show when={error()}>
          <p class="error" role="alert">
            {error()}
          </p>
        </Show>
      </form>

      <Show when={projects.error}>
        <p class="error" role="alert">
          Couldn't reach the API at {api.base}. Is the core running?
        </p>
      </Show>

      <ul class="project-list">
        <For
          each={projects()}
          fallback={
            <Show when={!projects.loading}>
              <li class="muted">No projects yet — create one above.</li>
            </Show>
          }
        >
          {(p) => (
            <li>
              <A href={`/projects/${p.id}`} class="project-list__item">
                <strong>{p.name}</strong>
                <span class="muted">{p.description || "No description"}</span>
              </A>
            </li>
          )}
        </For>
      </ul>
    </section>
  );
}

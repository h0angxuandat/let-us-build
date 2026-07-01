import { A, Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";
import { Suspense } from "solid-js";
import "./styles/tokens.css";
import "./styles/global.css";
import "./styles/kanban.css";

// Root app shell: skip link + header nav + main landmark (a11y-first per design/ui-ux-spec.md).
export default function App() {
  return (
    <Router
      root={(props) => (
        <>
          <a href="#content" class="skip-link">
            Skip to content
          </a>
          <header class="app-header">
            <nav aria-label="Main">
              <A href="/" class="brand">
                let·us·build
              </A>
            </nav>
          </header>
          <main id="content">
            <Suspense fallback={<p>Loading…</p>}>{props.children}</Suspense>
          </main>
        </>
      )}
    >
      <FileRoutes />
    </Router>
  );
}

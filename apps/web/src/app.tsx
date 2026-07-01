import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";
import { Suspense } from "solid-js";
import "./styles/tokens.css";
import "./styles/global.css";

// Root app shell. Layout (nav + main landmarks) is fleshed out in M2 per design/ui-ux-spec.md.
export default function App() {
  return (
    <Router
      root={(props) => (
        <Suspense>
          <main>{props.children}</main>
        </Suspense>
      )}
    >
      <FileRoutes />
    </Router>
  );
}

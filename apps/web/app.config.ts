import { defineConfig } from "@solidjs/start/config";

// SolidStart config. SPA mode (ssr:false) — the UI is a client app talking to the core API over
// REST + WebSocket, so there's no server-side data fetching to coordinate. Dev server on 8301.
export default defineConfig({
  ssr: false,
  server: {
    port: 8301,
  },
});

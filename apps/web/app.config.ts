import { defineConfig } from "@solidjs/start/config";

// SolidStart config. Dev server on 8301 (LUB_WEB_PORT). Proxy to core API added in M2.
export default defineConfig({
  server: {
    port: 8301,
  },
});

import {
  sourceState,
  isBuildCurrent,
  frontendRoot,
} from "./scripts/build-state.mjs";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import process from "node:process";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const buildInfo = sourceState(frontendRoot);
  return {
    define: {
      "import.meta.env.VITE_SKILLSYNC_BUILD": JSON.stringify(buildInfo),
    },
    plugins: [
      react(),
      {
        name: "skillsync-build-identity",
        generateBundle() {
          this.emitFile({
            type: "asset",
            fileName: "build-info.json",
            source: JSON.stringify(buildInfo, null, 2),
          });
        },
        configurePreviewServer() {
          if (!isBuildCurrent(frontendRoot))
            throw new Error(
              "Stale frontend build. Use npm run preview to rebuild before serving. Do not run an older dist folder.",
            );
        },
      },
    ],
    preview: { headers: { "Cache-Control": "no-store" }, allowedHosts: true },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    server: {
      headers: { "Cache-Control": "no-store" },
      host: true,
      port: 5173,
      allowedHosts: true,
      proxy: {
        "/api": {
          target: env.VITE_BACKEND_URL || "http://127.0.0.1:8000",
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});

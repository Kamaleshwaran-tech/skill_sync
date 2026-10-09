import { spawnSync } from "node:child_process";
import { frontendRoot, isBuildCurrent } from "./build-state.mjs";

if (!isBuildCurrent()) {
  console.log(
    "Frontend build is missing or older than this source. Rebuilding before preview…",
  );
  if (!process.env.npm_execpath) {
    console.error(
      "Run npm run preview (or the project web launcher), not this script directly.",
    );
    process.exit(1);
  }
  const result = spawnSync(
    process.execPath,
    [process.env.npm_execpath, "run", "build"],
    { cwd: frontendRoot, stdio: "inherit" },
  );
  if (result.error || result.status !== 0 || !isBuildCurrent()) {
    console.error(
      "Frontend build failed. Preview was not started. Run npm ci in frontend, then try again.",
    );
    process.exit(1);
  }
} else
  console.log("Verified: preview build matches the current frontend source.");

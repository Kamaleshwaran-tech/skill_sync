import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { sourceState, isBuildCurrent } from "../scripts/build-state.mjs";

test("old/missing builds are rejected and changes in source invalidate the fingerprint", () => {
  const root = mkdtempSync(join(tmpdir(), "skillsync-build-test-"));
  try {
    mkdirSync(join(root, "src"));
    mkdirSync(join(root, "dist"));
    writeFileSync(join(root, "src/App.jsx"), "first version");
    writeFileSync(join(root, "dist/index.html"), "old built page");
    assert.equal(isBuildCurrent(root), false);
    writeFileSync(
      join(root, "dist/build-info.json"),
      JSON.stringify(sourceState(root)),
    );
    assert.equal(isBuildCurrent(root), true);
    writeFileSync(join(root, "src/App.jsx"), "corrected version");
    assert.equal(isBuildCurrent(root), false);
    writeFileSync(join(root, "dist/build-info.json"), "{invalid");
    assert.equal(isBuildCurrent(root), false);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

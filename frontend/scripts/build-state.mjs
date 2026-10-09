import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

export const frontendRoot = dirname(dirname(fileURLToPath(import.meta.url)));
export function sourceState(root = frontendRoot) {
  const files = [];
  function collect(folder) {
    if (!existsSync(join(root, folder))) return;
    for (const entry of readdirSync(join(root, folder), {
      withFileTypes: true,
    })) {
      const path = join(folder, entry.name);
      if (entry.isDirectory()) collect(path);
      else if (entry.isFile()) files.push(path);
    }
  }
  for (const folder of ["src", "public", "scripts"]) collect(folder);
  for (const name of [
    "index.html",
    "package.json",
    "package-lock.json",
    "vite.config.js",
  ])
    if (existsSync(join(root, name))) files.push(name);
  const hash = createHash("sha256");
  for (const file of files.sort()) {
    hash.update(relative(root, join(root, file)).replaceAll("\\", "/"));
    hash.update("\0");
    hash.update(readFileSync(join(root, file)));
    hash.update("\0");
  }
  return { interfaceId: "screenshot-fixes-v1", sourceHash: hash.digest("hex") };
}
export function isBuildCurrent(root = frontendRoot) {
  try {
    const saved = JSON.parse(
      readFileSync(join(root, "dist/build-info.json"), "utf8"),
    );
    const current = sourceState(root);
    return (
      existsSync(join(root, "dist/index.html")) &&
      saved.interfaceId === current.interfaceId &&
      saved.sourceHash === current.sourceHash
    );
  } catch {
    return false;
  }
}

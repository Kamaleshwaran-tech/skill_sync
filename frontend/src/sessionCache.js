// Per-Workspace-instance cache. Never persisted or shared across signed-in users.
// Only GET snapshots belong here; an explicit Adzuna search always uses the network.
export function createSessionCache({
  ttlMs = 60_000,
  maxEntries = 16,
  maxBytes = 8 * 1024 * 1024,
  now = Date.now,
} = {}) {
  const entries = new Map();
  function cancelled() {
    return Object.assign(new Error("Snapshot request superseded"), {
      code: "ERR_CANCELED",
    });
  }
  function discard(key) {
    const entry = entries.get(key);
    entries.delete(key);
    entry?.controller?.abort();
  }
  function trim() {
    let bytes = [...entries.values()].reduce(
      (n, entry) => n + (entry.bytes || 0),
      0,
    );
    while (entries.size > maxEntries || bytes > maxBytes) {
      const key = entries.keys().next().value;
      bytes -= entries.get(key)?.bytes || 0;
      discard(key);
    }
  }
  function touch(key, entry) {
    entries.delete(key);
    entries.set(key, entry);
  }
  function sizeOf(data) {
    try {
      return JSON.stringify(data).length * 2;
    } catch {
      return maxBytes + 1;
    }
  }
  return {
    peek(key) {
      const entry = entries.get(key);
      return entry?.hasData
        ? { data: entry.data, fresh: now() - entry.updatedAt < ttlMs }
        : null;
    },
    load(key, loader) {
      let entry = entries.get(key);
      if (entry?.pending) return entry.pending;
      if (entry?.hasData && now() - entry.updatedAt < ttlMs) {
        touch(key, entry);
        return Promise.resolve(entry.data);
      }
      entry = { ...entry, controller: new AbortController() };
      touch(key, entry);
      const pending = Promise.resolve()
        .then(() => {
          if (entry.controller.signal.aborted) throw cancelled();
          return loader(entry.controller.signal);
        })
        .then((data) => {
          if (entries.get(key) !== entry) throw cancelled();
          Object.assign(entry, {
            data,
            hasData: true,
            updatedAt: now(),
            bytes: sizeOf(data),
            pending: null,
          });
          touch(key, entry);
          trim();
          return data;
        })
        .catch((error) => {
          if (entries.get(key) === entry) {
            entry.pending = null;
            if (!entry.hasData) entries.delete(key);
            else entry.updatedAt = -Infinity;
          }
          throw error;
        });
      entry.pending = pending;
      trim();
      return pending;
    },
    put(key, data) {
      discard(key);
      touch(key, {
        data,
        hasData: true,
        updatedAt: now(),
        bytes: sizeOf(data),
      });
      trim();
    },
    invalidate: discard,
    clear() {
      for (const key of [...entries.keys()]) discard(key);
    },
  };
}

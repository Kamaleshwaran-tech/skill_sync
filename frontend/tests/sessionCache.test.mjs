import test from "node:test";
import assert from "node:assert/strict";
import { createSessionCache } from "../src/sessionCache.js";

const deferred = () => {
  let resolve;
  const promise = new Promise((r) => {
    resolve = r;
  });
  return { promise, resolve };
};

test("deduplicates concurrent GETs and serves a fresh snapshot without another request", async () => {
  const cache = createSessionCache();
  const request = deferred();
  let calls = 0;
  const loader = () => {
    calls++;
    return request.promise;
  };
  const a = cache.load("analysis:1", loader),
    b = cache.load("analysis:1", loader);
  assert.equal(a, b);
  request.resolve({ id: 1 });
  await a;
  assert.deepEqual(await cache.load("analysis:1", loader), { id: 1 });
  assert.equal(calls, 1);
});
test("TTL revalidates once while the old snapshot remains available", async () => {
  let clock = 0;
  const cache = createSessionCache({ ttlMs: 50, now: () => clock });
  cache.put("analysis:1", { id: 1 });
  clock = 51;
  assert.equal(cache.peek("analysis:1").fresh, false);
  const pending = deferred();
  const read = cache.load("analysis:1", () => pending.promise);
  assert.equal(cache.peek("analysis:1").data.id, 1);
  pending.resolve({ id: 2 });
  await read;
  assert.equal(cache.peek("analysis:1").data.id, 2);
});
test("invalidation aborts a request and late responses cannot repopulate deleted data", async () => {
  const cache = createSessionCache();
  const pending = deferred();
  let signal;
  const read = cache.load("analysis:1", (s) => {
    signal = s;
    return pending.promise;
  });
  await Promise.resolve();
  cache.invalidate("analysis:1");
  assert.equal(signal.aborted, true);
  const rejected = assert.rejects(read, { code: "ERR_CANCELED" });
  pending.resolve({ id: 1 });
  await rejected;
  assert.equal(cache.peek("analysis:1"), null);
});
test("a successful fresh search cannot be overwritten by an older saved-result GET", async () => {
  const cache = createSessionCache();
  const pending = deferred();
  const old = cache.load("matches:1", () => pending.promise);
  await Promise.resolve();
  cache.put("matches:1", { result: { run_id: 2 } });
  const rejected = assert.rejects(old, { code: "ERR_CANCELED" });
  pending.resolve({ result: { run_id: 1 } });
  await rejected;
  assert.equal(cache.peek("matches:1").data.result.run_id, 2);
});
test("different sessions and resumes cannot share data; logout clears memory", () => {
  const a = createSessionCache(),
    b = createSessionCache();
  a.put("analysis:1", { id: 1 });
  a.put("analysis:2", { id: 2 });
  assert.equal(b.peek("analysis:1"), null);
  assert.equal(a.peek("analysis:2").data.id, 2);
  a.clear();
  assert.equal(a.peek("analysis:1"), null);
  assert.equal(a.peek("analysis:2"), null);
});
test("failed reads are retried, not cached as successful empty responses", async () => {
  const cache = createSessionCache();
  await assert.rejects(
    cache.load("matches:1", () => Promise.reject(new Error("outage"))),
  );
  assert.equal(cache.peek("matches:1"), null);
  assert.deepEqual(await cache.load("matches:1", () => ({ result: null })), {
    result: null,
  });
});
test("bounded LRU cache evicts old entries and rejects oversized retention", async () => {
  const cache = createSessionCache({ maxEntries: 2, maxBytes: 100 });
  cache.put("a", { x: 1 });
  cache.put("b", { x: 2 });
  await cache.load("a", () => assert.fail("network"));
  cache.put("c", { x: 3 });
  assert.equal(cache.peek("b"), null);
  assert.ok(cache.peek("a"));
  cache.put("large", "x".repeat(100));
  assert.equal(cache.peek("large"), null);
});

test("StrictMode-style teardown cancels queued work before the loader runs", async () => {
  const cache = createSessionCache();
  let requests = 0;
  const loader = () => {
    requests++;
    return { id: 1 };
  };
  const abandoned = cache.load("analysis:1", loader);
  cache.clear();
  const rejected = assert.rejects(abandoned, { code: "ERR_CANCELED" });
  const current = await cache.load("analysis:1", loader);
  await rejected;
  assert.equal(current.id, 1);
  assert.equal(requests, 1);
});

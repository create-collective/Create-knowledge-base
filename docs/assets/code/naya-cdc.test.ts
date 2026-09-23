// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Create-knowledge-base contributors
// Offline tests for naya-cdc.ts with a fake Web Serial port. Run: node --test naya-cdc.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  buildFrame, parseFrame, FrameReader, CreateLink, fwVersion, readStore, writeStore,
  keyPress, ledEntry, ledSetting, xor8, LEFT, RIGHT,
} from "./naya-cdc.ts";

const H = (s: string) => Uint8Array.from(s.trim().split(/\s+/).map(x => parseInt(x, 16)));
const hex = (b: Uint8Array) => Array.from(b, x => x.toString(16).padStart(2, "0")).join(" ");

function reply(category: number, subcmd: number, status: number, payload = new Uint8Array(0), sender = 0x50): Uint8Array {
  const data = new Uint8Array(3 + payload.length);
  data.set([subcmd >> 8, subcmd & 0xff, status]); data.set(payload, 3);
  const out = new Uint8Array(data.length + 8);
  out.set([0xaa, sender, 0x00, 0x00, category, data.length]); out.set(data, 6);
  out[6 + data.length] = xor8(data); out[7 + data.length] = 0x04;
  return out;
}

/** A fake Web Serial port: every written frame is answered by the next scripted reply,
 *  delivered one byte per read() like a USB capture shows it. */
function fakePort(replies: Uint8Array[]) {
  const written: Uint8Array[] = [];
  const queue: number[] = [];
  let wake: (() => void) | null = null;
  return {
    written,
    async open() {}, async setSignals() {}, async close() {},
    writable: { getWriter: () => ({ async write(f: Uint8Array) {
      written.push(f);
      const r = replies.shift();
      if (r) { queue.push(...r); wake?.(); }
    }, releaseLock() {} }) },
    readable: { getReader: () => ({
      async read(): Promise<{ value?: Uint8Array; done: boolean }> {
        while (queue.length === 0) await new Promise<void>(res => { wake = res; });
        return { value: Uint8Array.of(queue.shift()!), done: false };
      },
      async cancel() {}, releaseLock() {},
    }) },
  };
}

test("vendor frames", () => {
  assert.equal(hex(buildFrame(LEFT, 0xfe, 0x1001)), "aa 00 50 00 fe 03 10 01 00 11 04");
  assert.equal(hex(buildFrame(RIGHT, 0xfe, 0x1001)), "aa 00 51 00 fe 03 10 01 00 11 04");
  assert.equal(hex(buildFrame(LEFT, 0xfe, 0x1002)), "aa 00 50 00 fe 03 10 02 00 12 04");
  const f = parseFrame(H("aa 50 00 00 fe 03 10 01 00 11 04"));
  assert.deepEqual([f.sender, f.dest, f.subcmd, f.status], [0x50, 0x00, 0x1001, 0x00]);
});

test("version reply 3.41.0", () => {
  const f = parseFrame(H("aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04"));
  assert.equal(fwVersion(f), "3.41.0");
});

test("read and key-write frames", () => {
  assert.equal(hex(buildFrame(LEFT, 0x30, 0x1003, Uint8Array.of(0))), "aa 00 50 00 30 04 10 03 00 00 13 04");
  assert.equal(hex(buildFrame(LEFT, 0x30, 0x1003, Uint8Array.of(0), 1)), "aa 00 50 00 30 04 10 03 01 00 12 04");
  const payload = new Uint8Array([0x00, ...keyPress(0x20, 0x05)]);
  assert.equal(hex(buildFrame(LEFT, 0x30, 0x1004, payload)), "aa 00 50 00 30 0b 10 04 00 00 20 01 04 05 00 07 00 33 04");
});

test("frame reader resyncs", () => {
  const good = H("aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04");
  const r = new FrameReader();
  const noisy = new Uint8Array([0x00, 0xaa, 0x13, ...good.subarray(0, 4)]);
  assert.equal(r.push(noisy).length, 0);
  assert.equal(r.push(good.subarray(4)).length, 1);
});

test("full LED map write: three frames, byte 3 counts down", async () => {
  const port = fakePort([reply(0x30, 0x100e, 1), reply(0x30, 0x100e, 1), reply(0x30, 0x100e, 0)]);
  const link = new CreateLink(port); await link.open();
  const records = new Uint8Array(136 * 4);
  for (let i = 0; i < 136; i++) records.set(ledEntry(i, 0, 150), i * 4);
  await writeStore(link, 0x100e, 0, records);
  assert.deepEqual(port.written.map(w => w[3]), [2, 1, 0]);
  assert.deepEqual(port.written.map(w => w[5]), [0xf5, 0xf5, 0x42]);
  await assert.rejects(writeStore(link, 0x100e, 0, records, 2));
});

test("chunked read with continue flag", async () => {
  const port = fakePort([reply(0x30, 0x1003, 1, H("00 20 01 04")), reply(0x30, 0x1003, 0, H("00 05 00 07 00"))]);
  const link = new CreateLink(port); await link.open();
  const body = await readStore(link, 0x1003, 0);
  assert.equal(hex(body!), "20 01 04 05 00 07 00");
  assert.deepEqual(port.written.map(w => w[8]), [0, 1]);
});

test("ed/1013 guard and framing", async () => {
  const port = fakePort([reply(0xed, 0x1013, 0)]);
  const link = new CreateLink(port); await link.open();
  await assert.rejects(ledSetting(link, 0x1013, 0));
  await ledSetting(link, 0x1013, 100);
  assert.equal(hex(port.written[0].subarray(6, 11)), "10 13 00 00 64");
});

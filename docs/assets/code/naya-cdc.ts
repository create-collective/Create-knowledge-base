// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Create-knowledge-base contributors
// Minimal Naya Create CDC client for the browser (Web Serial) or any byte stream.
// Frame: AA <b1> <b2> <b3> <category> <size> <sub_hi> <sub_lo> <flags> <payload...> <xor> 04
// size = 3 + payload length; xor covers sub_hi .. last payload byte (not the size byte).
// The site's params / reply strings start at the flags / status byte; here that byte is
// `flags` / `status` and the rest is `payload`.
// Tested offline with naya-cdc.test.ts (Node 23.6+ runs .ts directly); not a flasher.

export const SOF = 0xaa;
export const EOT = 0x04;
export const LEFT = 0x50;
export const RIGHT = 0x51;
export const MAX_PAYLOAD = 242;
export const SLICE = 241;
export const ST_LAST = 0x00;
export const ST_MORE = 0x01;
export const ST_NOTHING_STORED = 0x16;
export const ST_NOTHING_STORED_CONT = 0x18;
export const ST_VALUE_REFUSED = 0xea;

export function xor8(data: Uint8Array): number {
  let x = 0;
  for (const b of data) x ^= b;
  return x;
}

export function buildFrame(dest: number, category: number, subcmd: number,
  payload: Uint8Array = new Uint8Array(0), flags = 0, remaining = 0): Uint8Array {
  if (payload.length > MAX_PAYLOAD) throw new RangeError("payload over 242 bytes: split it");
  const data = new Uint8Array(3 + payload.length);
  data[0] = (subcmd >> 8) & 0xff;
  data[1] = subcmd & 0xff;
  data[2] = flags;
  data.set(payload, 3);
  const out = new Uint8Array(data.length + 8);
  out.set([SOF, 0x00, dest, remaining, category, data.length], 0);
  out.set(data, 6);
  out[6 + data.length] = xor8(data);
  out[7 + data.length] = EOT;
  return out;
}

export interface Frame {
  sender: number; dest: number; remaining: number; category: number;
  subcmd: number; status: number; payload: Uint8Array;
}

export function parseFrame(f: Uint8Array): Frame {
  if (f.length < 11 || f[0] !== SOF || f[f.length - 1] !== EOT) throw new Error("not a frame");
  const size = f[5];
  if (size < 3 || f.length !== size + 8) throw new Error("length does not match the size byte");
  const data = f.subarray(6, 6 + size);
  if (xor8(data) !== f[6 + size]) throw new Error("checksum mismatch");
  return {
    sender: f[1], dest: f[2], remaining: f[3], category: f[4],
    subcmd: (data[0] << 8) | data[1], status: data[2], payload: data.slice(3),
  };
}

/** Collects bytes and returns whole frames; resyncs on 0xAA after noise. */
export class FrameReader {
  private buf: Uint8Array = new Uint8Array(0);

  push(chunk: Uint8Array): Frame[] {
    const merged = new Uint8Array(this.buf.length + chunk.length);
    merged.set(this.buf, 0);
    merged.set(chunk, this.buf.length);
    let b = merged;
    const out: Frame[] = [];
    for (;;) {
      const start = b.indexOf(SOF);
      if (start < 0) { b = new Uint8Array(0); break; }
      b = b.subarray(start);
      if (b.length < 6) break;
      const total = b[5] + 8;
      if (b.length < total) break;
      const cand = b.subarray(0, total);
      if (cand[total - 1] === EOT && xor8(cand.subarray(6, total - 2)) === cand[total - 2]) {
        out.push(parseFrame(cand.slice()));
        b = b.subarray(total);
      } else {
        b = b.subarray(1);
      }
    }
    this.buf = b.slice();
    return out;
  }
}

interface Waiter { category: number; subcmd: number; resolve: (f: Frame) => void; timer: ReturnType<typeof setTimeout>; }

/** One open port. Call open() once and keep the link for the whole job. */
export class CreateLink {
  dest: number;
  private port: any; // a Web Serial SerialPort (types: @types/w3c-web-serial)
  private reader: any = null;
  private writer: any = null;
  private frames = new FrameReader();
  private waiters: Waiter[] = [];

  constructor(port: any, dest: number = LEFT) {
    this.port = port;
    this.dest = dest;
  }

  async open(): Promise<void> {
    await this.port.open({ baudRate: 115200 });        // nominal on USB CDC
    await this.port.setSignals({ dataTerminalReady: true, requestToSend: true });
    this.writer = this.port.writable.getWriter();
    this.reader = this.port.readable.getReader();
    void this.pump();
  }

  async close(): Promise<void> {
    await this.reader?.cancel();
    this.reader?.releaseLock();
    this.writer?.releaseLock();
    await this.port.close();
  }

  private async pump(): Promise<void> {
    for (;;) {
      const { value, done } = await this.reader.read();
      if (done) return;
      for (const f of this.frames.push(value)) {
        const i = this.waiters.findIndex(w => w.category === f.category && w.subcmd === f.subcmd);
        if (i < 0) continue;                               // unsolicited or late: dropped
        const [w] = this.waiters.splice(i, 1);
        clearTimeout(w.timer);
        w.resolve(f);
      }
    }
  }

  async write(frame: Uint8Array): Promise<void> { await this.writer.write(frame); }

  /** One request. dest RIGHT on the left half's port reaches the right half for the version
   *  read; Bluetooth reads sent that way answer for the left half. */
  send(category: number, subcmd: number, payload: Uint8Array = new Uint8Array(0),
    flags = 0, remaining = 0, timeoutMs = 1000, dest: number = this.dest): Promise<Frame> {
    return new Promise<Frame>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.waiters = this.waiters.filter(w => w.timer !== timer);
        reject(new Error(`no reply to ${category.toString(16)}/${subcmd.toString(16)}`));
      }, timeoutMs);
      this.waiters.push({ category, subcmd, resolve, timer });
      this.write(buildFrame(dest, category, subcmd, payload, flags, remaining)).catch(reject);
    });
  }

  /** fe/1001 (media id request) then fe/1002 (firmware version), as NayaCore does. */
  async openSession(): Promise<Frame> {
    for (const waitMs of [300, 700, 1000]) {
      await this.write(buildFrame(this.dest, 0xfe, 0x1001));
      await new Promise(r => setTimeout(r, waitMs));
      try { return await this.send(0xfe, 0x1002, new Uint8Array(0), 0, 0, 500); } catch { /* retry */ }
    }
    throw new Error("no answer to fe/1001 + fe/1002");
  }
}

export function fwVersion(reply: Frame): string {
  const p = reply.payload;             // reply 00 00 03 29 00: status, then 00 major minor patch
  return `${p[p.length - 3]}.${p[p.length - 2]}.${p[p.length - 1]}`;
}

/** Chunked REMAP read (30/1003 layer, 30/100d LED map, 30/100b module config). */
export async function readStore(link: CreateLink, subcmd: number, index: number): Promise<Uint8Array | null> {
  const parts: Uint8Array[] = [];
  let flags = 0x00;
  for (;;) {
    const f = await link.send(0x30, subcmd, Uint8Array.of(index), flags);
    if (f.status === ST_NOTHING_STORED || f.status === ST_NOTHING_STORED_CONT) return null;
    if (f.status !== ST_LAST && f.status !== ST_MORE) throw new Error(`status ${f.status.toString(16)}`);
    parts.push(f.payload.subarray(1));                      // each chunk repeats the index byte
    if (f.status === ST_LAST) break;
    flags = 0x01;                                            // continue
  }
  const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out;
}

/** Chunked REMAP write (30/1004, 30/100e, 30/100c): [index] + 241-byte slices, byte 3 counts down. */
export async function writeStore(link: CreateLink, subcmd: number, index: number,
  records: Uint8Array, maxFrames?: number): Promise<void> {
  const slices: Uint8Array[] = [];
  for (let i = 0; i < records.length; i += SLICE) slices.push(records.subarray(i, i + SLICE));
  if (slices.length === 0) slices.push(new Uint8Array(0));
  if (maxFrames !== undefined && slices.length > maxFrames) throw new Error("split on record boundaries first");
  for (let k = 0; k < slices.length; k++) {
    const remaining = slices.length - 1 - k;
    const payload = new Uint8Array(1 + slices[k].length);
    payload[0] = index;
    payload.set(slices[k], 1);
    const f = await link.send(0x30, subcmd, payload, 0, remaining);
    if (f.status === ST_VALUE_REFUSED) throw new Error("the firmware refused a value; nothing stored");
    const expected = remaining ? ST_MORE : ST_LAST;
    if (f.status !== expected) throw new Error(`frame ${k}: status ${f.status.toString(16)}`);
  }
}

export function keyPress(position: number, usage: number, page = 0x07, mods = 0x00): Uint8Array {
  return Uint8Array.of(position, 0x01, 0x04, usage & 0xff, (usage >> 8) & 0xff, page, mods);
}

export function ledEntry(position: number, hue: number, sat: number): Uint8Array {
  if (hue < 0 || hue > 360 || !((sat >= 0 && sat <= 100) || sat === 150)) throw new RangeError("hue 0-360, sat 0-100 or 150");
  return Uint8Array.of(position, hue & 0xff, hue >> 8, sat);
}

/** ED settings take [target, value] after the flags byte (params 00 <target> <value>);
 *  a short payload is zero-filled. */
export async function ledSetting(link: CreateLink, subcmd: number, value: number, target = 0x00): Promise<Frame> {
  if (subcmd === 0x1013 && (value < 1 || value > 100)) throw new RangeError("ed/1013 0 keeps the key LEDs dark across reboots");
  return link.send(0xed, subcmd, Uint8Array.of(target, value));
}

export async function getTimeouts(link: CreateLink): Promise<[number, number, number]> {
  const p = (await link.send(0xfe, 0x100b)).payload;
  const v = new DataView(p.buffer, p.byteOffset, 12);
  return [v.getUint32(0, true), v.getUint32(4, true), v.getUint32(8, true)];
}

export async function setTimeouts(link: CreateLink, idleMs: number, sleepMs: number, thirdMs = 30000): Promise<[number, number, number]> {
  for (const v of [idleMs, sleepMs]) if (v !== 0 && v < 30000) throw new RangeError("under 30 s is refused");
  if (thirdMs < 30000) throw new RangeError("third field: keep 30 s or more");
  const b = new Uint8Array(12);
  const v = new DataView(b.buffer);
  v.setUint32(0, idleMs, true); v.setUint32(4, sleepMs, true); v.setUint32(8, thirdMs, true);
  const f = await link.send(0xfe, 0x100a, b);
  if (f.status === ST_VALUE_REFUSED) throw new Error("the firmware refused the timeouts");
  return getTimeouts(link);
}

# JavaScript recipes

The same recipes as the [Python page](recipes-python.md), in TypeScript for the browser (Web Serial)
or any byte stream in Node: frame build and parse with the right checksum, a stream reader that
resyncs, a Web Serial link that matches replies to requests, chunked reads and writes, LED settings
and timeouts. The wire bytes are the same whatever the host language, and USB is the only
configuration path: over Bluetooth the keyboard answers no configuration frame.

!!! note "At a glance"
    - Web Serial needs a Chromium-based desktop browser and a page served over HTTPS or localhost.
    - One program per port: quit NayaFlow first; a web page that holds a port can write to the keyboard.
    - The code is MIT, written for this site, and tested offline on 2026-09-23 with Node 25 against the
      vendor's own frames and a fake port. It has not been run against a keyboard in this form.
    - No recipe here resets, formats, flashes or pairs anything.

Download: [`naya-cdc.ts`](../assets/code/naya-cdc.ts) and
[`naya-cdc.test.ts`](../assets/code/naya-cdc.test.ts) (7 offline tests with a fake Web Serial port:
`node --test naya-cdc.test.ts` on Node 23.6 or later, which runs TypeScript directly; Node 22.6 needs `--experimental-strip-types`).

## Where this runs

- Web Serial is available in Chromium-based desktop browsers (Chrome, Edge, Opera), not in Firefox
  or Safari; the page must be served over HTTPS or from localhost, and the user picks the port in a
  browser dialog (filter `usbVendorId: 0x37d1`) <span class="tag inferred">INFERRED</span> (web
  platform documentation; re-check the browser list when you ship).
- In Node, feed the bytes of any serial library into `FrameReader` and write the output of
  `buildFrame`.
- Open with `baudRate: 115200` (nominal on USB CDC) and set DTR and RTS; keep one reader for the life
  of the port and match replies to requests by category and subcommand, dropping anything else (late
  replies, keyscan events) <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>
  (nayactl asserts DTR and RTS[^nx]; the rest is the recipe's design).

## Facts the code relies on

| Fact | Evidence |
|---|---|
| Every frame fact of the Python page applies: layout, size = 3 + payload, checksum from the subcommand high byte to the end of the payload, status byte, 242-byte payload limit. | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> ([Python recipes](recipes-python.md#the-frame)) |
| A reply parses the same way: sender at byte 1, category at byte 4, subcommand at bytes 6-7, status at byte 8 and the payload after it, with the XOR over bytes 6 up to the checksum byte. Every reply starts `aa 50 00` (left) or `aa 51 00` (right), and byte 3 of a chunked read reply counts down the chunks still to come. | <span class="tag static">STATIC</span> (vendor reply `aa 50 00 00 fe 03 10 01 00 11 04`[^nc]) <span class="tag measured">MEASURED</span> (header and countdown: owner's board, 3.41.0, our captures of 2026-09-01 to 2026-09-17; [Transport](../protocol/transport.md#the-frame)) |
| A write ack is status `00` (or `01` on a non-final chunk) followed by the echoed layer index. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-07) |
| `fe/1002` returns `00 00 <major> <minor> <patch>` (3.41.0 = `00 00 03 29 00`). | <span class="tag measured">MEASURED</span> (owner's board) |
| `fa/1001` is SPIFLASH_TEST, the read-only SPI-flash self-test. | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-10) |
| A key write is `30/1004` with `00 <layer>` + records and a layer-echo ack; a single LED entry is `30/100e` with `00 <layer> <KK> <hue lo> <hue hi> <sat>`. | <span class="tag measured">MEASURED</span> (NayaFlow captures, 2026-09-01) |
| `30/100b` is read per module-config slot, not per layer: the index byte selects a slot (slot 0 is a blank template), and layers point at slots through the bay records at positions `0x4a`-`0x51` of each layer. Reading "per layer 0-2" misses profiles in slots above 2. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-02/03) |
| `fe/100b` returns three u32 little-endian milliseconds and `fe/100a` writes them (params `00` + 12 bytes). NayaCore names the fields `idle_time_ms`, `sleep_time_ms`, `sleep_battery_time_ms`; the first is the LED idle timeout (it ran on battery in our test), the third is never changed by NayaFlow and its effect is unidentified. Values under 30 s are refused with status `ea`: report it as "value refused", not as a transport error. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-11) <span class="tag static">STATIC</span>[^nc] |
| `fe/100a` acks with a status byte and no layer echo; it is SET ACTIVITY TIMEOUTS, not a "commit", and NayaFlow sends it on every flash with the current values. | <span class="tag measured">MEASURED</span> (captures, 2026-09-01) <span class="tag static">STATIC</span>[^nc] |
| ED params are `00 <target> <value...>` (target and value after the flags byte); short payloads are zero-filled. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-09/10) |
| The right half has no keymap, LED-map, layer-list or module-config store, so it has nothing to answer `30/10xx` with; on its own port it answers the opener and the system, Bluetooth and module reads. While the halves run different firmware its own port answers the opener and then returns empty payloads; its version can still be read through the left port at `dst 0x51` (Bluetooth reads sent that way answer for the left half). Address REMAP reads and writes to the left only. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0; create-legacy-firmware[^nh-hw]) |

## Bluetooth is not a configuration path

Over Bluetooth on 3.41 the keyboard exposes HID (report protocol), one battery level, device
information and a vendor `0x1234`/`0x5678` pipe that answers no configuration frame; there is no DFU,
SMP or UART service <span class="tag reported">REPORTED</span> (createflow-dongle's
findings[^cfd]). Details on [Bluetooth](../connectivity/bluetooth.md).

## The code

The whole module, verbatim from `naya-cdc.ts` (MIT):

```ts
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
```

## Usage sketch

!!! warning "The last two lines write to the keyboard"
    They change key `0x20` on layer 0 and its color. Read the layer and the LED map first
    (`readStore`), and check `fe/1002` on both halves. Not run against a keyboard in this form.

```ts
const port = await navigator.serial.requestPort({ filters: [{ usbVendorId: 0x37d1 }] });
const link = new CreateLink(port);          // quit NayaFlow first: one program per port
await link.open();
console.log(fwVersion(await link.openSession()));                         // "3.41.0"
const right = await link.send(0xfe, 0x1002, new Uint8Array(0), 0, 0, 1000, RIGHT);  // right half, via the left
const layer0 = await readStore(link, 0x1003, 0);                           // whole layer 0
await writeStore(link, 0x1004, 0, keyPress(0x20, 0x05));                   // 0x20 -> B, layer 0
await writeStore(link, 0x100e, 0, ledEntry(0x20, 120, 100));               // key 0x20 green
```

Web Serial checklist: a Chromium-based desktop browser; HTTPS or localhost; one tab per port; NayaFlow
quit; on firmware 3.28.7 pass `maxFrames = 2` to `writeStore` and split on record boundaries (see the
[Python page](recipes-python.md#writes)).

## Test vectors

The TypeScript passes the same vectors as the [Python page](recipes-python.md#test-vectors): the
vendor opener and version frames, the 3.41.0 version reply, the read and key-write frames, the
resync case, the three-frame LED map write (byte 3 `02 01 00`, sizes `f5 f5 42`), the chunked read
with the continue flag, and the `ed/1013` guard (run 2026-09-23 with Node 25.8, 7 of 7 pass).

## Open questions

- <span class="tag open">OPEN</span> Whether any Bluetooth characteristic accepts configuration on firmware other than 3.41 (none found on 3.41).
- <span class="tag open">OPEN</span> The browser list for Web Serial (re-check before relying on it).

## Sources

[^nc]: NayaFlow 1.25.1 for Windows, `core/NayaCore/NayaCore.exe` (NayaCore 6.11.0): strings (port-detector frames, settings names).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`transport.py`).
[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^cfd]: createflow-dongle, [`docs/findings.md`](https://github.com/mediaandmerch/createflow-dongle/blob/main/docs/findings.md) (Bluetooth measurements on 3.41, September 2026).

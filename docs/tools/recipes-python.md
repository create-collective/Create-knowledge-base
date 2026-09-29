# Python recipes

Minimal, correct Python (pyserial) for the keyboard's binary USB serial protocol: building and
parsing frames, opening a session the way NayaFlow's NayaCore does, reading and writing the chunked
stores, and changing LED settings and timeouts, with the known hazards built in as guards. The one
thing to know: the frame checksum starts at the subcommand, not at the size byte, and every write
is acknowledged whether or not it was applied, so always read back what you wrote.

!!! note "At a glance"
    - One program per port: quit NayaFlow (all three processes) or release OpenFlow's ports first.
    - Read `fe/1002` on **both** halves before any write; the halves can run different firmware.
    - The code is MIT, written for this site, and tested offline on 2026-09-23 against the vendor's own
      frames and captured frame shapes. It has not been run against a keyboard in this form.
    - No recipe here resets, formats, flashes or pairs anything.

Download: [`naya_cdc.py`](../assets/code/naya_cdc.py) (the module) and
[`test_naya_cdc.py`](../assets/code/test_naya_cdc.py) (16 offline tests, no keyboard and no
pyserial needed: `python test_naya_cdc.py`).

## Before you start

- **One owner per port.** While NayaFlow runs, its NayaCore service holds every Create port; a
  second program gets "Access is denied" on Windows <span class="tag measured">MEASURED</span> (owner's machine, 3.41.0). See
  [Platforms](platforms.md) for the other operating systems.
- **Serial settings.** Open the port with pyserial's `dsrdtr=False` and a `write_timeout` (2.0 s):
  with DSR flow control Windows blocks the first write forever, because the keyboard never asserts
  DSR. The baud rate is nominal on USB CDC (115200 by convention). Keep one open port for a whole
  job: a tool that reopened the port for every request ran 140 times slower
  <span class="tag measured">MEASURED</span> (owner's machine, Windows, 3.41.0, 2026-09-20; the fix is also in nayactl pull request #2[^nx-pr2]).
- **Check the firmware on both halves** with `fe/1002` on each half's own port, and on the left port
  with destination `0x51` (see [below](#reaching-the-right-half-through-the-left)). A board can arrive
  with the halves on different firmware <span class="tag measured">MEASURED</span>[^nh-hw].

## The frame

Every frame, in both directions, has the same layout <span class="tag static">STATIC</span>
<span class="tag measured">MEASURED</span>:

| Byte | Request | Reply |
|---|---|---|
| 0 | `aa` | `aa` |
| 1 | `00` | the answering half's address (`50` left, `51` right) |
| 2 | destination: `50` left, `51` right | `00` |
| 3 | frames still to come in a chunked write, else `00` | frames still to come in a multi-part read, else `00` |
| 4 | category (`30` REMAP, `be` Bluetooth, `de` module, `ed` LED, `fa` SPI flash, `fe` system) | same |
| 5 | size = 3 + payload length | same |
| 6-7 | subcommand, big-endian (`10 04` for `0x1004`) | same |
| 8 | flags: `00`, or `01` to continue a chunked read | status (table below) |
| 9 ... | payload | payload |
| last - 1 | XOR of bytes 6 to the end of the payload | same |
| last | `04` | `04` |

This site writes the contents of a frame as a **params string** (request) or **reply string**
(reply): every byte from frame byte 8 up to the checksum. `fe/1002` with params `00` is the
request; `00 00 03 29 00` is its reply string. The code keeps byte 8 in `flags` or `status` and
calls the rest `payload`; the full convention is on [Transport](../protocol/transport.md).

- **The checksum excludes the size byte.** NayaCore's own port probe is
  `aa 00 50 00 fe 03 10 01 00 11 04`: `10 ^ 01 ^ 00 = 11`, while a sum that also covered the size
  byte would give `03 ^ 10 ^ 01 ^ 00 = 12` <span class="tag static">STATIC</span>[^nc]. naya-create-kb's
  Python and JavaScript sketches XOR from the size byte, so every frame they build carries a wrong
  checksum; its own parser and its web client compute it correctly[^kb-python].
- **Reply header.** A left reply starts `aa 50 00`, a right reply `aa 51 00`: in our own USB
  captures of NayaFlow 1.25.1 all 396 left replies and all 226 right replies had that header
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, captures of 2026-09-03 and
  2026-09-17), and NayaCore's port detector expects `aa 50 00 00 fe 03 10 01 00 11 04` from a left
  half <span class="tag static">STATIC</span>[^nc]. Also reported by naya-create-kb[^kb-python].
- **Size.** One frame carries at most 243 params bytes: the flags byte plus 242 payload bytes (for a
  chunked store write, the index byte and 241 record bytes) <span class="tag measured">MEASURED</span>
  (NayaFlow captures, 2026-09-01).
- **Reading a stream.** A USB capture shows the IN endpoint one byte per transfer, so read what is
  available, find `aa`, read the size at offset 5, take size + 8 bytes, check the `04` and the
  checksum, and resync one byte on a false start <span class="tag measured">MEASURED</span>
  <span class="tag static">STATIC</span>[^nx-transport].

Reply status (frame byte 8) <span class="tag measured">MEASURED</span> (owner's board 3.41.0; donor board 3.28.7, 2026-09-19):

| Status | Meaning |
|---|---|
| `00` | last or only frame |
| `01` | more to come (also the ack of a non-final chunk of a write) |
| `11` | command not implemented |
| `16` | nothing stored for this read (`18` on a continuation) |
| `ea` | value refused, nothing stored |
| `ff` | with an empty payload: a Bluetooth name that is not set |

## The code

The core of the module, copied verbatim from `naya_cdc.py` (MIT):

```python
# SPDX-License-Identifier: MIT
import struct
import time
from typing import Callable, Iterator, List, NamedTuple, Optional

SOF, EOT = 0xAA, 0x04
LEFT, RIGHT = 0x50, 0x51
MAX_PAYLOAD = 242          # payload bytes per frame after the flags byte
SLICE = 241                # record bytes per frame in a chunked write (index byte first)

ST_LAST, ST_MORE = 0x00, 0x01
ST_UNIMPLEMENTED = 0x11
ST_NOTHING_STORED, ST_NOTHING_STORED_CONT = 0x16, 0x18
ST_VALUE_REFUSED = 0xEA

CAT_REMAP, CAT_MODULE, CAT_LED, CAT_FLASH, CAT_SYSTEM = 0x30, 0xDE, 0xED, 0xFA, 0xFE


def xor8(data: bytes) -> int:
    x = 0
    for b in data:
        x ^= b
    return x


def build_frame(dest: int, category: int, subcmd: int, payload: bytes = b"",
                flags: int = 0x00, remaining: int = 0x00) -> bytes:
    payload = bytes(payload)
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("payload over 242 bytes: split it (see write_store)")
    data = bytes([(subcmd >> 8) & 0xFF, subcmd & 0xFF, flags]) + payload
    header = bytes([SOF, 0x00, dest, remaining, category, len(data)])
    return header + data + bytes([xor8(data), EOT])


class Frame(NamedTuple):
    sender: int
    dest: int
    remaining: int
    category: int
    subcmd: int
    status: int
    payload: bytes


def parse_frame(frame: bytes) -> Frame:
    if len(frame) < 11 or frame[0] != SOF or frame[-1] != EOT:
        raise ValueError("not a frame")
    size = frame[5]
    if size < 3 or len(frame) != size + 8:
        raise ValueError("length does not match the size byte")
    data = frame[6:6 + size]
    if xor8(data) != frame[6 + size]:
        raise ValueError("checksum mismatch")
    return Frame(frame[1], frame[2], frame[3], frame[4],
                 (data[0] << 8) | data[1], data[2], bytes(data[3:]))


def split_stream(buf: bytearray) -> List[bytes]:
    """Remove and return every complete frame at the front of buf; resync on 0xAA."""
    out = []
    while True:
        start = buf.find(bytes([SOF]))
        if start < 0:
            buf.clear()
            return out
        del buf[:start]
        if len(buf) < 6:
            return out
        total = buf[5] + 8
        if len(buf) < total:
            return out
        candidate = bytes(buf[:total])
        if candidate[-1] == EOT and xor8(candidate[6:-2]) == candidate[-2]:
            out.append(candidate)
            del buf[:total]
        else:
            del buf[:1]


class Link:
    """One open CDC port. Hold it for the whole job; do not reopen per request."""

    def __init__(self, port: str, dest: int = LEFT, ser=None):
        self.dest = dest
        if ser is None:
            import serial  # pyserial
            # dsrdtr=False and a write timeout: with DSR flow control Windows blocks the
            # first write forever, because the keyboard never asserts DSR.
            ser = serial.Serial(port, 115200, timeout=0.05,
                                write_timeout=2.0, dsrdtr=False)
            ser.dtr = True
            ser.rts = True
        self.ser = ser
        self.buf = bytearray()

    def close(self) -> None:
        self.ser.close()

    def write(self, frame: bytes) -> None:
        self.ser.write(frame)

    def send(self, category: int, subcmd: int, payload: bytes = b"", flags: int = 0,
             remaining: int = 0, timeout: float = 1.0, dest: Optional[int] = None) -> Frame:
        """Send one frame and wait for the reply with the same category and subcommand.
        dest=RIGHT on the left half's port reaches the right half for the version read;
        Bluetooth reads sent that way answer for the left half. Read the rest on the
        right half's own port."""
        to = self.dest if dest is None else dest
        self.write(build_frame(to, category, subcmd, payload, flags, remaining))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if not chunk:
                continue
            self.buf += chunk
            for raw in split_stream(self.buf):
                f = parse_frame(raw)
                if f.category == category and f.subcmd == subcmd:
                    return f
                # anything else (a late reply, a keyscan event) is dropped here
        raise TimeoutError(f"no reply to {category:02x}/{subcmd:04x}")

    def open_session(self) -> Frame:
        """The opener NayaCore and nayactl use: fe/1001 (media id) then fe/1002 (version)."""
        for wait in (0.3, 0.7, 1.0):
            self.write(build_frame(self.dest, CAT_SYSTEM, 0x1001))
            time.sleep(wait)
            try:
                return self.send(CAT_SYSTEM, 0x1002, timeout=0.5)
            except TimeoutError:
                continue
        raise TimeoutError("no answer to fe/1001 + fe/1002")
```

The module adds the helpers quoted in the sections below (`fw_version`, `kb_battery_mv`,
`module_on_dock`, `spiflash_test`, `read_store`, `keymap_records`, `led_entries`,
`write_store`, `split_on_records`, `key_press`, `led_entry`, `led_setting`, `get_timeouts`,
`set_timeouts`).

## Opening a session

The opener NayaCore and nayactl send is `fe/1001` (MEDIA_ID_REQUEST, which activates the protocol
channel), then `fe/1002` (GET_FW_VERSION), retried with waits of 0.3, 0.7 and 1.0 s
<span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (first two frames of a
NayaFlow capture, 2026-09-01; nayactl's transport[^nx-transport]).

naya-create-kb's `Session` performs a `30/1001` "handshake" and says `30/10xx` needs it on the same
handle <span class="tag reported">REPORTED</span>[^kb-python]; `30/1001` is READ LAYER LIST. That
rule is contradicted per connection: our captures show fresh connections answering `30/1003`,
`30/1009`, `30/100d` and `30/1005` after the session opener alone (`fe/1001`, `fe/1002`), with no
`30/1001` on that connection <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-01). Whether one `30/1001` is needed after power-up is untested; a read-only keyboard check
settles it <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-p02)). The recipes
below open with `fe/1001` and `fe/1002` only; NayaCore also reads `30/1001` before its other REMAP
reads.

## Reading the firmware, battery, module and flash state

```python
def fw_version(reply: Frame) -> str:
    """fe/1002 reply 00 00 03 29 00: status 00, payload 00 major minor patch -> '3.41.0'."""
    major, minor, patch = reply.payload[-3:]
    return f"{major}.{minor}.{patch}"


def kb_battery_mv(link: Link) -> int:
    """fe/1006: the half's own cell in millivolts, big-endian."""
    return int.from_bytes(link.send(CAT_SYSTEM, 0x1006).payload[:2], "big")
```

| Read | Reply string | Evidence |
|---|---|---|
| `fe/1002` firmware version | `00 00 03 29 00` = status `00`, then `00`, major, minor, patch: 3.41.0; followed on the wire by the checksum `38` (`10 ^ 02 ^ 00 ^ 00 ^ 03 ^ 29 ^ 00 = 38`). Another board replied `00 00 03 1e 01` = 3.30.1 | <span class="tag measured">MEASURED</span> (owner's board); nayactl pull request #5[^nx-pr5]; see [Firmware versions](../firmware/versions.md) |
| `fe/1006` the half's own cell | millivolts, big-endian (`[mV hi][mV lo]`) | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0); nayactl `status` |
| `de/1001` module on the dock | `00 01 <address>` when a booted module answers: bit 0 = side, high nibble = type (`10` Touch, `20` Track, `40` Tune; `80` Float unconfirmed); `00 00 f0` when nothing booted answers (`f0`/`f1` = not booted). `de/1002` only says "present" | <span class="tag measured">MEASURED</span> (owner's board 3.41.0; donor board 3.28.7); nayactl pull request #2[^nx-pr2]; [Modules](../protocol/modules.md) |
| `fa/1001` SPIFLASH_TEST | a read-only SPI-flash self-test, not "device info": 2 header bytes, then 6 bytes per partition (state 0 not detected, 1 detected, 2 formatted, 3 mounted, 4 erased, then five return codes); 32 bytes on the left (five partitions), 20 on the right (three) on a healthy 3.41.0 board. Safe as a liveness probe; NayaCore sends it right after the opener | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-10); differs from naya-create-kb, which calls it "device info"[^kb-python] |

## Chunked reads

`30/1003` (layer data), `30/100d` (LED map) and `30/100b` (module config) are read in chunks: send
params `00 <index>`, then `01 <index>` (the continue flag) while the reply status is `01`. Every
reply chunk starts with the index byte again (strip it), and records cross chunk borders. A 3.41.0
layer takes 3 to 4 chunks, and byte 3 of each reply counts the chunks still to come (`03 02 01 00`
for a four-chunk layer) <span class="tag measured">MEASURED</span> (owner's board, 3.41.0; our
captures of 2026-09-03 and 2026-09-17). The read cursor belongs to the open connection.

```python
def read_store(link: Link, subcmd: int, index: int) -> Optional[bytes]:
    """Chunked REMAP read: 30/1003 layer data, 30/100d LED map, 30/100b module config.

    First request flags 00, then flags 01 ("continue") while the reply status is 01.
    Every reply chunk starts with the index byte again; records cross chunk borders.
    The cursor belongs to the open port, so keep one Link for the whole read.
    """
    body = bytearray()
    flags = 0x00
    while True:
        f = link.send(CAT_REMAP, subcmd, bytes([index]), flags=flags)
        if f.status in (ST_NOTHING_STORED, ST_NOTHING_STORED_CONT):
            return None
        if f.status not in (ST_LAST, ST_MORE):
            raise RuntimeError(f"status {f.status:02x} on {subcmd:04x}")
        body += f.payload[1:]
        if f.status == ST_LAST:
            return bytes(body)
        flags = 0x01


def keymap_records(body: bytes) -> Iterator[tuple]:
    """Layer data records: [position][type][len][param...]."""
    i = 0
    while i + 3 <= len(body):
        pos, kind, n = body[i], body[i + 1], body[i + 2]
        yield pos, kind, bytes(body[i + 3:i + 3 + n])
        i += 3 + n


def led_entries(body: bytes) -> Iterator[tuple]:
    """LED map entries: [position][hue u16 LE][saturation]; sat 150 = no color set."""
    for i in range(0, len(body) - 3, 4):
        yield body[i], body[i + 1] | (body[i + 2] << 8), body[i + 3]
```

Layer records are `[position][type][len][param...]`; LED map entries are 4 bytes
`[position][hue lo][hue hi][saturation]` (hue in degrees 0-360, saturation 0-100, 150 = no color
set); a KEY_PRESS param is `[usage lo][usage hi][page][modifier bits]`
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01 to 09-08). Record types
are on [Keymap](../protocol/keymap.md), the LED map on [LEDs](../protocol/led.md). naya-create-kb
reads a layer in "both parts"; a 3.41.0 layer takes 3 to 4 chunks[^kb-python].

## Writes

!!! warning "These recipes write to the keyboard"
    A write replaces stored keymap, LED or module data. Save what you are about to change with
    `read_store` first. On firmware 3.28.7 pass `max_frames=2` and split with `split_on_records`
    (a three-frame write wedges that firmware until the half is unplugged). Tested offline only.

```python
def write_store(link: Link, subcmd: int, index: int, records: bytes,
                max_frames: Optional[int] = None) -> None:
    """Chunked REMAP write: 30/1004 layer data, 30/100e LED map, 30/100c module config.

    Every frame carries [index] + up to 241 record bytes (records may straddle frames);
    byte 3 counts the frames still to come (02 01 00 for three frames).
    Firmware 3.28.7 wedges on any three-frame write: pass max_frames=2 and split first.
    """
    slices = [records[i:i + SLICE] for i in range(0, len(records), SLICE)] or [b""]
    if max_frames is not None and len(slices) > max_frames:
        raise ValueError("too many frames: split on record boundaries first")
    for k, part in enumerate(slices):
        remaining = len(slices) - 1 - k
        f = link.send(CAT_REMAP, subcmd, bytes([index]) + part, remaining=remaining)
        if f.status == ST_VALUE_REFUSED:
            raise ValueError("the firmware refused a value; nothing was stored")
        expected = ST_MORE if remaining else ST_LAST
        if f.status != expected:
            raise RuntimeError(f"frame {k}: status {f.status:02x}, expected {expected:02x}")


def split_on_records(records: bytes, rec_len: Callable[[bytes, int], int],
                     limit: int = 2 * SLICE) -> List[bytes]:
    """Group whole records into writes of at most `limit` bytes (two frames by default)."""
    out, cur, i = [], bytearray(), 0
    while i < len(records):
        n = rec_len(records, i)
        if cur and len(cur) + n > limit:
            out.append(bytes(cur))
            cur = bytearray()
        cur += records[i:i + n]
        i += n
    if cur:
        out.append(bytes(cur))
    return out


def key_press(position: int, usage: int, page: int = 0x07, mods: int = 0x00) -> bytes:
    """A KEY_PRESS record: param = [usage lo][usage hi][page][modifier bits]."""
    return bytes([position, 0x01, 0x04, usage & 0xFF, (usage >> 8) & 0xFF, page, mods])


def led_entry(position: int, hue: int, sat: int) -> bytes:
    if not (0 <= hue <= 360 and (0 <= sat <= 100 or sat == 150)):
        raise ValueError("hue 0-360, saturation 0-100 (150 = no color)")
    return bytes([position, hue & 0xFF, hue >> 8, sat])
```

| Fact | Evidence |
|---|---|
| Writes to the REMAP stores start their payload with the index (layer or slot): `30/1004` params `00 <layer> <records...>`; a sparse write of a few records is normal (NayaFlow sends them). | <span class="tag measured">MEASURED</span> (NayaFlow captures, 2026-09-01) |
| A missing layer byte gives an ack `19 KK` (the device takes KK as the layer) and nothing is applied. | <span class="tag reported">REPORTED</span> by naya-create-kb[^kb-keymap]; a donor-board check is open |
| A write ack echoes the layer (or slot): `00 00` for layer 0, `00 01` for layer 1 (status, then echo). naya-create-kb accepts `00 00` or `00 <layer>`. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-07); also reported by naya-create-kb[^kb-python] |
| A payload bigger than one frame goes out as several frames: each frame's params are `00 <index>` plus a slice of up to 241 record bytes (slices may split records), and byte 3 counts the frames still to come (`02 01 00`). Continuation frames are acked with status `01`, the last with `00`; a writer that accepts only `00` stops after the first frame and leaves the store half written. | <span class="tag measured">MEASURED</span> (NayaFlow captures, 2026-09-01; owner's board, 3.41.0) |
| Firmware 3.28.7 wedges (stops answering and typing until replugged) on any write that needs three frames; two frames are fine. Split on record boundaries into writes of at most 482 record bytes; writes land by record index, so the parts can be sent one after another. | <span class="tag measured">MEASURED</span> (donor board, 3.28.7, 2026-09-19) |
| A single LED entry is one sparse `30/100e` write: params `00 <layer> <KK> <hue lo> <hue hi> <sat>`. The layer byte is mandatory. | <span class="tag measured">MEASURED</span> (NayaFlow capture, 2026-09-01); also reported by naya-create-kb[^kb-python] |
| A write ack means "parsed", not "applied". | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0) |

## LED settings and activity timeouts

!!! warning "Persistent settings"
    `ed/1013` sets a brightness ceiling that survives reboots; value 0 keeps the key LEDs dark while
    every LED command still acks. `led_setting` refuses 0. Timeouts change when the board dims and
    sleeps.

```python
def led_setting(link: Link, subcmd: int, value: int, target: int = 0x00) -> Frame:
    """ED commands take [target, value] after the flags byte (params 00 <target> <value>).
    A one-byte payload is zero-filled by the firmware (value 0), and every ED frame is
    acked, applied or not. ed/1012 scan mode (0/1), ed/1013 max brightness (1-100,
    persistent), ed/1014 LED action override (0 until restart, 1 until layer change),
    ed/1008 brightness now (0-100), ed/1011 effect now."""
    if subcmd == 0x1013 and not 1 <= value <= 100:
        raise ValueError("ed/1013 value 0 keeps the key LEDs dark across reboots")
    return link.send(CAT_LED, subcmd, bytes([target, value]))


def get_timeouts(link: Link) -> tuple:
    """fe/100b: three u32 LE milliseconds (idle, sleep, third field)."""
    return struct.unpack("<3I", link.send(CAT_SYSTEM, 0x100B).payload[:12])


def set_timeouts(link: Link, idle_ms: int, sleep_ms: int, third_ms: int = 30000) -> tuple:
    """fe/100a, then read back with fe/100b as NayaCore does. On 3.41.0 values under
    30 s are refused (status EA); 0 turns idle or sleep off."""
    for v in (idle_ms, sleep_ms):
        if v and v < 30000:
            raise ValueError("under 30 s is refused")
    if third_ms < 30000:
        raise ValueError("third field: keep 30 s or more (0 untested)")
    f = link.send(CAT_SYSTEM, 0x100A, struct.pack("<3I", idle_ms, sleep_ms, third_ms))
    if f.status == ST_VALUE_REFUSED:
        raise ValueError("the firmware refused the timeouts")
    return get_timeouts(link)
```

- ED commands take params `00 <target> <value>`. The target's value made no difference in our tests
  (0, 1, 2, 3 and 200 behaved the same on `ed/1008`); a one-byte payload is zero-filled (the value
  becomes 0); and every ED frame is acked whether or not it applied
  <span class="tag measured">MEASURED</span> (owner's board, left half, 3.41.0, 2026-09-09/10).
  Whether a target such as `ff` reaches the other half is untested by us.
- `ed/1013` sets a persistent maximum brightness (1-100); `ed/1012` is scan-mode PWM (0/1);
  `ed/1014` is the LED action override (0 until restart, 1 until the next layer change)
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-13/16); the ceiling was
  first measured by a nayactl pull request #6 contributor[^nx-pr6]. Details on [LEDs](../protocol/led.md).
- `fe/100a` takes three u32 little-endian millisecond values (idle, sleep, and a third that NayaCore
  calls `sleep_battery_time_ms`), params `00` + 12 bytes; `fe/100b` reads the same 12 bytes back. On
  3.41.0 values under 30 s are refused with status `ea` and nothing is stored; 0 turns idle or sleep
  off. Stock bytes: `90 5f 01 00 e0 93 04 00 30 75 00 00` (90 s, 300 s, 30 s)
  <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board,
  3.41.0, 2026-09-01 and 2026-09-11; NayaCore strings[^nc]). See [Settings and timing](../protocol/settings.md).

## Reaching the right half through the left

The right half's firmware version can be read through the left port with destination `0x51`, even
while the halves run different firmware and the right half's own port returns empty payloads
<span class="tag measured">MEASURED</span>[^nh-hw]. Relaying is partial: Bluetooth identity reads sent
to `0x51` on the left port answer for the left half, so read everything else on each half's own
port. The right half has no REMAP stores of its own: keymaps, LED maps, the layer list and module
configs all live on the left <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-01). Which sender byte a relayed reply carries is <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-c12)).

```python
link = Link("COM7")                                          # or /dev/ttyACM0, /dev/cu.usbmodem...
print(fw_version(link.open_session()))                       # left half, e.g. "3.41.0"
print(fw_version(link.send(CAT_SYSTEM, 0x1002, dest=RIGHT))) # right half, through the left port
```

## Deliberately left out: the factory format

!!! danger "`30/10ca` wipes the keymaps"
    `30/10ca` erases the keymaps, LED maps, layer list and module configs. We give no runnable
    recipe: restoring afterwards is untested by us. Read [Factory reset](../storage/factory-reset.md)
    first, and save the raw layer list and every store before trying it on a donor board.

NayaCore sends `30/10ca` with params `00 00` (frame `aa 00 50 00 30 04 10 ca 00 00 da 04`): in our
disassembly of NayaCore 6.11.0 (macOS and Windows builds), `_remapClearFlash` passes one byte `00`,
built the same way as `30/1001`'s index byte <span class="tag static">STATIC</span>[^nc-mac].
This differs from naya-create-kb, which read the byte array's size argument as its value, so its own tool sends `01`
(`aa 00 50 00 30 03 10 ca 01 db 04`) to the left half, gets status `00`, and afterwards `30/1001`
and `30/1003` answer status `16` (nothing stored) until a profile is written again
<span class="tag reported">REPORTED</span>[^kb-python]. Status `16` as "nothing stored" is ours
<span class="tag measured">MEASURED</span> (donor board, 3.28.7, 2026-09-19). Whether `00 00` and
`01` behave the same stays a donor-board test <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-f16)). NayaFlow's "Clear all keymap data" sends `clear_data`,
which dispatches to ClearAllData and then `30/10ca` <span class="tag static">STATIC</span>[^nc-mac].

No recipe on this page sends `ee/10ae`, `ee/10be`, `ee/10ce`, `fa/1002`, `fa/1006`, `30/10ca` or any
pairing command; see [Recovery](../recovery.md) and [Troubleshooting](../troubleshooting.md) for
the never-send list. A hold-tap flavor byte of 4 or more stops every key until the board is
unplugged (a power cycle) <span class="tag measured">MEASURED</span> (owner's board, 3.41.0): never
sweep hold-tap header bytes.

## The community KB's own recipes

naya-create-kb's Python page describes its own client (`transact(port, dst, type_, c0, c1, params,
timeout)`, `Session(port, dst, timeout)`, `cmd`, `read_layer`, `write_key`; example port
`/dev/cu.usbmodem1101`) and its snapshot and recovery commands (`naya-backup.py`,
`naya-restore.py --snap snap.json` as a dry run and `--apply`, `naya-undark.py --apply`,
`naya-maxbrt.py --level 100 --apply`) <span class="tag reported">REPORTED</span>[^kb-python]
(its published scripts match that description, code read 2026-09-23). Those names
belong to its client, not to this page's code.

## Test vectors

All pass with the module above (`test_naya_cdc.py`, run 2026-09-23):

| Case | Bytes | Source |
|---|---|---|
| opener, left | `aa 00 50 00 fe 03 10 01 00 11 04` | NayaCore's port-detector string |
| opener, right | `aa 00 51 00 fe 03 10 01 00 11 04` | NayaCore's port-detector string |
| version request | `aa 00 50 00 fe 03 10 02 00 12 04` | NayaCore's port-detector string |
| reply "left detected" | `aa 50 00 00 fe 03 10 01 00 11 04` | NayaCore's port-detector string |
| version reply, 3.41.0 | `aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04` | reply string `00 00 03 29 00` framed |
| read layer 0, first | `aa 00 50 00 30 04 10 03 00 00 13 04` | computed |
| read layer 0, continue | `aa 00 50 00 30 04 10 03 01 00 12 04` | computed |
| key write, layer 0, position `0x20` = B | `aa 00 50 00 30 0b 10 04 00 00 20 01 04 05 00 07 00 33 04` | computed; the shape of NayaFlow's captured sparse writes |
| full LED map write (136 entries) | three frames, byte 3 `02 01 00`, size `f5 f5 42` (slices 241, 241, 62) | the shape of a NayaFlow capture |
| stock timeouts | `90 5f 01 00 e0 93 04 00 30 75 00 00` | NayaFlow capture |

## Open questions

- <span class="tag open">OPEN</span> Whether one `30/1001` is needed after power-up; per connection it is not (contradicted by our captures) ([details](../open-questions.md#oq-p02)).
- <span class="tag open">OPEN</span> Whether `30/10ca` with `00 00` (NayaCore, STATIC) and `01` (naya-create-kb's tool) behave the same: a donor-board test ([details](../open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> Whether the third timeout field accepts 0 (the recipe keeps 30 s or more).
- <span class="tag open">OPEN</span> The status bytes for the vendor names Busy, Memory Full, Invalid Format, Save Failed, Load Failed, NVS, No Data and Invalid ID ([Transport](../protocol/transport.md)).

## Sources

[^nc]: NayaFlow 1.25.1 for Windows, `core/NayaCore/NayaCore.exe` (NayaCore 6.11.0): strings (the port-detector frames, status names, settings names).
[^nc-mac]: NayaFlow 1.25.1 for macOS (arm64 and x86_64), `NayaFlow.app/Contents/core/NayaCore.app/Contents/MacOS/NayaCore` (NayaCore 6.11.0): symbols and code of `_remapClearFlash`, `_remapReadLayerList`, `_constructRemapMessages`, the ZMQ dispatcher and `doClearAllDataOperations`; cross-checked on the Windows x64 build. See [Disassembly](../software/disassembly.md).
[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^nx-transport]: nayactl, [`transport.py`](https://github.com/Qonfused/nayactl) (opener retries, stream reader).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (Windows serial settings, module type from the dock address).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) (a board on 3.30.1).
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6) (LED settings; a contributor's measurements).
[^kb-python]: naya-create-kb, [toolkit/python](https://nemezzizz.github.io/naya-create-kb/toolkit/python/).
[^kb-keymap]: naya-create-kb, [protocol/keymap](https://nemezzizz.github.io/naya-create-kb/protocol/keymap/).

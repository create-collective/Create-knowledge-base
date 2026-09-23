# Transport

This page describes how a host talks to a Naya Create half over its USB CDC data port: the frame,
the checksum, addressing, the flag and status bytes, chunked reads and writes, how a session opens,
and what silence means. It also declares the **byte convention** that every protocol and
connectivity page on this site uses. The one thing to know first: every request and every reply is
the same small frame, and the byte just before the final `04` is a checksum, not data.

!!! note "At a glance"
    - One frame: `aa`, two address bytes, a countdown byte, category, LEN, command (2 bytes), a
      flag or status byte, data, an XOR checksum, `04`.
    - `50` is the left half, `51` the right. Only the left half holds keymaps, LED maps, the layer
      list and module configs.
    - Replies start `aa 50 00` (left) or `aa 51 00` (right), and byte 3 of a reply counts down the
      chunks still to come: both measured in our own captures (3.41.0, 2026-09-01 to 2026-09-17).
    - Reads longer than one frame continue with flag `01`; writes longer than one frame re-send the
      index byte in every frame.
    - Nothing on this protocol is a commit: every write takes effect at once and persists.

MEASURED on this page means measured on the owner's board (one Create) unless a source is named;
the firmware version and date follow each tag. Keyboard firmware is written `3.41.0` in prose; the
four-part form the device reports is explained on [Versions](../firmware/versions.md).

## Byte convention

<!--TR-conv-->Every byte string on the protocol and connectivity pages follows these rules.

- A frame is written as lower-case hex bytes separated by spaces, with no `0x`:
  `aa 00 50 00 fe 03 10 02 00 12 04`. A single value in prose may be written `0x50`.
- A command is named `cc/xxxx`: the category byte, then the two command bytes in the order they
  are sent. `fe/1002` is category `fe`, command bytes `10 02`. Command ids repeat across categories
  (see [Command map](commands.md)), so a command is always named with its category.
- **params** (in a request) and **reply** (in a response) mean every byte after the two command
  bytes, up to but not including the checksum. **The first byte of every params or reply string is
  frame byte 8, and it is always shown.** In a request it is the flag byte (`00`, or `01` to
  continue a chunked read); in a reply it is the status byte. So the `fe/1002` reply
  `00 00 03 29 00` is status `00`, then four version bytes.
- The checksum and the `04` terminator appear only in whole-frame examples, and a whole frame shows
  every byte.
- Record bytes inside a params string follow the index byte: `30/1004` params
  `00 01 24 01 04 04 00 07 00` are flag `00`, layer `01`, then one 7-byte record.
- Every length says which count it is: frame bytes, params bytes, reply bytes or record bytes.
- Placeholders: `<addr6>` for a 6-byte Bluetooth address, `<uuid16>` for a 16-byte layer or
  profile id, `<ascii>` for a serial string. Per-device values are never reproduced.

Converting other sources to this convention:

- nayactl's output and most tool code print the bytes **after** the flag byte (nayactl calls it
  `flags`); put the flag byte in front to get this site's form.
- naya-create-kb's REMAP and `fe` request strings already include the flag byte (its
  `[00, layer] + record` is this site's form). Its reply strings include the status byte, but some
  also include the checksum as if it were data (see [the framing trap](#the-framing-trap)). Its `ed`
  strings leave out the flag byte; see [LEDs](led.md) for the framing this site measured.

## The frame

<!--TR-01-->Every binary exchange on the data port is one frame, and the same layout runs in both
directions except for bytes 1 and 2. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01
(NayaFlow 1.25.1 captured on USB) <span class="tag static">STATIC</span>[^nx][^nc] The
naya-create-kb maintainer's published captures have the same layout, with every checksum valid (raw
data checked)[^kb-raw];
naya-create-kb draws it the same way[^kb-transport].

| Offset | This site's name | NayaCore's name | In a request | In a reply |
|---|---|---|---|---|
| 0 | start | header | `aa` | `aa` |
| 1 | sender | sender | `00` (the host) | `50` or `51`, the half that answers |
| 2 | destination | destination | `50` left, `51` right | `00` |
| 3 | countdown | ID | frames still to come in a chunked write; `00` otherwise | chunks still to come in a chunked read reply; `00` otherwise |
| 4 | category | type | `30`, `be`, `ca`, `de`, `ed`, `ee`, `f1`, `fa`, `fe`, `ff` | the same |
| 5 | LEN | length | 2 + params length | 2 + reply length |
| 6-7 | command | command | two bytes, high byte first | the same |
| 8 | flag / status | status | flag `00` (or `01`) | status (see [status values](#flag-and-status-bytes)) |
| 9 to LEN+5 | data | data | parameters | reply data |
| LEN+6 | checksum | checksum ("CRC") | XOR of bytes 6 to LEN+5 | the same |
| LEN+7 | end | EOT | `04` | `04` |

<!--TR-02-->In a request byte 1 is `00` and byte 2 is the destination. In a reply byte 1 is the
address of the half that answers and byte 2 is `00`: a left reply starts `aa 50 00 00` and a right
reply `aa 51 00 00`. All 5 239 replies in our own captures follow this pattern, and NayaCore's port
detector expects the reply `aa 50 00 00 fe 03 10 01 00 11 04`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17
<span class="tag static">STATIC</span>[^nc] Also reported by naya-create-kb[^kb-transport]. (An
earlier note of ours drew the reply as `aa 00 <dest> 00`; that was wrong.)

<!--TR-03-->Destination bytes: `50` is the left half and `51` the right half. nayactl also uses `50`
for the Speedlink dongle, which answers nothing (see [USB](../connectivity/usb.md)).
<span class="tag measured">MEASURED</span> 3.41.0 (`50`, `51`)
<span class="tag static">STATIC</span>[^nx]

<!--TR-04-->NayaCore names eleven fields, in the order it checks a received frame: header, sender,
destination, ID, type, length, command, status, data, checksum, EOT (its log messages include
"Invalid sender received. Trimming packet." and siblings for each). Byte 3 is the vendor's "ID"
and byte 8 its "status". <span class="tag static">STATIC</span>[^nc]

<!--TR-05-->LEN (byte 5) counts every byte from the first command byte through the last data byte,
so LEN = 2 + the params length, where the params include the flag byte. A whole frame is LEN + 8
bytes. The smallest frame, whose params are the flag byte alone, is 11 bytes:
`aa 00 50 00 fe 03 10 01 00 11 04`. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01
<span class="tag static">STATIC</span>[^nx] naya-create-kb says the same (requests of 11 to 12
bytes, LEN = the command bytes plus params)[^kb-transport].

<!--TR-07-->The command travels high byte first: `0x1001` is sent `10 01`. NayaCore keeps it
little-endian in its message structure and writes the high byte first.
<span class="tag static">STATIC</span>[^nx]

<!--TR-08-->Every request carries the flag byte, even with no data: all 795 parameterless requests
in one NayaFlow capture decode as flag `00`, and the vendor's own probe `fe/1001` has LEN `03`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 <span class="tag static">STATIC</span>[^nc]

## Checksum and the framing trap

<!--TR-06-->The checksum is the XOR of every byte from the first command byte through the last data
byte (frame bytes 6 to LEN+5). NayaCore's logs call it a CRC, but it is a plain XOR. The terminator
is always `04`. <span class="tag measured">MEASURED</span> 3.41.0 (every frame of our captures and of
six third-party captures re-checked, 2026-09-23) <span class="tag static">STATIC</span>[^nx]
naya-create-kb checked 269 frames the same way[^kb-transport].

!!! warning "Start the XOR at the command bytes, not at LEN"
    A checksum that includes the LEN byte is wrong for every frame. Two published code sketches
    start their XOR one byte too early; the reference code [below](#reference-encoder-and-parser)
    starts at byte 6.

### The framing trap

<!--TR-41-->The byte just before `04` is the checksum and changes with every payload. Several
published reply strings carry it as if it were data, and each can be checked by XOR:

| Published reply | What it is | Check |
|---|---|---|
| `fe/1002` `00 00 03 29 00 38` | reply `00 00 03 29 00`, checksum `38` | `10 ^ 02 ^ 00 ^ 00 ^ 03 ^ 29 ^ 00` = `38` |
| `be/100f` `00 02 1d` ("BLE firmware 0.2.29") | reply `00 02`, checksum `1d` | `10 ^ 0f ^ 00 ^ 02` = `1d` |
| `be/1002` "8 B" | status + 6 address bytes, plus the checksum | LEN `09` |
| `de/1001` fourth byte "X" | the checksum of `00 01 <addr>` | e.g. `10 ^ 01 ^ 00 ^ 01 ^ 20` = `30` |
| `ed` ack "byte 2 = internal slot id" | the checksum of an empty ack | `10 ^ <C1> ^ 00` (see [Command map](commands.md#ed-led)) |

<span class="tag measured">MEASURED</span> 3.41.0 (our captures show `fe/1002`
`aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04`, `be/100f` `aa 50 00 00 be 04 10 0f 00 02 1d 04` from
both halves, `be/1002` with LEN `09`, 2026-09-01 to 2026-09-17)
<span class="tag inferred">INFERRED</span> (the XOR arithmetic on the published bytes).
naya-create-kb flags the same trap for `de/1008`[^kb-modules].

<!--TR-42-->Several published "payload" sizes are whole-frame sizes. Use this list when a size does
not add up:

| Published size | Command | What it counts |
|---|---|---|
| "43 B" | `fa/1001` (left half) | the whole frame: 8 header bytes + status + 32 data bytes + checksum + `04`; the right half's frame is 31 bytes |
| "72 B" | `30/1001` (three layers) | the whole frame: status, index echo, three 20-byte entries |
| "41 B" | `30/1009` (one stored profile) | the whole frame; 61, 101, 121 and 141 bytes with more profiles |
| "250 B" | `be/100c` | the whole frame (LEN `f2`); the status blob is 239 bytes |

<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17
<span class="tag inferred">INFERRED</span> (arithmetic). The sizes appear as payloads on
naya-create-kb[^kb-transport][^kb-commands].

## Addressing and relaying

<!--TR-31-->Only the left half answers the REMAP category `30` (keymap, LED maps, layer list, module
configs): the right half holds none of those stores, NayaFlow never sends a REMAP frame to `51`,
and a `30/1009` read sent to the right half on 2026-09-01 got no reply.
<span class="tag measured">MEASURED</span> 3.41.0 Also reported by naya-create-kb[^kb-transport]
and by nayactl PR #6 (the right half returns nothing to `30/100d`)[^nx-pr6].

<!--TR-32-->Relaying through the left half is partial. Through the left half's port, `dst 51`
reaches the right half for the firmware-version read: on 2026-09-20 the left port read the right
half's version (3.35.4) while the right half's own port answered only empty payloads (see the hollow
port below). The Bluetooth identity reads `be/1008`, `be/1002` and `be/1005` sent to `51` on the
left port answer for the **left** half. Through the right half's port the left half is not
reachable. <span class="tag measured">MEASURED</span> 2026-09-20, 2026-09-22[^fp-mismatch] OpenFlow
has no automatic retry through this route, but the route itself is measured. naya-create-kb
describes the left half as a full proxy for `51`[^kb-transport]; for these reads it is not.

<!--TR-33-->Which sender byte (byte 1) a `dst 51` reply carries when it comes back through the left
port is not recorded by us. naya-create-kb gives two readings: check the sender, `51` meaning the
right half (its transport page), and replies to `51` arriving with sender `50` (its device
overview)[^kb-transport][^kb-device]. <span class="tag reported">REPORTED</span>
<span class="tag open">OPEN</span> One read of `fe/1002` at `dst 51` with the raw bytes logged
settles it.

<!--TR-34-->A half running different keyboard firmware from its partner has a **hollow port**: it
opens, completes the handshake, accepts every command and answers each with an empty payload, while
it still types. Seen with a newer left half (3.41.0) and an older right half (3.35.4); during that
state the right half still answered the version read at `51` through the left port (3.35.4). Matching
the firmware ends it. <span class="tag measured">MEASURED</span> 2026-09-20[^fp-mismatch] See
[Split link](../connectivity/split-link.md) and [Differences by firmware](firmware-differences.md).

## Flag and status bytes

<!--TR-09-->Request flag values: `00` is normal, and also "start over" for a chunked read; `01` asks
for the next chunk of a chunked read. NayaCore has never been seen sending another value.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 naya-create-kb calls this byte a
"part" number[^kb-transport]; see [chunked reads](#chunked-reads).

<!--TR-10-->Reply status values seen on the wire:

| Status | Meaning | Where seen | Evidence |
|---|---|---|---|
| `00` | final or only frame; write accepted | everywhere | <span class="tag measured">MEASURED</span> 3.41.0, 3.28.7 |
| `01` | more read chunks follow, or the ack of a non-final write chunk | chunked reads and writes | <span class="tag measured">MEASURED</span> 3.41.0 |
| `11` | command not implemented | macro opcodes and an invented opcode on 3.28.7 (2026-09-19); the one macro-list read captured on 3.41.0 (params `00` only, 2026-09-01) | <span class="tag measured">MEASURED</span> |
| `16` | nothing stored for that index; header-only reply (e.g. an LED-map read of a layer with no map) | 3.28.7 (ours, 2026-09-19); 3.41.0 (third-party capture, raw data checked) | <span class="tag measured">MEASURED</span> <span class="tag reported">REPORTED</span>[^kb-raw] |
| `18` | the same, on a continuation | 3.28.7 | <span class="tag measured">MEASURED</span> |
| `19` | the index does not exist: `30/1003` reads of layers `81`, `e4` and `e5` answered `19 81`, `19 e4`, `19 e5` | 3.41.0, 2026-09-01 | <span class="tag measured">MEASURED</span>; also reported by naya-create-kb for `30/1004` sent without its layer byte[^kb-keymap] |
| `ea` | value refused, nothing stored | `fe/100a` under 30 s; `fe/1007` value `ff` (3.41.0, 2026-09-02 and 2026-09-11) | <span class="tag measured">MEASURED</span> |
| `ff` | no data | `be/1006` with no name set (3.28.7) | <span class="tag measured">MEASURED</span> |

naya-create-kb lists `00` and `16 00`[^kb-transport].

<!--TR-11-->NayaCore's own status names, in table order: Final Packet / Success, Multi Packet /
Continue, Invalid Command, Busy, Memory Full, Invalid Format, Save Failed, Load Failed, NVS, No
Data, Invalid ID, then "Unknown Status: 0x". It retries on Busy. Its error table lists the same
remap errors in the same order (invalid command, busy, memory full, invalid format, save failed,
load failed, NVS, no data, invalid ID). <span class="tag static">STATIC</span>[^nc][^nc-disasm]
Numbering the error names from `11` gives `11` Invalid Command, `12` Busy, `13` Memory Full, `14`
Invalid Format, `15` Save Failed, `16` Load Failed, `17` NVS, `18` No Data, `19` Invalid ID, which
fits all four measured error codes; `12` to `15` and `17` have not been seen.
<span class="tag inferred">INFERRED</span> `ea` and `ff` are outside NayaCore's table.
naya-create-kb lists the names without codes[^kb-transport].

<!--TR-12-->An ack proves that the frame parsed, not that the write took effect. The firmware acks
writes it silently discards (every macro write, a record of unknown type `7e`) and stores
short-parameter records that then do nothing. Verify by reading back, and verify behavior by
pressing the key. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-07 Also reported by
naya-create-kb[^kb-transport].

## Chunked reads

<!--TR-15-->A read longer than one frame: send the read with params `00 <index>`; while the reply
status is `01`, send the same command with params `01 <index>` for the next chunk. Every reply chunk
starts with the index echo; strip it from every chunk after the first and join the chunks by bytes,
because chunks split records. The last chunk has status `00` and is shorter than a full one.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 naya-create-kb describes the same loop
with a "part" byte and a layer echo[^kb-transport].

<!--TR-24-->The first params byte of a read is a continue flag (`00` for the first chunk, `01` for
every later chunk), not a part number: NayaCore never sends `02`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17 (our captures carry only
`00` and `01`; the third-party captures agree, raw data checked[^kb-raw]) naya-create-kb writes
these params as `[part, layer]`[^kb-transport].

<!--TR-14-->Byte 3 of a reply counts the chunks still to come: `03 02 01 00` for a four-chunk layer,
`02 01 00` for an LED map. It is `00` on single replies and on write acks.
<span class="tag measured">MEASURED</span> 3.41.0 (235 non-final chunks in our captures,
2026-09-01 to 2026-09-17) Also reported by naya-create-kb[^kb-transport].

<!--TR-16-->A full read chunk carries LEN `f5`: status, index, then 241 record bytes.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01

<!--TR-17-->Sending `00` again restarts the read at chunk 1, so a reader that never sends `01` sees
only the first chunk (about 35 keys of a layer, or 60 LED entries). The read position belongs to the
open connection: reopening the port or sending the opener again resets it.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01[^nx]

<!--TR-18-->The number of chunks depends on the data. NayaCore read layers 0, 1 and 2 in 4, 3 and 4
frames and each LED map in 3 (3.41.0); a 764-byte layer comes back in 4.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 A third-party capture shows a
772-byte layer in 4 chunks (raw data checked)[^kb-raw]. naya-create-kb's "two parts per layer" holds
only for small layers[^kb-transport].

A layer read, as a sequence (layer 0, 764 record bytes):

| Step | Request params | Reply byte 3 | Reply status and first data byte | Record bytes in this chunk |
|---|---|---|---|---|
| 1 | `00 00` | `03` | `01 00` | 241 |
| 2 | `01 00` | `02` | `01 00` | 241 |
| 3 | `01 00` | `01` | `01 00` | 241 |
| 4 | `01 00` | `00` | `00 00` | 41 |

## Chunked writes

<!--TR-13-->Byte 3 of a request is `00` for a single frame and counts the frames still to come in a
chunked write: a three-frame write goes out with byte 3 = `02`, `01`, `00`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 naya-create-kb draws this byte as a
fixed `00`[^kb-transport].

<!--TR-19-->A write longer than one frame is split: every frame's params are `00 <index>` followed by
the next slice of up to 241 record bytes, so each frame re-sends the index byte and slices can split
records. Byte 3 counts the frames still to come. Each non-final frame is acked with status `01`, the
last with `00`, and the ack data is the index. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01

A captured example: NayaFlow writing a new layer 3.

| Frame | Byte 3 | Params | Ack |
|---|---|---|---|
| 1 | `02` | `00 03` + 241 record bytes (243 params) | `01 03` |
| 2 | `01` | `00 03` + 241 record bytes (243 params) | `01 03` |
| 3 | `00` | `00 03` + 4 record bytes (6 params) | `00 03` |

<!--TR-20-->Frame size limits: a full frame has LEN `f5` (245), is 253 bytes long and carries 243
params (flag, index, 241 record bytes). Two frames therefore carry at most 482 record bytes. Counts
that drop the flag byte and count the index once (nayactl's) say 242 per frame and 483 per two.
NayaCore quotes a "hard limit 257".
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 <span class="tag static">STATIC</span>[^nx-pr6]
naya-create-kb mentions "≤242 B" chunks as a nayactl claim[^kb-led].

<!--TR-21-->Writes apply by record index, so one large write can be sent as several smaller writes of
whole records: LED records 120 to 135 written alone landed exactly there, and a layer written in two
parts read back byte-identical. <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19

<!--TR-22-->Firmware 3.28.7 cannot receive a three-frame write: the half stops answering and typing
until it is unplugged, while two-frame writes land at any index. 3.41.0 accepts NayaFlow's
three-frame writes. <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19; 3.41.0,
2026-09-01 See [Differences by firmware](firmware-differences.md). naya-create-kb reports a
different wedge, from oversized single frames[^kb-led].

!!! danger "Three-frame writes wedge 3.28.7"
    On 3.28.7 any write that needs three frames stops the half (no typing, no answers) until it is
    unplugged. Read `fe/1002` on both halves first, and on every firmware prefer two-frame writes of
    whole records (TR-21). Tested on the owner's donor board, 2026-09-19.

<!--TR-23-->A writer must accept status `01` on continuation acks: a matcher that accepts only `00`
stops at frame 2 and leaves a layer half written. It must also hold the port for every frame of a
chunked write: a status poll every 6 s that slipped between two frames cost one flash its
continuation ack (2026-09-16). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16

<!--TR-25-->Write acks echo the index in their data: a layer write to layer 1 is acked `00 01`, to
layer 2 `00 02`; a layer-list or module-list write is acked `00 00`; a module-config write echoes the
slot. A strict "equals `00 00`" matcher rejects good writes to layers above 0.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17 Also reported by
naya-create-kb[^kb-transport].

## Opening a session and polling

<!--TR-26-->The session opener used by NayaCore and nayactl: open the port (nayactl asserts DTR and
RTS; its reading of NayaCore's setup is 115200 8N1 with DTR and RTS), send `fe/1001` MEDIA ID
REQUEST (params `00`, reply `00`), then `fe/1002` GET FW VERSION. The first connect can take about
1 s, and nayactl retries up to three times, waiting 0.3, 0.7 and 1.0 s.
<span class="tag static">STATIC</span>[^nx] <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01 (NayaCore's opener on the wire)

<!--TR-37-->naya-create-kb advises that the first frame after wake is often lost and should be
retried[^kb-transport]. Our captures agree: in 23 of 30 nayactl connections on 2026-09-01 the first
`fe/1001` on a freshly opened port got no reply and the retry did, with both halves awake on USB;
NayaCore's own connects were answered the first time.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 <span class="tag static">STATIC</span>[^nx]
The same page says that a sleeping half answers nothing at all and must be woken with a key press;
we have not measured a sleeping half. <span class="tag reported">REPORTED</span>[^kb-transport]

<!--TR-27-->NayaCore's port broker sends `fe/1001` to both `50` and `51` to tell left from right,
logs a short reply as "ProtocolCDC ... DEFECTIVE", and, when no binary reply comes, falls back to the
text command `fwvchk` (the retired text channel). <span class="tag static">STATIC</span>[^nc]

<!--TR-45-->When a port gives no binary reply, NayaCore's broker sends a newline, the text command
`fwvchk`, then `keyboard_mode_release_toggle`, and tries `fwvchk` again. It classifies text ports as
SystemCDC, Outdated, Legacy or Manufacturing SystemCDC, accepts text version replies of the forms
`fw_version#N.N.N.N`, `N.N.N.N` or a three-group number, and closes a port it judges an "Outdated
ProtocolCDC". <span class="tag static">STATIC</span>[^nc]

<!--TR-28-->NayaCore's captured connect sequence to the left half: `fe/1001`, `fe/1002`, `fa/1001`,
`be/1008`, `be/1002`, `be/1006`, `be/100f`, `be/100c`, `30/1001` (params `00 00`), `30/1003` for each
layer with the continue loop, `30/1009` (params `00 00`), `30/100b` for slots 0 to 4, `30/100d` for
each layer, `fe/100b`. To the right half: `fe/1001`, `fe/1002`, `fa/1001`, `be/1008`, `be/1002`,
`be/100f`, then module polling. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 The
third-party captures show the same sequence (raw data checked)[^kb-raw].

<!--TR-29-->NayaCore then polls each half every 6 s: the left with `be/100c`, `de/1001`, `de/1008`,
`de/100b` and `fe/1006`; the right with the same except `be/100c`. The keyboard never pushes battery
or module state. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01
<span class="tag static">STATIC</span>[^nc]

<!--TR-46-->NayaCore retries a command that gets the status "Busy" ("'Busy' response received. Trying
to send again") up to a per-command budget ("Max message retries reached"). We have never seen Busy
on the wire. <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span>
(absence, 3.41.0 and 3.28.7)

<!--TR-30-->naya-create-kb states that the `30/10xx` commands answer only after a `30/1001` read on
the same open handle[^kb-transport]. That rule is contradicted per connection: our captures show
fresh connections answering `30/1003`, `30/1009`, `30/100d` and `30/1005` after the session opener
alone (`fe/1001`, `fe/1002`), with no `30/1001` on that connection (full three-layer reads of 4, 3
and 4 chunks followed the opener directly). <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01 Whether one `30/1001` is needed after power-up is untested, because the board had been
read by NayaFlow earlier; a read-only keyboard check settles it. <span class="tag open">OPEN</span>
NayaCore and OpenFlow always read `30/1001` first anyway, and `30/1001` is READ LAYER LIST, not a
dedicated handshake (see [Layers](layers.md)).

<!--TR-38-->The baud rate is nominal on this CDC port: NayaCore opens the bootloader port at
1 000 000 baud, and 115200 reads the same bytes. <span class="tag measured">MEASURED</span>
2026-09-08 naya-create-kb says the same without a basis[^kb-transport].

<!--TR-47-->Timeouts seen in practice: a Bluetooth read that the firmware does not implement costs
the client's whole timeout (about 2.08 s per command in OpenFlow on 3.28.7; caching which commands a
half answers, per serial and firmware, cut a full read from 18.6 s to 6.1 s); a missing module
battery command costs about 1.09 s; a present one answers in about 0.22 s.
<span class="tag measured">MEASURED</span> 3.28.7 and 3.41.0, 2026-09-19

!!! note "Read-only session check"
    The opener and a version read change nothing on the keyboard:
    `aa 00 50 00 fe 03 10 01 00 11 04` (expect `aa 50 00 00 fe 03 10 01 00 11 04`), then
    `aa 00 50 00 fe 03 10 02 00 12 04` (on 3.41.0, expect
    `aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04`). If the first frame gets no answer, send it
    again. Close NayaFlow first: only one program can hold the port (see [USB](../connectivity/usb.md)).

## Empty payloads and silence

<!--TR-35-->Opcodes a half does not implement answer with silence, not an error: on 3.28.7
`be/100c` to `be/100f` return no frame at all; `ff/1000` sent to the left half on 3.41.0 got no frame
back; naya-create-kb also reports no reply to `ff/1003`, `ed/10d1` and `ed/10d2`. A client must time
out rather than wait. <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19;
3.41.0, 2026-09-01 (`ff/1000`) <span class="tag reported">REPORTED</span> (`ff/1003`, `ed/10d1`,
`ed/10d2`)[^kb-commands]

<!--TR-36-->An empty `ed` params string is a write, not a read: short `ed` params are zero-filled
(see [LEDs](led.md)), so probing `ed/1012` to `ed/1014` with empty params writes 0.
<span class="tag measured">MEASURED</span> (zero-fill, 3.41.0, 2026-09-09)
<span class="tag inferred">INFERRED</span> (the `ed/1013` case) naya-create-kb calls such an empty
send a self-targeted read returning a bare ack[^kb-commands][^kb-led]; the ack is real, but there
is no read command, and the probe writes.

<!--TR-43-->Frames can arrive unsolicited: keyscan events (`fe/1009`) stream while keyscan mode is on.
Request-shaped frames inside reply streams are not confirmed. The one in a third-party capture sits
among interleaved log fragments on both ports at the same instant, which points to a logging
artifact <span class="tag inferred">INFERRED</span>[^kb-raw]; a re-decode of all our remaining
captures finds none. Our own 2026-09-01 sighting (on the right half's IN pipe) cannot be re-checked,
because those two capture files no longer exist. <span class="tag open">OPEN</span>

<!--TR-44-->nayactl clears its input buffer before every command it writes, so unsolicited frames
that arrive between commands are thrown away; only its `listen` and `keyscan` modes stream.
<span class="tag static">STATIC</span>[^nx]

## Byte order

<!--TR-40-->Multi-byte fields use both byte orders, by field family:

| Big-endian (high byte first) | Little-endian (low byte first) |
|---|---|
| the command bytes | every REMAP u32 parameter (layer targets, Bluetooth, LED-key and two-word records) |
| `fe/1006` millivolts | the key usage in a key-press record (`[usage lo][usage hi][page][mods]`) |
| both `de/1009` values | the hold-tap term (u16) |
| `de/100b` millivolts | the LED-map hue (u16) |
| `be/100c` fields (revision, interval, latency, supervision timeout) | the `ed/100e` hue (u16) |
| the SMP header's length and group | the three `fe/100a` timeouts (u32) |

<span class="tag measured">MEASURED</span> 3.41.0 <span class="tag static">STATIC</span>
(the `be/100c` connection fields read little-endian would be 1536, 0 and 36865, which are not valid
Bluetooth values). naya-create-kb gives the order of individual fields[^kb-commands].

## The text channel

<!--TR-39-->The same port also takes ASCII text commands ending in CR LF, with parameters after `#`
(the "SystemCDC" channel): `fwvchk`, `dump_settings`, `ble_Address`, `ble_Pair#<addr>`,
`clear_bonds`, `mcuboot_reset`, `manual_fw_update_touch`, `manual_fw_update_track`,
`manual_fw_update_tune`, `keyboard_mode_release_toggle`, `force_touch_start`, `c_module_status`. On
3.41.0 every text command returns zero bytes on both halves (with CR LF, LF or CR, with or without
the binary opener). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01; the nayactl
maintainer saw the same[^nx-pr2] The vendor's notes retire SystemCDC in keyboard firmware 3.31.1 and
NayaCore 6.1.5 <span class="tag doc">DOC</span>[^nh-cl]; nayactl's author used it on 3.30.1
<span class="tag reported">REPORTED</span>[^nx]. naya-create-kb lists `clear_bonds` and
`mcuboot_reset` as never-send commands[^kb-transport]; on current firmware they do nothing.

## Worked frames

All checksums below are computed or captured; none is per-device.

| What | Whole frame |
|---|---|
| `fe/1001` request (left) | `aa 00 50 00 fe 03 10 01 00 11 04` |
| `fe/1001` reply (left) | `aa 50 00 00 fe 03 10 01 00 11 04` |
| `fe/1002` request (left) | `aa 00 50 00 fe 03 10 02 00 12 04` |
| `fe/1002` reply (left, 3.41.0) | `aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04` |
| `30/1003` layer 0, first chunk | `aa 00 50 00 30 04 10 03 00 00 13 04` |
| `30/1003` layer 0, next chunk | `aa 00 50 00 30 04 10 03 01 00 12 04` |
| `30/1004` one key (layer 0, position `20`, key B) | `aa 00 50 00 30 0b 10 04 00 00 20 01 04 05 00 07 00 33 04` |
| `ed/1008` brightness 40 | `aa 00 50 00 ed 05 10 08 00 00 28 30 04` |
| `fe/100a` write ack (status `00`, no data) | `aa 50 00 00 fe 03 10 0a 00 1a 04` |

!!! warning "The `30/1004` and `ed/1008` rows are writes"
    They change the keymap and the brightness at once, with no undo. Read and save what you are
    about to overwrite first (see [Keymap](keymap.md) and [LEDs](led.md)).

## Reference encoder and parser

<!--TR-fig7-->A minimal encoder and parser in this site's convention (params start with the flag
byte). The checksum starts at byte 6, the first command byte. Both snippets were run against the
worked frames above (2026-09-23). Code snippets on this site are MIT-licensed.

=== "Python"

    ```python
    # SPDX-License-Identifier: MIT
    def build_frame(dest: int, category: int, command: int, params: bytes = b"\x00",
                    frames_left: int = 0) -> bytes:
        """params = every byte after C0 C1, flag byte first (this site's convention)."""
        body = bytes([command >> 8, command & 0xFF]) + params
        checksum = 0
        for b in body:                    # XOR from C0 to the last data byte; LEN is not included
            checksum ^= b
        return bytes([0xAA, 0x00, dest, frames_left, category, len(body)]) + body + bytes([checksum, 0x04])


    def parse_frame(frame: bytes) -> dict:
        """Split one received frame; raises ValueError on a bad length, terminator or checksum."""
        if len(frame) < 11 or frame[0] != 0xAA or len(frame) != frame[5] + 8 or frame[-1] != 0x04:
            raise ValueError("not a whole frame")
        checksum = 0
        for b in frame[6:-2]:
            checksum ^= b
        if checksum != frame[-2]:
            raise ValueError("checksum mismatch")
        return {
            "sender": frame[1], "frames_left": frame[3], "category": frame[4],
            "command": (frame[6] << 8) | frame[7],
            "reply": frame[8:-2],         # status byte first, as on this site
        }


    assert build_frame(0x50, 0xFE, 0x1002).hex(" ") == "aa 00 50 00 fe 03 10 02 00 12 04"
    ```

=== "JavaScript"

    ```js
    // SPDX-License-Identifier: MIT
    export function buildFrame(dest, category, command, params = [0x00], framesLeft = 0) {
      // params = every byte after C0 C1, flag byte first (this site's convention)
      const body = [command >> 8, command & 0xff, ...params];
      const checksum = body.reduce((x, b) => x ^ b, 0); // XOR from C0; LEN is not included
      return Uint8Array.from([0xaa, 0x00, dest, framesLeft, category, body.length, ...body, checksum, 0x04]);
    }

    export function parseFrame(frame) {
      if (frame.length < 11 || frame[0] !== 0xaa || frame.length !== frame[5] + 8 ||
          frame[frame.length - 1] !== 0x04) {
        throw new Error("not a whole frame");
      }
      const checksum = frame.slice(6, -2).reduce((x, b) => x ^ b, 0);
      if (checksum !== frame[frame.length - 2]) throw new Error("checksum mismatch");
      return {
        sender: frame[1], framesLeft: frame[3], category: frame[4],
        command: (frame[6] << 8) | frame[7],
        reply: frame.slice(8, -2), // status byte first, as on this site
      };
    }
    ```

For longer recipes (chunked reads, sessions, platform notes) see [Python recipes](../tools/recipes-python.md)
and [JavaScript recipes](../tools/recipes-js.md).

## Safety

- Writing is live: every REMAP write takes effect at once and persists; there is no commit and no
  undo. Read and save what you are about to overwrite first.
- Firmware 3.28.7 wedges on any write that needs three frames (see above). Split large writes into
  two-frame writes of whole records on every firmware, or check `fe/1002` first.
- Hold one port owner for every frame of a chunked write; do not run a second tool, NayaFlow or a
  status poll at the same time.
- Do not probe with empty or short `ed` params: they are zero-filled writes, and a zero `ed/1013`
  darkens the board persistently.
- The never-send list is on [Command map](commands.md#never-send-list); its text-channel entries
  matter only on firmware older than 3.31.1.

## Open questions

- <span class="tag open">OPEN</span> Status codes `12` to `15` and `17`; what `ea` and the `80` data
  byte of naya-create-kb's `30/10ca` reply mean beyond "refused" and "observed"
  ([details](../open-questions.md#oq-p01)).
- <span class="tag open">OPEN</span> Which sender byte a `dst 51` reply carries through the left
  port ([details](../open-questions.md#oq-c12)).
- <span class="tag open">OPEN</span> Whether one `30/1001` is needed after power-up; per connection
  it is not (contradicted by our captures) ([details](../open-questions.md#oq-p02)).
- <span class="tag open">OPEN</span> Our own sighting of a request-shaped frame in a reply stream
  ([details](../open-questions.md#oq-p03)).
- <span class="tag open">OPEN</span> What NayaCore's "hard limit 257" applies to, given a one-byte
  LEN ([details](../open-questions.md#oq-p04)).
- <span class="tag open">OPEN</span> Whether a sleeping half answers at all, and how it is woken
  ([details](../open-questions.md#oq-p25)).

## Sources

[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`protocol.py` frame builder and checksum, `transport.py` opener, retries and buffer handling, `constants.py` categories and addresses, `docs/cdc-wire-format.md` command byte order).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) and its comments (Windows serial fixes; text channel silent on 3.41.0).
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6) (NayaCore 6.11.0 LED table, frame limits, right half silent to `30/100d`).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): frame-field messages, status names, port-broker and retry messages.
[^nc-disasm]: NayaFlow 1.25.1, NayaCore 6.11.0 (Windows x64), our disassembly (2026-09-23): the error-code table ("Remap error is ...").
[^nh-cl]: nayaHistory, vendor release notes, [changelogs/](https://github.com/traviswye/nayaHistory/tree/79eeefb/changelogs) (NayaFlow 1.17.2: SystemCDC retired in keyboard 3.31.1 and NayaCore 6.1.5).
[^fp-mismatch]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Pairing and firmware mismatch"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L369-L384) (commit cdd897c; measured 2026-09-20).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs: NayaFlow 1.25.1 on macOS, keyboard 3.41.0); raw data decoded by us, never copied.
[^kb-transport]: naya-create-kb, [protocol/transport](https://nemezzizz.github.io/naya-create-kb/protocol/transport/) (commit 7668067).
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-keymap]: naya-create-kb, [protocol/keymap](https://nemezzizz.github.io/naya-create-kb/protocol/keymap/) (commit 7668067).
[^kb-led]: naya-create-kb, [protocol/led](https://nemezzizz.github.io/naya-create-kb/protocol/led/) (commit 7668067).
[^kb-modules]: naya-create-kb, [protocol/modules](https://nemezzizz.github.io/naya-create-kb/protocol/modules/) (commit 7668067).
[^kb-device]: naya-create-kb, [device/index](https://nemezzizz.github.io/naya-create-kb/device/) (commit 7668067).

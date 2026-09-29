# Command map

Every known command, by category, with its params and reply in this site's
[byte convention](transport.md#byte-convention) (params and replies always start with the flag or
status byte), what has been measured, what is only named in vendor software, and what must not be
sent. The one thing to know first: every write on this protocol takes effect immediately and
persists; there is no commit and no undo, and several commands drop bonds or wipe stored data.

!!! note "At a glance"
    - Ten categories: `30` REMAP, `be` BLE, `ca` IC CHARGER, `de` MODULE, `ed` LED, `ee` RESET,
      `f1` FIRMWARE, `fa` SPI FLASH, `fe` SYSTEM, `ff` META (host-side only).
    - REMAP (keymap, layer list, LED maps, module configs) is answered by the left half only.
    - `ed` params are `00 <target> <values>`; short params are zero-filled, so a short `ed/1013`
      writes a brightness ceiling of 0.
    - Several published reply bytes are checksums read as data; see
      [the framing trap](transport.md#the-framing-trap).
    - The never-send list is at the [end of this page](#never-send-list).

MEASURED on this page means measured on the owner's board (one Create) unless a source is named;
firmware and date follow the tag. Firmware is 3.41.0 unless a row says otherwise.

## How to read the tables

<!--CM-01-->There are ten categories (frame byte 4): `30` REMAP, `be` BLE, `ca` IC CHARGER, `de`
MODULE, `ed` LED, `ee` RESET, `f1` FIRMWARE, `fa` SPI FLASH, `fe` SYSTEM, `ff` META. The names come
from nayactl's constants and from NayaCore's log classes (`[IC CHARGER 0x`, `[FIRMWARE 0x`, SYSTEM,
POWER, BLE, SPIFLASH, LED, MODULES, REMAP); NayaCore's own per-category command tables list the
ids in each category except `ca`, `f1` and `ff`. <span class="tag static">STATIC</span>[^nx][^nc][^nc-disasm]
naya-create-kb names the same categories and calls `ca` and `f1` all-unknown[^kb-commands].

<!--CM-02-->Command ids are numbered per category and collide across categories: `10 0a` is WRITE
MODULE CONFIG LIST in REMAP, SET ACTIVITY TIMEOUTS in SYSTEM, MODULE FILE FW VERSION in MODULE,
CLEAR BLE PROFILE in BLE and LEDs GREEN in LED. Always name a command with its category (`30/100a`,
`fe/100a`). <span class="tag static">STATIC</span>[^nx] naya-create-kb uses the same `xx/yyyy`
notation[^kb-commands].

<!--CM-03-->The names used here are the vendor's: NayaCore's log strings, as carried by nayactl,
whose reverse engineering matches NayaCore's worker names one to one. Where the measured meaning
differs from the name, both are given (see [names versus meaning](#names-versus-measured-meaning)).
<span class="tag static">STATIC</span>[^nx][^nc] naya-create-kb reports cross-checking its tables
against NayaCore jump tables and live probes[^kb-commands].

Columns: **Params** and **Reply** follow the byte convention; `<layer>`, `<slot>`, `<target>`
stand for one byte; "named only" means no source we hold sends it and nobody we know of has
measured it.

## `30` REMAP

<!--CM-10-->Odd REMAP ids are reads and the next even id is the paired write; `10ca` is CLEAR ALL
DATA. The whole category is answered by the left half only, and NayaFlow sends every REMAP frame
to `50`. NayaCore's REMAP table holds exactly `1001` to `100e` and `10ca`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 <span class="tag static">STATIC</span>[^nc-disasm]
Also reported by naya-create-kb ("left only")[^kb-commands]; its list of what NayaCore builds
(`1001` to `100e` plus `10ca`) matches NayaCore's table, except that NayaCore never builds the
macro ids `1005` to `1008`.

!!! warning "REMAP writes are live"
    `30/1002`, `30/1004`, `30/1006`, `30/1008`, `30/100a`, `30/100c` and `30/100e` change the
    keyboard at once and persist. Read and save the layer list, every layer, the LED maps and the
    module configs first. `30/10ca` is on the [never-send list](#never-send-list).

| Command | Vendor name | Params | Reply | Evidence |
|---|---|---|---|---|
| <!--CM-11-->`30/1001` | READ LAYER LIST | `00 00` | `00`, the index echo `00`, then one 20-byte entry per layer `[idx][id][animation][10][<uuid16>]`; 62 reply bytes and a 72-byte frame for three layers | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 |
| <!--CM-12-->`30/1002` | WRITE LAYER LIST | `00 00` + only the entries added, replaced or deleted (delete = `[idx] 00 00 00`) | `00 00` | <span class="tag measured">MEASURED</span> NayaFlow 1.25.1, 2026-09-01 and 2026-09-03 |
| <!--CM-13-->`30/1003` | READ LAYER DATA | `00 <layer>`, then `01 <layer>` per further chunk | chunks starting with the layer echo; records on [Keymap](keymap.md) | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-14-->`30/1004` | WRITE LAYER DATA | `00 <layer>` + any number of records `[position][type][len][param]`, sparse or full | `00 <layer>` (`01 <layer>` on non-final chunks) | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 |
| <!--CM-15-->`30/1005` to `30/1008` | READ / WRITE MACRO LIST, READ / WRITE MACRO DATA | see below | see below | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> |
| <!--CM-16-->`30/1009` | READ MODULE CONFIG LIST | `00 00` | `00`, a leading byte, a slot-0 entry `00 00 80 05` + five bytes, then one 20-byte entry per stored profile `[slot][list id][type][10][<uuid16>]` | <span class="tag measured">MEASURED</span> 3.41.0 <span class="tag static">STATIC</span>[^nc-disasm] |
| <!--CM-17-->`30/100a` | WRITE MODULE CONFIG LIST | `00 00` + changed entries: add `00 00 05 05 01 10 <uuid16>` (slot 5, a Track), delete `00 00 05 00 00 00` | `00 00` | <span class="tag measured">MEASURED</span> NayaFlow 1.25.1, 2026-09-03 |
| <!--CM-18-->`30/100b` | READ MODULE CONFIG DATA | `00 <slot>`, then `01 <slot>` | chunked like layer data | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-19-->`30/100c` | WRITE MODULE CONFIG DATA | `00 <slot>` + field records `[field][type][len][value]`, sparse (NayaFlow sends single-field writes such as `00 01 0b 07 00`) or full | `00 <slot>` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02 (written by us and captured from NayaFlow) |
| <!--CM-20-->`30/100d` | READ LED MAP DATA | `00 <layer>`, then `01 <layer>` | 136 four-byte entries per layer (544 record bytes in 241 + 241 + 62); status `16 <layer>` when a layer has no stored map | <span class="tag measured">MEASURED</span> 3.41.0 and 3.28.7 <span class="tag reported">REPORTED</span> (status `16` on 3.41.0, raw data checked)[^kb-raw] |
| <!--CM-21-->`30/100e` | WRITE LED MAP DATA | `00 <layer>` + entries `[led][hue lo][hue hi][sat]`, sparse (`00 00 22 f0 00 64`) or the full map in three chunked frames | `00 <layer>` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 |
| <!--CM-22-->`30/10ca` | CLEAR ALL DATA | NayaCore: `00 00` (naya-create-kb's tool: `01`) | naya-create-kb: `00 80` | <span class="tag static">STATIC</span> (NayaCore's params)[^nc-disasm] <span class="tag reported">REPORTED</span> (the tool's params, the reply, the effect)[^kb-fr] |

Notes on the REMAP rows:

- <!--CM-11b-->`30/1001` is the first REMAP read NayaCore sends, and naya-create-kb calls it a
  handshake[^kb-commands]; it is the layer list (decode on [Layers](layers.md)). The byte after the
  status is the index echo every REMAP read carries. The third-party captures show the same request
  `aa 00 50 00 30 04 10 01 00 00 11 04` and 72-byte replies for three layers (raw data checked)[^kb-raw].
- `30/1002` was captured from NayaFlow in two flashes; naya-create-kb lists it as never observed on
  the wire[^kb-commands].
- `30/1004`: without the layer byte the device reads the first position as a layer number. For
  reads of layers that do not exist our board answers status `19` and the index
  (<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01); naya-create-kb reports the same
  status for a `30/1004` sent without its layer byte, with nothing applied
  (<span class="tag reported">REPORTED</span>, 3.41.0, 2026-09-22)[^kb-keymap]. Captured NayaFlow
  write for layer 1: params `00 01 24 01 04 04 00 07 00 34 01 04 1e 00 07 00`, ack `00 01`.
  naya-create-kb writes the params as `[00, layer, KK] + record` on two pages; its keymap page gives
  the right form[^kb-commands][^kb-keymap].
- <!--CM-15b-->Macros: on 3.41.0 the macro list read answers without ever returning an entry (the
  one read in our captures, sent with params `00` only, answered status `11` with data `00`,
  2026-09-01); the macro data read echoes the index with no body; seven write encodings were all
  acked and nothing was kept (2026-09-07). On 3.28.7 the macro ids answer status `11` (not
  implemented, 2026-09-19). NayaCore never builds them (its REMAP switch has no case for `1005` to
  `1008`) and flashes a macro binding as `07 00` (NONE).
  <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^nc-disasm]
  naya-create-kb agrees that the store is always empty and macros are host-only[^kb-commands].
- <!--CM-16b-->`30/1009`: the 16 bytes of each profile entry are NayaFlow's profile ids, not a
  "profile header/checksum" as naya-create-kb reads its 41-byte frame[^kb-commands]. The slot-0
  entry `00 00 80 05 00 00 00 00 00` read the same in five NayaFlow reads on our board (2026-09-01
  to 2026-09-17); type `80` is NayaCore's 40-field template type. The byte before it read `00` in
  NayaFlow's reads and in the third-party captures. Decode on [Modules](modules.md).
- `30/100a`: incremental like the layer list; naya-create-kb lists it as "write(?)", used only by
  the stock flash[^kb-commands].
- `30/100b`: the index byte is a module-config SLOT, not a layer; naya-create-kb reads it as
  `[part, layer]` with the content "on L1"[^kb-commands].
- `30/100c`: naya-create-kb's commands page lists it as never observed, while its modules page
  reports a live write[^kb-commands][^kb-modules].
- `30/100e`: naya-create-kb documents the single-entry form, which equals our captured sparse
  write[^kb-commands].

<!--CM-22b-->`30/10ca` CLEAR ALL DATA has never been sent by us. NayaCore sends `30/10ca` with
params `00 00` (frame `aa 00 50 00 30 04 10 ca 00 00 da 04`): in our disassembly of NayaCore 6.11.0
(macOS and Windows builds), `_remapClearFlash` passes one byte `00`, built the same way as the index
byte of its `30/1001` read. <span class="tag static">STATIC</span>[^nc-disasm] naya-create-kb's `01`
read the byte array's size argument as its value; its own tool sends `01`
(`aa 00 50 00 30 03 10 ca 01 db 04`: in this site's convention a flag byte `01` and no data), and it
reports status `00` with data `80` and a formatted data partition on 3.41.0.
<span class="tag reported">REPORTED</span>[^kb-fr] Whether `00 00` and `01` behave the same stays a
donor-board test. <span class="tag open">OPEN</span> NayaFlow's "Clear all keymap data" sends
`clear_data`, which dispatches to ClearAllData and then `30/10ca` (CM-121). What it wipes and how to
restore is on [Factory reset](../storage/factory-reset.md).

!!! danger "`30/10ca` formats the keyboard's data partition"
    Reported to wipe the keymaps, LED maps, module configs and the layer list. Never sent by us;
    the restore procedure is untested. Back up everything first and make first attempts on a donor
    board. See [Factory reset](../storage/factory-reset.md).

<!--CM-23-->No REMAP write needs a commit: a `30/1004` write applies at once and persists across a
reboot. `fe/100a` is not a commit (see [Settings and timing](settings.md)).
<span class="tag measured">MEASURED</span> 3.41.0 Also reported by naya-create-kb[^kb-commands].

## `fe` SYSTEM

| Command | Vendor name | Params | Reply | Evidence |
|---|---|---|---|---|
| <!--CM-30-->`fe/1001` | MEDIA ID REQUEST | `00` | `00` (status only); opens the protocol channel | <span class="tag measured">MEASURED</span> 3.41.0[^nx] |
| <!--CM-31-->`fe/1002` | GET FW VERSION | `00` | `00 00 <major> <minor> <patch>`: `00 00 03 29 00` = 3.41.0, `00 00 03 23 04` = 3.35.4, `00 00 03 1e 01` = 3.30.1 | <span class="tag measured">MEASURED</span> 3.41.0, 3.35.4 <span class="tag reported">REPORTED</span> (3.30.1)[^nx-pr5] |
| <!--CM-32-->`fe/1003` | MODULE BATTERY RECOVERY | one data byte, one of two values (not recovered) | never captured | <span class="tag static">STATIC</span>[^nc] |
| <!--CM-33-->`fe/1004` | GET HW ID NUMBER | `00` | `00` + ASCII equal to the half's USB serial string (`<ascii>`) | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-34-->`fe/1005` | SET HOST OS | `00 00` Windows, `00 01` macOS | never sent by us | <span class="tag static">STATIC</span>[^nc] |
| <!--CM-35-->`fe/1006` | GET KB BATTERY LEVEL | `00` | `00 <mV hi> <mV lo>`, the half's own cell, e.g. `00 0f f5` = 4085 mV | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-36-->`fe/1007` | SET RELEASE MODE | `00 00`, `00 01` accepted; `00 ff` refused (`ea`) | `00` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02 <span class="tag static">STATIC</span> |
| <!--CM-37-->`fe/1008` | TOGGLE KEYSCAN MODE | one data byte; nayactl sends `00 01` on, `00 00` off | `00` | <span class="tag static">STATIC</span>[^nx] <span class="tag measured">MEASURED</span> 2026-09-20 |
| <!--CM-38-->`fe/1009` | KEYSCAN EVENT (device to host) | none | `00 <row> <col> <state>` | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> <span class="tag reported">REPORTED</span> (polarity) |
| <!--CM-39-->`fe/100a` | SET ACTIVITY TIMEOUTS | `00` + three u32 little-endian milliseconds | `00` | <span class="tag measured">MEASURED</span> 3.41.0 <span class="tag static">STATIC</span> |
| `fe/100b` | GET ACTIVITY TIMEOUTS | `00` | `00` + the same 12 bytes | <span class="tag measured">MEASURED</span> 3.41.0 |

Notes on the SYSTEM rows:

- `fe/1001` opens the protocol channel; see [opening a session](transport.md#opening-a-session-and-polling).
  naya-create-kb gives the name only[^kb-commands].
- `fe/1002`: naya-create-kb prints the reply as `00 00 03 29 00 38`; the `38` is the
  checksum[^kb-commands]. Our captures show `00 00 03 29 00` from both halves, and so do the
  third-party captures (raw data checked)[^kb-raw]. The 3.30.1 reading is from the nayactl
  maintainer's board, a version in no public release. How the vendor writes versions is on
  [Versions](../firmware/versions.md).
- `fe/1003` is NayaCore's rescue for a critically drained module. NayaCore checks for one data byte
  with one of two values, as for `fe/1007` and `fe/1008`; the values were not recovered, and it was
  never captured or sent by us[^nc]. naya-create-kb gives the name[^kb-commands].
- `fe/1004`: the ASCII string is the same as the USB serial string and NayaCore's hardware id; it is
  per device and never reproduced here[^nx]. naya-create-kb gives the name[^kb-commands].
- `fe/1005` takes one data byte below 2, `00` Windows and `01` macOS, from NayaCore's checks and its
  enum order. <span class="tag static">STATIC</span>[^nc]
- `fe/1006` readings are noisy; nayactl takes the median of five[^nx]. naya-create-kb gives the same
  layout (millivolts, big-endian)[^kb-commands].
- `fe/1007`: on the left half of a 3.41.0 board, toggling produced no new USB interface and no
  re-enumeration. NayaCore checks a two-value enum. NayaCore's captured connect sequence contains no
  `fe/1007`[^nx]. naya-create-kb gives the name[^kb-commands].
- `fe/1008`: NayaCore accepts two values that were not recovered. Keyscan events were read directly
  from a right half that did not type (143 events, 2026-09-20), so they bypass the split link.
  naya-create-kb calls it a one-byte toggle with live key events[^kb-commands].
- <!--CM-38b-->`fe/1009`: "state `00` = press" is nayactl's assumption and naya-create-kb's
  statement[^kb-commands]; no test of ours pins it. NayaCore routes only this id to its integration
  worker. <span class="tag inferred">INFERRED</span>
- `fe/100a` values under 30 s are refused with `ea`. Full detail on
  [Settings and timing](settings.md). naya-create-kb documents both commands[^kb-commands].

!!! warning "`fe/1005`, `fe/1007`, `fe/1008` and `fe/100a` are writes"
    They change the host OS mode, the release mode, the keyscan mode and the activity timeouts.
    `fe/1007` was toggled on 3.41.0 without visible effect; `fe/1005` has never been sent by us.
    `fe/1003` is on the [never-send list](#never-send-list).

## `ed` LED

<!--CM-ed-->Framing, settled for this site (measured 2026-09-09): every `ed` request's params are
`00` (the flag byte), then a TARGET byte, then the command's values. The target's value is ignored,
and short params are zero-filled from the end. Evidence, and how other tools frame it, is on
[LEDs](led.md).

!!! warning "Every `ed` command is a write, including the short ones"
    A short or empty params string is zero-filled, not rejected: `ed/1013` with params `00` sets a
    brightness ceiling of 0, which would leave the keys dark across reboots (the ceiling is stored),
    while still acking normally.
    Keep the restore frame `aa 00 50 00 ed 05 10 13 00 00 64 67 04` (ceiling 100) at hand.

| Command | Vendor name | Params | Effect | Evidence |
|---|---|---|---|---|
| <!--CM-40-->`ed/1003`, `ed/1004`, `ed/1005` | LEDs ON, LEDs OFF, LEDs TOGGLE | `00 <target>` | `ed/1004` with params `00` alone (target zero-filled) switched the board off | <span class="tag measured">MEASURED</span> (`1004`, 3.41.0, 2026-09-09) <span class="tag static">STATIC</span>[^nx-pr6] |
| `ed/100f`, `ed/1010`, `ed/100d` | HALT, RESUME, EFFECT CYCLE | `00 <target>` | named only by us | <span class="tag static">STATIC</span>[^nx-pr6] |
| <!--CM-41-->`ed/1006`, `ed/1007` | INCREMENT, DECREMENT | `00 <target> <amount>`, amount below 101 | not measured | <span class="tag static">STATIC</span>[^nx-pr6] |
| <!--CM-42-->`ed/1008` | ADJUST BRIGHTNESS | `00 <target> <level>`, level 0 to 100 | see below | <span class="tag measured">MEASURED</span> (left half, 3.41.0, 2026-09-09) <span class="tag static">STATIC</span> |
| <!--CM-43-->`ed/1009` to `ed/100c` | RED, GREEN, BLUE, WHITE | not known | untested by anyone we know of | <span class="tag static">STATIC</span>[^nx][^nc] |
| <!--CM-44-->`ed/100e` | HUE SATURATION | `00 <target> <hue lo> <hue hi> <sat>`: hue below 361, saturation below 101 | not measured | <span class="tag static">STATIC</span>[^nx-pr6] |
| <!--CM-45-->`ed/1011` | SELECT EFFECT | `00 <target> <effect>`: 0 solid, 1 breathe, 2 swirl, 3 spectrum | `00 01` (effect zero-filled) left the board solid; `00 00 01` made it breathe | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-09 <span class="tag static">STATIC</span> |
| <!--CM-46-->`ed/1012` | SET SCANMODE PWM | `00 <target> <bool>` | a persistent setting (NayaFlow "LED scan mode", default on); visible only as flicker on camera | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-13 |
| <!--CM-47-->`ed/1013` | SET LED MAX BRIGHTNESS | `00 <target> <1-100>` | a persistent ceiling over the key array | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-13 <span class="tag reported">REPORTED</span> (module LEDs)[^nx-pr6] |
| <!--CM-48-->`ed/1014` | SET LED LAYER OVERRIDE | `00 <target> <0 or 1>` | how long an LED action pressed on a key lasts | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16 <span class="tag reported">REPORTED</span> (right half)[^kb-commands] |
| <!--CM-50-->`ed/1050` | RGB BRIGHTNESS | `00 <target> <r> <g> <b> <brightness>`, brightness below 101 | untested by us | <span class="tag static">STATIC</span>[^nx-pr6] <span class="tag reported">REPORTED</span>[^kb-commands][^kb-led] |
| <!--CM-51-->`ed/10d1`, `ed/10d2` | FORCE LEDs ON, FORCE LEDs OFF | not known | untested by us | <span class="tag static">STATIC</span>[^nc-disasm] <span class="tag reported">REPORTED</span> (silence)[^kb-commands] |

Notes on the LED rows:

- `ed/1003` to `ed/1005`, HALT, RESUME and EFFECT CYCLE take the target only. naya-create-kb
  describes ON, OFF and TOGGLE with the same target byte, EFFECT CYCLE as stepping through solid,
  breathe, swirl and spectrum, and HALT / RESUME as freezing and resuming the animation; the cycle
  order and the freeze are not measured by us <span class="tag reported">REPORTED</span>[^kb-commands].
- `ed/1006` and `ed/1007`: NayaCore requires an amount below 101 (its `_constructLEDMessages`, as
  published in nayactl PR #6)[^nx-pr6]. naya-create-kb gives the range 0 to 100[^kb-commands].
- <!--CM-42b-->`ed/1008`: NayaCore clamps larger values to 100 with a warning. The measured series,
  params as sent: `00 10` off (target `10`, level 0), `00 64` off, `00 00 0f` dim, `00 03 64` full,
  `00 c8 0f` dim. nayactl's command line sends one byte after the flag and documents 0 to 255, so on
  3.41.0 it sets brightness 0[^nx][^nx-pr6]. naya-create-kb gives 0 to 100 and flags nayactl's
  range as wrong[^kb-commands].
- `ed/1009` to `ed/100c` are named by NayaCore and nayactl; nobody we know of has tried them.
- `ed/100e`: the hue is a little-endian u16; naya-create-kb gives the parameters without the byte
  order[^kb-commands].
- `ed/1011`: the effect index uses NayaCore's order (0 solid, 1 breathe, 2 swirl, 3 spectrum), and
  NayaCore requires an index below its effect count. The effect is a runtime state, per half. The
  stored per-layer animation uses a different order (see [Layers](layers.md)). naya-create-kb gives
  the same effect order[^kb-commands].
- `ed/1012` has no meaning given on naya-create-kb[^kb-commands].
- <!--CM-47b-->`ed/1013`: 30 visibly dims the board and 100 restores it, and the value persists
  <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-13. A ceiling of 0 would therefore leave
  the keys dark across reboots while every LED command still acks
  <span class="tag inferred">INFERRED</span>, as the author of nayactl PR #6 reports
  <span class="tag reported">REPORTED</span>[^nx-pr6]; we have never sent 0. Module LEDs are reported to be outside this
  ceiling by the author of nayactl PR #6 and by naya-create-kb; no measurement of ours
  <span class="tag reported">REPORTED</span>[^nx-pr6][^kb-led]. naya-create-kb documents the
  ceiling[^kb-commands].
- <!--CM-48b-->`ed/1014`: 0 = an LED action pressed on a key lasts until the keyboard restarts;
  1 = until the next layer change (NayaFlow's "LED action override", default "until keyboard
  restart"). naya-create-kb saw the left half ack and the right half not answer
  <span class="tag reported">REPORTED</span>[^kb-commands]; we have sent it only to the left half.
- <!--CM-49-->The three settings `ed/1012` to `ed/1014` have no read command: NayaCore 6.11.0
  names every LED command it can send and none of them reads a setting. Their values can only be
  known by writing them. <span class="tag static">STATIC</span>[^nc] Also reported by
  naya-create-kb ("no GET path")[^kb-commands].
- `ed/1050`: naya-create-kb reports it as a global color override that survives a reboot and that
  bulk `30/100e` writes drop back to following the map <span class="tag reported">REPORTED</span>[^kb-commands][^kb-led].
- `ed/10d1` and `ed/10d2`: NayaCore 6.11.0's own LED command table starts with `10d1` and `10d2`,
  and its log names start with FORCE LEDs ON / OFF, so these are the vendor's ids
  <span class="tag static">STATIC</span>[^nc-disasm]. naya-create-kb reports no reply from either
  half <span class="tag reported">REPORTED</span>[^kb-commands]; nayactl names them[^nx].

<!--CM-52-->Every well-formed `ed` frame is acked `00` with no data, whether or not its params made
sense. The byte naya-create-kb calls the "ED ACK byte 2 ... internal slot id"[^kb-transport][^kb-glossary]
is the reply's checksum: for an empty ack the XOR is `10 ^ C1`, which gives exactly its values
(`1013` gives `03`, `1010` gives `00`, `1003` gives `13`, `1012` gives `02`, `1014` gives `04`,
`1050` gives `40`, `1008` gives `18`, `1011` gives `01`).
<span class="tag inferred">INFERRED</span> (arithmetic on its own values)
<span class="tag measured">MEASURED</span> (identical acks, 3.41.0, 2026-09-09)

<!--CM-53-->NayaCore refuses to build an LED command with no target ("Missing or empty target
parameter for LED command"), so NayaFlow never sends empty `ed` params; it clamps out-of-range
values to 100 with a warning. <span class="tag static">STATIC</span>[^nx-pr6]

<!--CM-54-->naya-create-kb reports that ON/OFF and brightness act as separate states: ON does not
relight a board at brightness 0, while INCREMENT does. Untested by us.
<span class="tag reported">REPORTED</span>[^kb-commands]

<!--CM-55-->Brightness and effect commands act on the half they are sent to: the right half stayed
solid while the left breathed. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10

## `be` BLE

!!! danger "`be/1001`, `be/1003`, `be/1004`, `be/100a` and `be/1010` change bonds"
    UNPAIR ALL (`be/1004`) drops every bond on the half, host bonds and the split link alike, and
    CLEAR ALL SPLIT LINKS (`be/1010`) drops the link between the halves. Store both halves' own and
    pair addresses before any of them, and use them only inside the repair sequence on
    [Split link](../connectivity/split-link.md). The read commands in this table are safe.

| Command | Vendor name | Params | Reply | Evidence |
|---|---|---|---|---|
| <!--CM-60-->`be/1001` | SET PAIR ADDRESS | `00 <addr6>` (NayaCore: "1 parameter of 6 bytes") | `00` | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (by hand, 3.35.4, 2026-09-20) |
| <!--CM-61-->`be/1002` | GET PAIR ADDRESS | `00` | `00 <addr6>`: the OTHER half's address (the split-link partner) | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-62-->`be/1003` | UNPAIR PAIR ADDRESS | one 6-byte address | named only | <span class="tag static">STATIC</span>[^nc] |
| <!--CM-63-->`be/1004` | UNPAIR ALL PAIRS | `00` (empty data, INFERRED) | drops every bond on that half | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (as a repair step, 2026-09-20) |
| <!--CM-64-->`be/1005` | GET ALL PAIRS | `00` | `00 <count>` + `<addr6>` per bond; with no host bonded the only entry is the other half | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-65-->`be/1006` | GET BLE NAME | `00` | `00 <len> <ascii>`; the stock name is "DefaultName" (`00 0b` + 11 bytes); status `ff` with no data when no name is set (3.28.7) | <span class="tag measured">MEASURED</span> 3.41.0, 3.28.7 |
| <!--CM-66-->`be/1007` | SET BLE NAME | one parameter shorter than 256 bytes | never sent by us | <span class="tag static">STATIC</span>[^nc] |
| <!--CM-67-->`be/1008` | GET BLE ADDRESS | `00` | `00 <addr6>`: the half's own split-link identity, not the identity a host pairs with | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-68-->`be/1009`, `be/100a` | SELECT BLE PROFILE, CLEAR BLE PROFILE | one data byte, slot below 5 | select slot 1: `aa 00 50 00 be 04 10 09 00 01 18 04` | <span class="tag static">STATIC</span>[^nc] <span class="tag inferred">INFERRED</span> (frame) |
| <!--CM-69-->`be/100b` | SELECT BLE OUT | not known | named only | <span class="tag static">STATIC</span>[^nx] |
| <!--CM-70-->`be/100c` | GET BLE STATUS | `00` | `00` + a 239-byte status blob; answered by the left half, not the right | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-71-->`be/100d` | GET DONGLE ADDR | `00` | the left half returns a stored dongle address (6 bytes; not the dongle's USB serial) | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11 |
| `be/100e` | GET SLOTX ADDR | not known | named only | <span class="tag static">STATIC</span>[^nx] |
| <!--CM-72-->`be/100f` | GET BLE FW VERSION | `00` | `00 02` on both halves: one data byte, BLE version 2 | <span class="tag measured">MEASURED</span> 3.41.0 <span class="tag doc">DOC</span>[^nh-cl] |
| <!--CM-73-->`be/1010` | CLEAR ALL SPLIT LINKS | `00` (empty data, INFERRED) | drops the link record between the halves | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (in the repair, 2026-09-20) |

Notes on the BLE rows:

- `be/1001` is the first step of NayaCore's pairing repair. naya-create-kb names it[^kb-commands].
- `be/1002`: naya-create-kb's "8 B" counts the status byte, the six address bytes and the
  checksum[^kb-commands]; our captures show LEN `09` (status + 6 bytes) from both halves, and so do
  the third-party captures (raw data checked)[^kb-raw].
- `be/1005`, `be/1006`, `be/1007`, `be/1009` to `be/100b`, `be/100d` and `be/100e` are named on
  naya-create-kb as well[^kb-commands]; its description of `be/1006` (`0b` + ASCII) matches ours.
- `be/1009` and `be/100a` refuse other sizes and values: "Invalid parameter size (%1) for
  SEL/CLEAR_BLE_PROFILE, should be 1", "should be less than 5"[^nc].
- `be/100c`: naya-create-kb's "250 B live blob" is the whole frame[^kb-commands]. Decode on
  [Split link](../connectivity/split-link.md) and [Bluetooth](../connectivity/bluetooth.md).
- <!--CM-72b-->`be/100f`: the frame from both halves is `aa 5x 00 00 be 04 10 0f 00 02 1d 04` (LEN
  `04` leaves one data byte); naya-create-kb reads `00 02 1d` as "BLE firmware v0.2.29", but `1d`
  is the checksum[^kb-commands][^kb-ble]. Its note that this is not a battery reading is right. The
  version byte `02` fits the vendor's "BLE v2" (keyboard 3.35.4 onward)[^nh-cl].
- <!--CM-74-->On 3.28.7, `be/100c`, `be/100d`, `be/100e` and `be/100f` return no frame at all on
  either half, while `be/1002`, `be/1005`, `be/1006` and `be/1008` answer.
  <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19

## `de` MODULE

Module commands go to the half the module is docked on; each half answers for its own dock.

!!! danger "`de/1005` and `de/1006` act on the docked module"
    MODULE FWUP starts a module firmware update and RESET MODULE resets the module; neither has been
    sent by us, and an interrupted module update can leave the keyboard's module store partly
    erased. The read commands in this table are safe.

| Command | Vendor name | Params | Reply | Evidence |
|---|---|---|---|---|
| <!--CM-80-->`de/1001` | SEND HANDSHAKE | `00` | `00 01 <addr>` when a booted module answers (`addr` = dock address, type and side); `00 00 f0` (left) or `00 00 f1` (right) with nothing booted in the dock | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-81-->`de/1002` | MODULE DETECT | `00` | `00 01` for ANY docked module (presence only, never the type), `00 00` when empty | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-82-->`de/1003` | CHECK HANDSHAKE | `00` | no reply on either half (3.41.0, 2026-09-01) | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (no reply) |
| <!--CM-83-->`de/1004` | (no name in any source) | not known | not known | <span class="tag static">STATIC</span> (absence) |
| <!--CM-84-->`de/1005` | MODULE FWUP | one data byte: the docked module's type | never sent by us | <span class="tag static">STATIC</span>[^nc] <span class="tag inferred">INFERRED</span> (numbering) |
| <!--CM-85-->`de/1006` | RESET MODULE | empty data (INFERRED) | never sent | <span class="tag static">STATIC</span>[^nc] |
| <!--CM-86-->`de/1007` | GET ADDRESS | `00` | `00 <addr>`, the authoritative dock address | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-87-->`de/1008` | GET MODULE FW VERSION | `00` | `00 <addr> <flag> 00 <major> <minor> <patch>`, e.g. `00 20 00 00 02 03 03` = Track left, 2.3.3 | <span class="tag measured">MEASURED</span> 3.41.0 |
| <!--CM-88-->`de/1009` | GET BATTERY | `00` | `00 <b0> <batt hi> <batt lo> <rail hi> <rail lo>`, both values big-endian in 0.1 mV | <span class="tag measured">MEASURED</span>[^nx-issue4] |
| <!--CM-89-->`de/100a` | MODULE FILE FW VERSION | `00` | left half: `00 00 02 03 03` (2.3.3); the right half does not answer | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16 |
| <!--CM-90-->`de/100b` | GET PRECISE BATTERY LEVEL | `00` | `00 <mV hi> <mV lo> <valid>` (`valid` `00` = good): the module's battery cell in plain millivolts | <span class="tag measured">MEASURED</span> module 2.3.3 |

Notes on the MODULE rows:

- <!--CM-80b-->`de/1001`: send it before other module queries on a connection. Our captures show
  left Tune `00 01 40`, left Track `00 01 20`, right Track `00 01 21`, right Tune `00 01 41`, right
  Touch `00 01 11`. naya-create-kb's fourth byte "X" in its dock table is the frame
  checksum[^kb-modules]; its left-Touch row `00 01 10` is in the third-party captures (raw data
  checked)[^kb-raw]. Decode on [Modules](modules.md).
- `de/1002`: nayactl labeled every module "Touch" until this was fixed upstream[^nx-pr2].
  naya-create-kb gives the name[^kb-commands].
- `de/1003`: NayaCore's string "not implemented on version %1.%2.%3 of CORE" suggests the command
  is version-gated; nayactl sent it to both halves on 2026-09-01 and neither answered.
  naya-create-kb gives the name[^kb-commands].
- `de/1005`: NayaCore requires one parameter ("parameter size should be 1") and falls back to
  AUTO_DETECT on an invalid type; the numbering 1 Touch, 2 Track, 3 Tune is INFERRED.
  naya-create-kb gives the name[^kb-commands].
- `de/1006` and `de/1007` are named on naya-create-kb too[^kb-commands].
- <!--CM-87b-->`de/1008`: the flag byte read `01` with an all-zero version while a module had not
  reported yet. Each half answers for its own dock, the right half included (our captures:
  `00 21 00 00 02 03 03`, `00 11 00 00 02 01 02`); naya-create-kb calls it left-only, and its
  slice `p[3..6]` is `00 02 03 03`[^kb-commands][^kb-modules].
- `de/1009`: `b0` read `00`; `rail` is the USB or Qi charging rail. It works on module 2.1.2, 2.2.2
  and 2.3.3. naya-create-kb's "6 B: [00][batt][usb]" leaves out the `b0` byte[^kb-commands].
- `de/100a` reads the version of the module firmware bundle stored on the keyboard, not the docked
  module's own version. naya-create-kb gives the name[^kb-commands].
- `de/100b` is absent on module 2.1.2 (no data, about 1.09 s of timeout) and 2.2.2 (no reply).
  naya-create-kb reads the value as the module's supply rail; back-to-back readings against
  `de/1009` show it is the cell[^kb-commands][^kb-modules]. Details on [Modules](modules.md).

## `fa`, `ee`, `ff`, `ca` and `f1`

| Command | Vendor name | Params | Reply | Evidence |
|---|---|---|---|---|
| <!--CM-100-->`fa/1001` | SPIFLASH TEST (TEST FLASH) | `00` | `00` + 2 header bytes + 6 bytes per partition (status + five return codes): 32 data bytes on the left (5 partitions), 20 on the right (3) | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10 <span class="tag static">STATIC</span> |
| <!--CM-101-->`fa/1002` | FORMAT PARTITION | one data byte, the partition (INFERRED) | never sent | <span class="tag static">STATIC</span>[^nx] |
| `fa/1006` | ERASE CHIP | not known | never sent | <span class="tag static">STATIC</span>[^nx] |
| <!--CM-102-->`ee/10ae` | MCU BOOT RESET | `00` | the half re-enumerates in MCUboot | <span class="tag measured">MEASURED</span> 2026-09-16, 2026-09-20[^fp-measured] |
| <!--CM-103-->`ee/10be` | DFU RESET | not known | never sent by us | <span class="tag static">STATIC</span>[^nc] |
| `ee/10ce` | NORMAL RESET | `00` | reboots the half | <span class="tag measured">MEASURED</span> (in the pairing repair, 2026-09-20) |
| <!--CM-104-->`ff/1000` to `ff/1003` | WAIT, VERIFY FLASH, ENQUEUE READ LAYERS, GET MODULE INFO IF PRESENT | host-side | `ff/1000` sent to the left half got no reply | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (`ff/1000`, 3.41.0, 2026-09-01) <span class="tag reported">REPORTED</span> (`ff/1003`)[^kb-commands] |
| <!--CM-105-->`ca/xxxx`, `f1/xxxx` | IC CHARGER, FIRMWARE | none known | none known | <span class="tag static">STATIC</span>[^nc] |

Notes:

- `fa/1001` is read-only; its decode belongs to [Flash layout](../storage/flash-layout.md). The
  third-party captures show frames of 43 and 31 bytes (raw data checked)[^kb-raw]. naya-create-kb
  lists it as TEST FLASH on its commands page but as a 43-byte "device info" read on its transport
  page[^kb-commands][^kb-transport]. naya-create-kb agrees that `fa` has exactly these three
  commands and is a danger zone; only `fa/1002` and `fa/1006` are destructive.
- <!--CM-102b-->`ee/10ae`: the half re-enumerates at its MCUboot product id with two CDC ports and
  stays there (over a minute measured, no timeout) until an SMP `os reset` on the port that answers
  SMP (back in the application in about 8 s) or a power cycle (on USB the half's own switch is
  enough, see [USB](../connectivity/usb.md)). It is the first step of every stock firmware update,
  so it is recoverable, but send it only with that exit at hand; the reset to the log port does
  nothing[^fp-measured]. naya-create-kb lists it as never-send[^kb-transport]. Details on
  [Bootloader](../firmware/bootloader.md).
- `ee/10be` DFU RESET has never been sent by us, and no DFU product id has ever been seen.
  `ee/10ce` NORMAL RESET reboots the half and is the last step of NayaCore's pairing repair.
  naya-create-kb calls `ee/10ce` the only software true reboot[^kb-commands]; `ee/10ae` also resets
  the MCU (into MCUboot), SMP `os reset` reboots a half from MCUboot, and on USB the half's switch is
  a reset, so `ee/10ce` is the only command that reboots straight back into the application.
  <span class="tag measured">MEASURED</span> 2026-09-16 to 2026-09-23
- `ff`: these are NayaCore job-queue steps ("WAIT meta command duration %1 ms exceeds max %2 ms,
  clamping"), not device commands; category `ff` is absent from NayaCore's per-category device
  tables[^nc-disasm]. naya-create-kb reports no reply to `ff/1000` and `ff/1003`[^kb-commands]; we
  confirmed it for `ff/1000`.
- `ca` and `f1` are category names only, from NayaCore's log classes; no command is known. Do not
  blind-probe them. naya-create-kb calls them all-unknown groups[^kb-commands].

!!! danger "`fa/1002`, `fa/1006`, `ee/10ae` and `ee/10be`"
    FORMAT PARTITION and ERASE CHIP destroy stored data; nayactl refuses both without `--force`.
    MCU BOOT RESET parks the half in its bootloader until an SMP `os reset` on the right port or a
    power cycle. DFU RESET has an unknown effect. None of these belongs in an experiment on a board
    you rely on.

## Text commands

The retired text channel (`fwvchk`, `clear_bonds`, `mcuboot_reset` and others) is described on
[Transport](transport.md#the-text-channel); on 3.41.0 it answers nothing.

## Host operations that send these commands

These are NayaFlow 1.25.1 / NayaCore 6.11.0 operations; details on
[NayaFlow and NayaCore](../software/nayaflow.md).

<!--CM-120-->NayaFlow's renderer has one device-control path: `POST /rpc/send-nayacore-zmq-message`
with `{"messages": [topic, event, ...frames]}`, the topic always `command`. The UI's events are
`update_create_fw`, `update_module_fw`, `create_pairing_start`, `force_touch_start`,
`force_track_start`, `force_tune_start`, `clear_data`, `repair_flash` and `clear_ble_devices`;
NayaCore also knows `flash_keymap`, `update_keymap`, `start_device_manager`, `close_device_manager`,
`update_fw_files` and `set_handshake_frequency`. <span class="tag static">STATIC</span>[^nf][^nc]
naya-create-kb describes a 15-event list[^kb-fr].

<!--CM-121-->NayaFlow's "Clear all keymap data" (the Danger Zone button) sends `clear_data`, which
dispatches to ClearAllData and then `30/10ca`: NayaCore's dispatcher maps `clear_data` (event 5) to
its clearAllData request, whose chain ends in `doClearAllDataOperations`, which queues `30/10ca`; its
step names are Clearing, ReadData and VerifyDataCleared, and the vendor's text says the board clears
and restarts. <span class="tag static">STATIC</span>[^nf][^nc][^nc-disasm] No USB capture of the
button exists, so the bytes it puts on the wire are still unrecorded
<span class="tag open">OPEN</span>. naya-create-kb's test sent an event named `clear_all_data`, which
is not on the dispatch list, and concluded that a direct frame is the only path[^kb-fr]; the UI's own
event is `clear_data`.

<!--CM-122-->`repair_flash` runs `fa/1001`, then `fa/1002` on the partitions that report errors, a
normal restart and a new self-test; `fa/1006` sits in the same code path. `clear_ble_devices` runs
NayaCore's ClearBLEDevices operation, and `create_pairing_start` runs the pairing repair (`be/1001`,
`be/1010`, `be/1004`, `ee/10ce`; see [Split link](../connectivity/split-link.md)).
<span class="tag static">STATIC</span>[^nc] naya-create-kb says `repair_flash` formats only when the
self-test fails[^kb-littlefs].

<!--CM-123-->NayaFlow's Danger Zone buttons (`repair_flash`, `clear_data`, `clear_ble_devices`) act
without a confirmation dialog, and its Hardware Manager binds Ctrl/Cmd+D to `update_create_fw`,
which flashes both halves when no warning is pending. <span class="tag static">STATIC</span>[^nf]

<!--CM-124-->NayaFlow's keymap flash (`update_keymap`, then `flash_keymap`) reads the board, writes
the layer list, layer data, module config list and data, LED maps and settings as a sparse diff of
its own profile, then reads everything again to verify ("Profile verification FAILED"). It pushes
the host's profile: a board configured elsewhere is overwritten wherever the profiles differ.
<span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01 to 2026-09-17

## Never-send list

<!--CM-nsl-->The site's one never-send list is on
[Troubleshooting](../troubleshooting.md#the-never-send-list); the table below gives the protocol-level
reason behind each command-related entry and agrees with it. naya-create-kb keeps a similar list;
where our evidence differs, the entry says so[^kb-transport].

| Entry | What happens | Severity | Evidence |
|---|---|---|---|
| <!--CM-110-->`30/10ca`, `fa/1002`, `fa/1006`; `be/1004` and `be/1010` outside the repair sequence; `de/1005` and `fe/1003` | formats the data partition (reported); formats a partition; erases the flash chip; drops host bonds and the split link; untested module paths | data loss or bond loss | <span class="tag static">STATIC</span>[^nx] <span class="tag reported">REPORTED</span> (the `30/10ca` effect)[^kb-fr] |
| <!--CM-111-->hold-tap flavor `04` or higher in any hold-tap record | accepted, stored, then every key stops until the board is unplugged; rewriting the record does not help | board stops until replug | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03 |
| <!--CM-112-->any write that needs three frames, on 3.28.7 | the half stops answering and typing until unplugged | board stops until replug | <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19 |
| <!--CM-113-->`ed/1013` with 0, or with short or empty params | the ceiling is stored (30 and 100 persist, measured), so 0 means a key array that stays dark across reboots; short or empty params are zero-filled into 0 | reversible (send 100) | <span class="tag measured">MEASURED</span> (persistence of 30 and 100, 3.41.0, 2026-09-13; zero-fill, 2026-09-09/10) <span class="tag inferred">INFERRED</span> (the effect of 0) <span class="tag reported">REPORTED</span>[^nx-pr6] |
| <!--CM-114-->a `0d` TOGGLE record targeting layer 0 | does not leave the current layer; strands the keyboard until a power cycle; NayaFlow does not offer it | stranded until power cycle | <span class="tag measured">MEASURED</span> 3.41.0 <span class="tag static">STATIC</span>[^nf] |
| <!--CM-115-->BT_OUT pressed on battery with no reachable host | froze the keyboard (typing and layer switching) until a power cycle | stranded until power cycle | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11 |
| <!--CM-116-->`ee/10ae` without an SMP client ready; `ee/10be` ever | parks the half in MCUboot; unknown | recoverable with `os reset`; unknown | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> |
| <!--CM-118-->the text commands `clear_bonds` and `mcuboot_reset` | nothing on 3.41.0 (the text channel is retired); they matter only on 3.30.1 and older | none on current firmware | <span class="tag measured">MEASURED</span> 3.41.0 <span class="tag doc">DOC</span>[^nh-cl] |
| <!--CM-119-->naya-create-kb's LED recovery ladder (its RESUME and RGB phases) sent to the RIGHT half's port | the naya-create-kb maintainer reports that it left the right half and its module fully dark on 3.41.0; a single `ed/1013` sent to the right half's own port was answered and parked nothing (3.35.4 and 3.41.0, 2026-09-20/22); the LEDs of both halves are driven from the left half's stores (see [LEDs](led.md)) | lighting | <span class="tag reported">REPORTED</span> (the ladder)[^kb-raw] <span class="tag measured">MEASURED</span> (the single write) |

<!--CM-110b-->nayactl gates only the five reset, format and erase ids and two text commands;
`30/10ca` and the Bluetooth clears pass through its `raw` command ungated[^nx].

<!--CM-117-->Replaying `fe/100a` bytes is **not** on this list. naya-create-kb warns that replayed
`fe/100a` bytes "wedge the state machine"[^kb-transport]. NayaFlow sends the same `fe/100a` bytes on
every flash, and every later command answered, in our captures (3.41.0, 2026-09-01 and 2026-09-17)
and in the third-party captures (raw data checked)[^kb-raw], so a replay of valid values is not a
hazard in our records; what wedged that board in that session is not known.
<span class="tag measured">MEASURED</span> 3.41.0 <span class="tag reported">REPORTED</span> (the
wedge)

!!! danger "You can damage a half or lose data"
    Every entry above has a measured or reported hazard. Read the page each entry links to, and
    make first attempts on a donor board. `30/10ca` restore is untested by us after a format,
    layer list included; see [Factory reset](../storage/factory-reset.md).

## Names versus measured meaning

<!--CM-fig3-->Some vendor names mislead:

| Command | Name suggests | What it is |
|---|---|---|
| `30/1001` | a handshake (naya-create-kb) | READ LAYER LIST; not required first per connection (see [Transport](transport.md#opening-a-session-and-polling)) |
| `de/100b` | a "precise level" of a supply rail | the module's battery cell voltage in millivolts |
| `de/1002` | module detection | presence only; the type comes from `de/1007` |
| `fa/1001` | a device-info read (naya-create-kb) | the SPI flash self-test |
| `be/100f` | BLE firmware "v0.2.29" (naya-create-kb) | one data byte, `02` |
| `ff/10xx` | device commands | NayaCore job-queue steps |

## Open questions

- <span class="tag open">OPEN</span> `de/1004`; `be/100b`, `be/100e`; `ed/1009` to `ed/100c`; what
  `ed/10d1` and `ed/10d2` do; everything in `ca` and `f1`; the payloads of `fe/1003`, `de/1005`,
  `de/1006`, `be/1004`, `be/1010` and `fa/1002` as NayaCore sends them
  ([details](../open-questions.md#oq-p06)).
- <span class="tag open">OPEN</span> Which two values `fe/1008` accepts, and the meaning and
  polarity of the `fe/1009` bytes ([details](../open-questions.md#oq-p07)).
- <span class="tag open">OPEN</span> Whether `30/10ca` behaves the same with params `00 00`
  (NayaCore) and `01` (naya-create-kb's tool), a donor-board test, and what its `80` reply byte means
  ([details](../open-questions.md#oq-p06)).
- <span class="tag open">OPEN</span> The `de/1008` flag byte (seen `00` and `01`)
  ([details](../open-questions.md#oq-p08)).
- <span class="tag open">OPEN</span> The bytes NayaFlow's `clear_data` button puts on the wire (that
  it runs `30/10ca` is read from NayaCore) ([details](../open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> The effect of `ed/1050`, the cycle order of `ed/100d`, ON versus
  brightness 0, and `ed/1014` on the right half, all reported by naya-create-kb only
  ([details](../open-questions.md#oq-p25)).

## Sources

[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py` command names and `DANGEROUS_COMMANDS`, `cli/led.py`, `cli/keyscan.py`, `transport.py`).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (module type from the dock address; Windows fixes).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) and its comments (a board on 3.30.1 with modules on 2.2.2).
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6) (NayaCore 6.11.0 LED command table and parameter checks; the LED ceiling; module LEDs).
[^nx-issue4]: nayactl, [issue #4](https://github.com/Qonfused/nayactl/issues/4) (module battery samples).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): command log names and categories, parameter checks, job-queue and operation step names.
[^nc-disasm]: NayaFlow 1.25.1, NayaCore 6.11.0 (Windows x64), our disassembly (2026-09-23): the per-category command tables, `ProtocolCDCProcessWorker::_remapStartStep` (the `0x10ca` case and the missing macro cases), `_constructRemapMessages`, the module-config template type.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings (static reading): ZMQ events, Danger Zone texts, the Ctrl/Cmd+D binding, the Toggle target list.
[^nh-cl]: create-legacy-firmware, vendor release notes, [changelogs/](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (NayaFlow 1.17.2: SystemCDC retired; 1.19.1: BLE v2).
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384) (commit cdd897c).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs and a device-state note of 2026-09-22); raw data decoded by us, never copied.
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-transport]: naya-create-kb, [protocol/transport](https://nemezzizz.github.io/naya-create-kb/protocol/transport/) (commit 7668067).
[^kb-keymap]: naya-create-kb, [protocol/keymap](https://nemezzizz.github.io/naya-create-kb/protocol/keymap/) (commit 7668067).
[^kb-led]: naya-create-kb, [protocol/led](https://nemezzizz.github.io/naya-create-kb/protocol/led/) (commit 7668067).
[^kb-modules]: naya-create-kb, [protocol/modules](https://nemezzizz.github.io/naya-create-kb/protocol/modules/) (commit 7668067).
[^kb-ble]: naya-create-kb, [connectivity/ble](https://nemezzizz.github.io/naya-create-kb/connectivity/ble/) (commit 7668067).
[^kb-fr]: naya-create-kb, [storage/factory-reset](https://nemezzizz.github.io/naya-create-kb/storage/factory-reset/) (commit 7668067).
[^kb-littlefs]: naya-create-kb, [storage/littlefs](https://nemezzizz.github.io/naya-create-kb/storage/littlefs/) (commit 7668067).
[^kb-glossary]: naya-create-kb, [glossary](https://nemezzizz.github.io/naya-create-kb/glossary/) (commit 7668067).

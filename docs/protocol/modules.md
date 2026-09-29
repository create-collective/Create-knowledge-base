# Modules on the wire

This page covers how a host finds, identifies and reads a docked module (Touch, Track, Tune; Float
is named but was never released), where module configurations live (the left half's config store:
the list, the slots and the per-layer bays), how NayaFlow creates, changes and removes them, the
battery and firmware-version commands and their units, and the module firmware and recovery paths.
The one thing to know first: every module configuration lives on the LEFT half, whichever half the
module is docked on, and slot numbers are not stable, so a writer must resolve a slot from a fresh
read before it writes. Field-by-field maps are on [Module fields](module-fields.md).

!!! note "At a glance"
    - `de/10xx` module commands go to the half the module is docked on; each half answers for its own dock.
    - The dock address encodes type and side: Touch `10`/`11`, Track `20`/`21`, Tune `40`/`41`; `f0`/`f1` means nothing booted answered.
    - `de/100b` returns the module's battery cell in plain millivolts; `de/1009` returns cell and charging rail in 0.1 mV units.
    - Configs live in numbered slots on the left half; a list says what each slot is; each layer's bay records pick a slot per dock.
    - NayaCore 6.11.0 limits a config to 31 fields (Touch), 15 (Track) or 36 (Tune); the slot-0 template has 40.

Byte strings follow the [byte convention](transport.md#byte-convention): params and replies start
with the flag or status byte. Profile ids are shown as `<uuid16>`; config fields are quoted as
`[field][type][len][value]`.

## Module types and identity

<!--MO-01-->Three module types shipped: Touch, Track and Tune. Float appears unreleased and Query
deprecated or experimental; both still have firmware apps in every module bundle. nayactl's type
table (`0 None, 1 Touch, 2 Track, 3 Tune, 4 Float, 5 Query`) is a naming table, not what any device
byte means <span class="tag static">STATIC</span>[^nx]. Hardware is on [Module dock](../hardware/dock.md),
[Tune](../hardware/tune.md), [Touch](../hardware/touch.md) and [Track](../hardware/track.md).

<!--MO-02-->Module commands (`de/10xx`) go to the half the module is docked on, and each half answers
for its own dock only <span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--MO-03-->Docking or undocking a module re-enumerates that half's USB: an open port handle goes
stale ("device does not recognize the command") and must be reopened, and NayaFlow relaunches itself
when a module is re-docked <span class="tag measured">MEASURED</span> 3.41.0, 2026-09. See
[USB](../connectivity/usb.md).

!!! note "Read-only probe: who is docked"
    `de/1001`, `de/1007`, `de/1008`, `de/1009`, `de/100a` and `de/100b` are reads. Send `de/1001`
    first on each connection, then the others, to the half the module is docked on.

<!--MO-04-->`de/1001` SEND HANDSHAKE must come before the other module queries on a connection. It
replies `00 01 <addr>` when a booted module answers and `00 00 f0` (left) or `00 00 f1` (right) when
nothing booted answers <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17.
The byte that follows the reply in the frame is the checksum, as the byte before `04` always is
(see the framing trap on [Transport](transport.md)); the table shows it separately:

| Dock | Reply | Checksum | Evidence |
|---|---|---|---|
| left, Track | `00 01 20` | `30` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09 |
| left, Touch | `00 01 10` | `00` | <span class="tag reported">REPORTED</span> (address `10`, nayactl)[^nx-pr2] |
| left, Tune | `00 01 40` | `50` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 |
| left, nothing booted | `00 00 f0` | `e1` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09 |
| right, Touch | `00 01 11` | `01` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09 |
| right, Track | `00 01 21` | `31` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 |
| right, Tune | `00 01 41` | `51` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09 |
| right, nothing booted | `00 00 f1` | `e0` | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09 |

The checksum is `10 ^ 01` XOR the three reply bytes, so every value in the third column follows from
the reply <span class="tag inferred">INFERRED</span> (arithmetic).

<!--MO-05-->The dock address encodes type AND side: bit 0 is the side (0 left, 1 right) and the high
nibble is a one-hot type bit: Touch `10`/`11`, Track `20`/`21`, Tune `40`/`41`; Float `80`/`81` is an
unconfirmed placeholder, because nobody had a Float to dock. An `enum << 4` scheme is ruled out (it
would put Tune at `30`). It was confirmed by moving the same modules between halves
<span class="tag measured">MEASURED</span> 3.41.0 and 3.28.7, 2026-09, and on 3.30.1 by the nayactl
maintainer <span class="tag reported">REPORTED</span>[^nx-pr2].

<!--MO-06-->`f0` / `f1` (all type bits set) is not a type. It is what a dock reports when no booted
module answers, for example a module at about 0-1 % battery that draws pogo power but has not booted
(no LEDs, firmware 0.0.0, no battery reading until it charges past about 1 %)
<span class="tag reported">REPORTED</span> (nayactl maintainer, 3.30.1, module 2.2.2)[^nx-pr2]. We see
`00 00 f0` on the left and `00 00 f1` on the right with an empty dock
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09, and `f0` on 3.28.7 as well
<span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19.

<!--MO-07-->`de/1002` MODULE DETECT answers `00 01` for ANY docked module: presence only. The type must
come from the address: `de/1007` GET ADDRESS (reply `00 <addr>`) is the authoritative read. Keying a
type table on the detect byte labels every module "Touch", which was nayactl's bug, fixed upstream in
PR #2[^nx-pr2]. NayaFlow's interrogation uses only the handshake, the firmware version and the precise
battery; there is no get-type command <span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

### Dock addresses

| Module | Left dock | Right dock | Handshake reply (left) | Evidence |
|---|---|---|---|---|
| Touch | `10` | `11` | `00 01 10` | <span class="tag measured">MEASURED</span> (right), <span class="tag reported">REPORTED</span> (left) |
| Track | `20` | `21` | `00 01 20` | <span class="tag measured">MEASURED</span> |
| Tune | `40` | `41` | `00 01 40` | <span class="tag measured">MEASURED</span> |
| Float | `80` | `81` | (never seen) | <span class="tag inferred">INFERRED</span> |
| nothing booted | `f0` | `f1` | `00 00 f0` | <span class="tag measured">MEASURED</span> |

## Firmware versions

<!--MO-08-->`de/1008` GET MODULE FW VERSION replies `00 <addr> <flag> 00 <major> <minor> <patch>`.
The half the module is docked on answers, the right half included: the right
half has answered `00 21 00 00 02 03 03` (Track, 2.3.3), `00 41 00 00 02 03 03` (Tune) and
`00 11 00 00 02 01 02` (Touch, 2.1.2) <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to
2026-09-17. The flag byte read `01` with an all-zero version while the module had not reported yet
(`00 21 01 00 00 00 00`) <span class="tag measured">MEASURED</span> 3.41.0, 2026-09. The byte after
the version in the frame is the checksum, not a reply byte (see [Transport](transport.md#the-framing-trap)). The nayactl maintainer read `00 11 00 00 02 02 02`
(module 2.2.2) <span class="tag reported">REPORTED</span>[^nx-pr5].

<!--MO-09-->Module firmware seen: 2.1.2 (with keyboard 3.28.7, and on a right-docked Touch on our
3.41.0 board, read 2026-09-16), 2.3.3 (the Tune and Track with 3.41.0)
<span class="tag measured">MEASURED</span> 3.41.0 and 3.28.7, 2026-09; 2.2.2 with keyboard 3.30.1 on
the nayactl maintainer's board <span class="tag reported">REPORTED</span>[^nx-pr5]. Cache a module's
firmware per physical half (USB serial) plus address, not per bay: two different boards' Tunes both
read "left, `40`", and a per-bay cache made a board swap inherit the old module's version
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--MO-10-->`de/100a` MODULE FILE FW VERSION is the version of the module firmware bundle stored on the
keyboard (its VERSION file), not the docked module's: the left half answers `00 00 02 03 03` for a
2.3.3 bundle, and the right half, which has no module store, does not answer
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16. NayaCore compares it with `de/1008`
after an update ("Module firmware version image does not match stored module firmware version")
<span class="tag static">STATIC</span>[^nc]. The bundle is on [Module firmware](../firmware/modules.md).

## Battery

<!--MO-20-->`de/100b` GET PRECISE BATTERY LEVEL replies `00 <mV hi> <mV lo> <valid>` (`valid` `00` =
good): the module's battery (cell) voltage in plain millivolts, despite the name. Back to back on
module 2.3.3: Track `de/100b` 4152 mV against `de/1009` battery 4142.3 mV; Tune 4236 against 4257.2 mV,
while `de/1009`'s second value (the charging rail) read 4.6-5.1 V on USB. A transient `00 00 00 01`
(value 0, invalid) was seen once <span class="tag measured">MEASURED</span> 3.41.0, 2026-09[^nx-issue4].

<!--MO-21-->`de/100b` does not exist on module 2.1.2 (no data, about 1.09 s of timeout on every request)
<span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19 or 2.2.2 (no reply)
<span class="tag reported">REPORTED</span> (nayactl maintainer)[^nx]; `de/1009` works on 2.1.2, 2.2.2
and 2.3.3.

<!--MO-22-->`de/1009` GET BATTERY replies `00 <b0> <batt hi> <batt lo> <rail hi> <rail lo>`: both
values big-endian in 0.1 mV; `b0` has read `00`; `rail` is the USB / Qi charging rail. Examples:
Track on 2.3.3 `00 00 a2 37 c8 f6` = 4.1527 V battery, 5.1446 V rail[^nx-issue4]; a Tune on our board
`00 00 a5 fa c5 7f` = 4.2490 V battery, 5.0559 V rail <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-01.

<!--MO-23-->Feeding the millivolt value of `de/100b` into 0.1 mV arithmetic shows every module at 1 %:
a bug that nayactl and OpenFlow both had and both fixed. A value below 10 000 is millivolts
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--MO-24-->Percentages are computed by the host. NayaFlow's module percentage is
`(clamp(mV, 3300, 4200) - 3300) * 100 / 900`, truncated, then clamped to 1-100 %, from the `de/100b`
millivolts <span class="tag static">STATIC</span> (NayaCore 6.11.0)[^nc-batt]: 9 mV per point, 100 %
from 4200 mV. nayactl and OpenFlow use the same 3.3 to 4.2 V scale (nayactl floors, as NayaCore does)
<span class="tag static">STATIC</span>[^nx]. On the same Tune NayaFlow showed 4228 mV as 100 % and
4127 mV as 92 %, where the formula gives 91 %, so NayaFlow's display was probably fed a slightly later
reading <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span> 3.41.0,
2026-09[^nx-issue4]. NayaFlow 1.20.0's notes warn of 5-10 % fluctuation, and module
2.3.3 disabled the module's battery blink "as battery can now be fully read out by NayaFlow"
<span class="tag doc">DOC</span>[^nh-cl][^beta]. See [Power and batteries](../hardware/power.md#percentages).

<!--MO-25-->The keyboard never pushes module state: NayaCore polls each half every 6 s (handshake,
module firmware version, precise battery, keyboard battery; the left also the Bluetooth status), so
battery figures move in steps <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. NayaCore's
`set_handshake_frequency` takes a period in milliseconds ("6000" in its usage string)
<span class="tag static">STATIC</span>[^nc].

<!--X22-->With a dock empty, `de/100b` does not show presence. Our one read with both docks empty
returned `00 00 00 00` on both halves <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01, but the
naya-create-kb maintainer's empty-dock dump shows the left half at `00 10 60 00` (a phantom 4192 mV)
beside a handshake of `00 00 f0`, and the right at `00 00 00 01` <span class="tag reported">REPORTED</span> (raw data
checked)[^kb-raw]. The last byte is the validity flag, so the left's phantom reading passes as valid
while the right's zero is flagged invalid <span class="tag inferred">INFERRED</span> (from the reply layout of
CM-90). The handshake byte is the reliable presence test (MO-04).

| Command | Reply (this site) | Unit | Module firmware that answers | Example |
|---|---|---|---|---|
| `de/100b` | `00 <mV hi> <mV lo> <valid>` | cell, mV | 2.3.3 (not 2.1.2, not 2.2.2) | `00 10 38 00` = 4152 mV |
| `de/1009` | `00 <b0> <batt hi> <batt lo> <rail hi> <rail lo>` | cell and rail, 0.1 mV | 2.1.2, 2.2.2, 2.3.3 | `00 00 a2 37 c8 f6` |
| `fe/1006` | `00 <mV hi> <mV lo>` | the half's own cell, mV | (keyboard) | `00 0f f5` = 4085 mV |

## The config store on the left half

<!--MO-30-->All module configurations live on the LEFT half, whichever half a module is docked on:
NayaFlow sends every module-config write to `50` (the right-docked Track's config included), and the
right half reports no config slots at all <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01.

<!--MO-31-->A module profile is stored in a numbered config SLOT; a separate module config LIST says
what each slot is; and each layer's bay records pick a slot for each dock
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03.

```
config list (30/1009):  slot 0 = template (type 80)   slot 1 = Track <uuid16>   slot 2 = Tune <uuid16> ...
config slots (30/100b): slot N = field records [field][type][len][value] ...
layer data (30/1003):   bay 4a (Touch L) = slot | 78 (inherit base) | 00 (disabled)   ... bay 51 (Float R)
```

<!--MO-32-->`30/1009` READ MODULE CONFIG LIST (params `00 00`) replies: status `00`, a leading byte (the
index echo, `00`), a slot-0 entry `00 00 80 05` plus five bytes (`00 00 00 00 00` on our board), then
one 20-byte entry per stored profile `[slot][list id][type][10][uuid16]`. The list id equals the slot;
the 16 bytes are NayaFlow's profile id (each NayaFlow install writes its own), not a checksum
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17. Type `80` is NayaCore's
template config type <span class="tag static">STATIC</span>[^nc-disasm].

<!--MO-33-->The list entry's type byte: Touch `00`, Track `01`, Tune `02`
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03; `80` is the slot-0 template, which
NayaCore gives 40 fields <span class="tag static">STATIC</span>[^nc-disasm]; Float `03` is
<span class="tag inferred">INFERRED</span> from the bay order, though NayaCore 6.11.0's module-config
code knows only types 0, 1, 2 and `80`. This numbering differs from nayactl's names table (Touch 1).
The device matches a docked module to a config by type and chooses between same-type entries by dock
half.

!!! warning "Config list and config writes are live"
    `30/100a` and `30/100c` take effect at once and persist. Back up the list and every slot first,
    resolve slots from a fresh list read and by content, and never write a short config over a longer
    one without clearing the tail.

<!--MO-34-->`30/100a` WRITE MODULE CONFIG LIST: params `00 00` plus the changed entries; add
`00 00 05 05 01 10 <uuid16>` (slot 5, list id 5, Track), delete `00 00 05 00 00 00`; ack `00 00`. It is
incremental: entries not sent are untouched, and rewriting an occupied slot's entry (new id only)
works. NayaFlow's list writes restore its own profile ids to the slots it touches
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1, 3.41.0, 2026-09-03.

<!--MO-35-->`30/100b` READ MODULE CONFIG DATA: params `00 <slot>` then `01 <slot>`, chunked like layer
data. The index byte is a SLOT, not a layer. Slot 0 is a blank template of 40 empty records
`[field] 00 00`, so a config has at most 40 fields (`00`-`27`); every other slot holds one profile
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--MO-36-->`30/100c` WRITE MODULE CONFIG DATA: params `00 <slot>` plus field records
`[field][type][len][value]` (the key-record shape); ack `00 <slot>`. Writes may be sparse (NayaFlow
sent `00 01 0b 07 00`: slot 1, field `0b` cleared) or full, and they apply live with no commit. Live
writes on our board: the Tune one-finger tap set to B (params `00 02 08 01 04 05 00 07 00`, and the
tap typed B), Track Left button 1 changed from M1 to M2, and the Track Right rotate pair swapped
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02.

<!--MO-37-->The index byte of `30/100c` params is the config SLOT, and the ack echoes it; a
length-changing field write applies (field `08` from a 3-byte empty record to a 7-byte key press)
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02. This differs from naya-create-kb, which reads that
byte as a layer and warns against sending a slot number <span class="tag reported">REPORTED</span>[^kb-modules]; a
writer that sends layer 0 there writes into the slot-0 template <span class="tag inferred">INFERRED</span>.

<!--MO-38-->NayaCore 6.11.0's module-config serializer, in our disassembly: it skips negative indices
and indices at or above `maxSlots`, writes an index below `behaviourSlotStart` as `[f] 01 01 value`,
writes the others with the slot serializer, and takes absent fields from `ModuleConfig::defaultValue`,
whose defaults include the setting values 10, 50, 75 (Tune `06`) and 5 (Tune `05`) and `07` empties
<span class="tag static">STATIC</span>[^nc-disasm]. This matches the measured record forms: one-byte settings are
`01`-type length-1 records and gestures are typed records <span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--MO-39-->Slot numbers are NOT stable: a Tune profile moved from slot 4 to slot 2, and a Track
appeared at slot 4 only after its profile was flashed. A new profile is always given a fresh slot,
never a reused one. Resolve a slot by id from a live list read AND by content, because the list can
mislabel a slot <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03.

<!--MO-40-->Slot ceiling: all 80 slot indices probed answered and returned empty, and the most any
board has shown in use is 5 (OpenFlow reads slots 0-7) <span class="tag measured">MEASURED</span>
3.41.0, 2026-09. NayaCore 6.11.0's per-type limits are FIELD limits, not slot limits:
<span class="tag static">STATIC</span>[^nc-disasm]

| Config type | `maxSlots` (fields) | `behaviourSlotStart` (first gesture field) |
|---|---|---|
| `00` Touch | 31 (`00`-`1e`) | 5 |
| `01` Track | 15 (`00`-`0e`) | 5 |
| `02` Tune | 36 (`00`-`23`) | 8 |
| `80` template (slot 0) | 40 (`00`-`27`) | 40 (no gesture fields) |

<!--MO-41-->A shorter config written over a longer one is not truncated: a 15-field Track written over
a 36-field config left 21 orphaned fields, and the list then named the slot "Track Right" while it
still held the old tail. Check a slot by its shape, not its field count
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

## Bays and the life cycle of a config

!!! warning "Bay records are layer-data writes"
    A bay record written with `30/1004` repoints a dock at another slot at once. Save the layer (its
    bays included) first; a full-layer writer must carry the board's bay bytes through.

<!--MO-50-->Module enablement is per layer and per dock, in the keymap's bay records (`4a` Touch L,
`4b` Touch R, `4c` Track L, `4d` Track R, `4e` Tune L, `4f` Tune R, `50` Float L, `51` Float R): `N` =
use slot N, `78` = inherit from the BASE layer (layer 0), `00` = disabled. Inherit resolves to layer 0,
not to the next lower layer: pressing Track buttons on layer 2 while layer 1 overrode the bay gave
layer 0's clicks. NayaFlow writes explicit slots on layer 0 and usually `78` above (sometimes explicit
slots on higher layers too) <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03. See
[Keymap](keymap.md).

<!--MO-51-->A layer-0 gap in any bay leaves that module unconfigured: it runs its own animation and
answers no gesture <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16.

<!--MO-52-->Side binding: a Track config drives only the side whose bay points at it, so a Track needs a
config for each side to work on both (changing Track Left's button 1 had no effect with the Track
docked right). Eight bays cap what is active on one layer; the stored configs are a larger pool
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02.

<!--MO-53-->**Add.** NayaFlow's add sequence ("layer 1 uses a different Track profile"), captured
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03:

| Step | Command | Params | Ack |
|---|---|---|---|
| 1 | `30/1004` | `00 01 4c 05 00` (layer 1, bay `4c` to slot 5) | `00 01` |
| 2 | `30/100a` | `00 00 05 05 01 10 <uuid16>` (slot 5, Track) | `00 00` |
| 3 | `30/100c` | `00 05` + a full Track config | `00 05` |

<!--MO-54-->**Remove.** NayaFlow 1.25.1 garbage-collects unreferenced profiles unprompted, in this order:
point the bays away, delete the list entry, then blank the slot in full; the board came back
byte-identical to its baseline. Order matters <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-03.

| Step | Command | Params |
|---|---|---|
| 1 | `30/1004` | `00 01 4c 00 00 4f 00 00` (layer 1, bays `4c` and `4f` disabled) |
| 2 | `30/100a` | `00 00 05 00 00 00` (delete slot 5's entry) |
| 3 | `30/100c` | `00 05` + 40 records `[f] 00 00` |

<!--MO-55-->**Change.** NayaFlow's "enable all modules" flash wrote bays `00 00 4a 03 00 4b 03 00 4c 04 00
4f 02 00`, list entries for slot 3 (Touch) and slot 4 (Track), then configs for slots 1, 3 and 4; the
slot-1 write was the four-byte clear `00 01 0b 07 00`, which silently unbound Track Right button 1
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03.

<!--MO-56-->A new config should be templated from a config of the same type already on the device,
because host apps model only part of a config; authoring one from app data alone drops the fields
they do not model <span class="tag inferred">INFERRED</span> from the measured orphan tails (MO-41).

## Module firmware update and recovery

!!! danger "Module update and rescue commands act on the docked module"
    We have run `de/1005` (MODULE FWUP) through NayaFlow and OpenFlow (3.41.0, 2026-09-23). Its type
    byte must match the module: a Tune sent `03` was programmed with the Track's app and stayed dark
    until `02` was forced. One Track update never finished and hung the keyboard until a power cycle.
    `de/1006` (RESET MODULE) and `fe/1003` (MODULE BATTERY RECOVERY) have never been sent by us. A
    module update interrupted midway would leave the keyboard's module partition partly erased
    (INFERRED). First attempts on a donor board. See [Module firmware](../firmware/modules.md).

<!--MO-60-->NayaCore's module update, which we have captured from NayaFlow and repeated with OpenFlow:
with only the LEFT half on USB and the module docked on it, put that half into MCUboot and upload
`FlashMemory.bin` (a 1 MiB LittleFS bundle of encrypted `.sfb` apps, one per module type, with a
VERSION file and `_HASH` sidecars) to SMP image id 4 in 512-byte chunks; the half restarts by itself.
Then send `de/1005` with one byte for the docked module (`01` Touch, `02` Tune, `03` Track); the
keyboard programs the module from its store and restarts, and `de/1008` is compared with `de/100a`.
The upload is skipped when `de/100a` already reports the bundle being installed
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-23[^fp-modules]. Its step names are
`ModuleFW_FileVerification`, `ModuleFW_Update`, `ModuleFW_VersionCheck` and
`ModuleFW_Touch/Track/Tune_Upload` <span class="tag static">STATIC</span>[^nc]. Details are on
[Module firmware](../firmware/modules.md).

<!--MO-60b-->The vendor's rules for a module update: only one Create Left connected; it takes up to
about 7 s (a Tune up to 1 min); a forced update up to about 4 min <span class="tag doc">DOC</span>[^nf].

<!--MO-61-->Vendor notes: a module update failed unless the LED effect was Solid (fixed in keyboard
3.40.4), and NayaCore 6.1.3 handled a corrupted module firmware file
<span class="tag doc">DOC</span>[^beta][^nh-cl].

<!--MO-62-->Module recovery mode is the `06` 401 MODULE_FORCE_CHARGING key (stock System layer,
position 62). It acts only on the half the key is on (bind one per side), puts that half's LEDs out,
force-charges its bay, makes the module non-functional meanwhile, and times out back to normal by
itself; a restart clears it. On 2026-09-19 it brought back an unresponsive Tune and Touch
<span class="tag measured">MEASURED</span> 3.28.7, module 2.1.2, 2026-09-19. Its origin: Kickstarter
update 21 (2025-06-16) described "Battery Zero", a rare bug that could drain modules beyond recovery,
with firmware fixes, minor hardware changes and a recovery mode for drained modules
planned[^ks-21]; the release notes list module recovery support for "battery Zero" in NayaFlow 1.3.8
<span class="tag doc">DOC</span>[^nh-cl]. The record itself is on [Keymap](keymap.md).

<!--MO-63-->`fe/1003` MODULE BATTERY RECOVERY (NayaCore's rescue for a dead module) and `de/1006` RESET
MODULE exist, and NayaCore sends `fe/1003` only with one data byte, `00` (OFF) or `01` (ON) (see
[Command map](commands.md#fe-system)); neither command was captured or sent by us
<span class="tag static">STATIC</span>[^nc].

## Open questions

- <span class="tag open">OPEN</span> The Float's address, list type and bay behavior; the slot-0 list entry's five bytes ([details](../open-questions.md#oq-p23))
- <span class="tag open">OPEN</span> How many config slots the firmware holds (all 80 probed indices answered empty) ([details](../open-questions.md#oq-p15))
- <span class="tag open">OPEN</span> The `de/1008` flag byte; `de/1009` byte `b0`; the transient invalid `de/100b` reading ([details](../open-questions.md#oq-p08))
- <span class="tag open">OPEN</span> `fe/1003` and `de/1006` on the wire as NayaCore sends them ([details](../open-questions.md#oq-p06))
- <span class="tag open">OPEN</span> Why one Track update hung the keyboard and left the Track answering like an empty bay, and whether every half needs a cable replug to come back after a module update's restarts ([details](../open-questions.md#oq-f13))
- <span class="tag open">OPEN</span> Recovery mode on 3.41.0 with module 2.3.3 ([details](../open-questions.md#oq-f22))
- <span class="tag open">OPEN</span> Whether the half cells sag overnight only when the modules are undocked ([details](../open-questions.md#oq-h38))

## Sources

[^kb-modules]: naya-create-kb, [protocol/modules](https://nemezzizz.github.io/naya-create-kb/protocol/modules/) (commit 7668067).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py` module names; module battery decoding).
[^nx-pr2]: nayactl, [pull request 2](https://github.com/Qonfused/nayactl/pull/2) (module address map, the detect-byte fix, the non-booted `f0` value).
[^nx-pr5]: nayactl, [pull request 5](https://github.com/Qonfused/nayactl/pull/5) (readings on keyboard 3.30.1, module 2.2.2).
[^nx-issue4]: nayactl, [issue 4](https://github.com/Qonfused/nayactl/issues/4) (module battery samples and units).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): module update steps and messages, `set_handshake_frequency`, command names.
[^nc-disasm]: NayaFlow 1.25.1, NayaCore 6.11.0 (Windows x64), our disassembly (2026-09-23): `ModuleConfig::maxSlots`, `ModuleConfig::behaviourSlotStart`, `ModuleConfig::defaultValue` and the module-config serializer.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings (static reading): module update instructions.
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs and empty-dock dumps); raw data decoded by us, never copied.
[^nh-cl]: create-legacy-firmware, vendor release notes, [changelogs/](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (v1.3.8, v1.20.0, v1.25.0).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (v1.17.0, v1.23.0, v1.24.0).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^fp-modules]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Module firmware update, captured from NayaFlow (2026-09-23)"](https://github.com/create-collective/create-legacy-firmware/blob/db9a07c/FLASHING-PROCEDURE.md#module-firmware-update-captured-from-nayaflow-2026-09-23).

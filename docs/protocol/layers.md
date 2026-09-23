# Layers

This page covers the layer list, the small table (`30/1001` to read, `30/1002` to write) that
tells the keyboard which layers exist, and what happens to a layer across its life: creation,
replacement, deletion, stacking and restore. Each list entry carries an index, an id, the layer's
stored LED animation and NayaFlow's 16-byte layer id; there are no layer names on the wire. The one
thing to know first: deleting a layer from the list does not erase its data, and rewriting the list
byte for byte is the cheapest way to bring the lighting of both halves back.

!!! note "At a glance"
    - `30/1001` reply: status `00`, index echo `00`, then one 20-byte entry per layer
      `[idx][id][animation][10][uuid16]`.
    - The animation byte uses ZMK's underglow order (2 spectrum, 3 swirl), not the effect
      command's order (2 swirl, 3 spectrum).
    - List writes are incremental; a delete is `[idx] 00 00 00`, and the layer's data stays behind.
    - Rewriting the full list to the left half restores both halves' stored lighting in one frame.
    - A factory format (`30/10ca`) reportedly wipes the list too; keep it in every backup.

Byte strings follow the site's [byte convention](transport.md#byte-convention): params and replies
start with the flag or status byte. Layer ids are shown as `<uuid16>`; no real id is reproduced.

## What the layer list is

<!--LY-04-->The list is the keyboard's identity table for layers. The 16 bytes of an entry are
NayaFlow's random layer id (a UUID, written as the plain hex of its dashed form), not a content
hash: they change only when a layer is created or deleted. There is no layer name anywhere in the
protocol; names live in the host app. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01.
naya-create-kb calls the entries UUIDs[^kb-transport].

<!--LY-19-->NayaFlow's template layer names ("Typing", "Keypad + Arrow Keys", "System") exist only
in its host database. <span class="tag static">STATIC</span>[^nf]

<!--LY-21-->NayaFlow names layer actions by the target layer's id (for example `MO_LAYER_<uuid>`)
and resolves the index at flash time; NayaCore flashes only the profile marked ON_BOARD; a layer's
`animation_id` defaults to solid. <span class="tag static">STATIC</span>[^nc] See
[NayaFlow and NayaCore](../software/nayaflow.md).

## Reading the list

!!! note "Read-only"
    `30/1001` with params `00 00` changes nothing:
    `aa 00 50 00 30 04 10 01 00 00 11 04`, sent to the left half.

<!--LY-01-->`30/1001` READ LAYER LIST takes params `00 00` (NayaCore; OpenFlow sends `00` and gets
the same list). The reply is status `00`, the index echo (`00`), then one 20-byte entry per layer:
`[idx][id][animation][10][uuid16]`. For three layers that is 62 reply bytes and a 72-byte frame.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01; the naya-create-kb maintainer's
captures show the same 72-byte frames (raw data checked[^kb-raw]). naya-create-kb describes this read
as a handshake returning "`00 00 00 10` plus three UUIDs"[^kb-transport][^kb-commands].

A three-layer reply, as params:

```text
00 00
00 00 00 10 <uuid16>
01 01 00 10 <uuid16>
02 02 00 10 <uuid16>
```

| Entry byte | Name | Meaning |
|---|---|---|
| 0 | `idx` | layer index |
| 1 | `id` | equals `idx` in every capture |
| 2 | animation | stored LED animation (ZMK underglow order) |
| 3 | `10` | length of the id that follows |
| 4-19 | `uuid16` | NayaFlow's layer id |

<!--LY-02-->The byte after the status is the index echo that every REMAP read reply carries (`00`
for the list, because NayaCore sends params `00 00`). It read `00` in every NayaFlow read on the
owner's board and in the third-party captures. The `81` and `02` once seen on the owner's board came
from reads sent with the flag byte only, right after reads of index `81` and `02`, so the device
echoed a stale index. It is not a layer count. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01 to 2026-09-17

<!--LY-03-->Byte 1 (`id`) equals byte 0 (`idx`) in every capture.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09

## The animation byte

<!--LY-05-->Byte 2 of an entry is the layer's stored LED animation, in ZMK underglow order: 0 solid,
1 breathe, 2 spectrum, 3 swirl. Two NayaFlow flashes settled it: layers set to breathe, swirl and
spectrum read back 1, 3 and 2. It read 0 on early boards because every layer was solid. The
animation also plays on the module bay LEDs. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-08/09. naya-create-kb reports a per-layer animation registry with no sender[^kb-index];
NayaFlow does send it, in this byte.

<!--LY-06-->The animation byte uses a different order from the effect command `ed/1011` and the LED
effect keys (0 solid, 1 breathe, 2 swirl, 3 spectrum). A writer that uses one table for both swaps
swirl and spectrum; a writer that writes byte 2 as 0 resets every layer to solid.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09

| Value | Layer-list byte 2 (stored animation) | `ed/1011` and LED effect keys |
|---|---|---|
| 0 | solid | solid |
| 1 | breathe | breathe |
| 2 | spectrum | swirl |
| 3 | swirl | spectrum |

See [LEDs](led.md) for the effect command and the LED keys.

## Writing the list

!!! warning "List writes are live"
    `30/1002` changes the keyboard's layer table at once. Deleting an entry does not erase the
    layer's data, and a reused index inherits it unless it is blanked. Save the list before editing.

<!--LY-07-->`30/1002` WRITE LAYER LIST takes params `00 00` followed by only the entries being
changed, in read format. Two new layers: `00 00 03 03 00 10 <uuid16> 04 04 00 10 <uuid16>` (42
params bytes). The ack is `00 00`. The write is incremental: entries not sent are untouched, and
writing an index that already holds a different id replaces it.
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0, 2026-09-01, 2026-09-03,
2026-09-08. naya-create-kb lists this command as never observed on the wire[^kb-commands]; it was
captured from NayaFlow in two flashes.

<!--LY-08-->A delete is an entry with an empty id, `[idx] 00 00 00`. NayaCore sent the pair twice in
one frame (params `00 00 03 00 00 00 04 00 00 00 03 00 00 00 04 00 00 00`); a single entry
(`00 00 03 00 00 00`) also deleted layer 3. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01, 2026-09-03

## A layer's life cycle

<!--LY-11-->**Create.** Once a new layer's list entry is written, the firmware initializes 156
records (148 unbound), its own 136-entry LED map, and all eight bays at `00`. NayaCore then writes
the layer in full (82 records, unassigned keys `0e 00`, bays `78 00`) and its LED map.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01, 2026-09-03

<!--LY-09-->**Delete.** The firmware does NOT clear a deleted layer's data or LED map. NayaCore
follows the list delete with a full blank: 82 records (`07 00` at key positions `00`-`49`, `00 00`
at the bays, in two frames) and an all-zero LED map. After that delete NayaCore still read layers
0-4 and LED maps 0-4. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01

<!--LY-10-->A zeroed LED entry `00 00 00` is hue 0, saturation 0, which the saturation model reads
as WHITE, not "off"; OpenFlow blanks with saturation 150 (NayaFlow's "no color" sentinel) instead.
What the board shows for 150 is not recorded. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09 + <span class="tag inferred">INFERRED</span>

| Step | Create | Delete |
|---|---|---|
| 1 | list add (`30/1002`) | list delete (`[idx] 00 00 00`) |
| 2 | firmware initializes 156 records, an LED map, bays `00` | nothing; the data stays |
| 3 | NayaCore writes 82 records (`0e 00`, bays `78 00`) | NayaCore writes 82 blank records |
| 4 | NayaCore writes the LED map | NayaCore writes an all-zero LED map |

If the blank in the delete column is skipped, the old keys and colors are still stored under that
index and come back when the index is reused.

<!--LY-12-->NayaFlow writes the layer list only when layers are added or removed. Its flash order is
the list, then layer data per changed layer, then module configs, then LED maps, then verification
reads and the activity timeouts. <span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0,
2026-09-01, 2026-09-17

<!--LY-18-->NayaCore names a `MAX_LAYERS` constant whose value we have not recovered. Boards have
carried five layers (0-4) through NayaFlow. <span class="tag static">STATIC</span>[^nc] +
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. naya-create-kb assumes three
layers[^kb-keymap].

<!--LY-20-->Layer ids stayed unchanged across two keyboard firmware flashes (3.35.4 to 3.41.0 and
back): the list lives in the data partition, not in the firmware image.
<span class="tag measured">MEASURED</span> 3.35.4 and 3.41.0, 2026-09-20. See
[Flash layout](../storage/flash-layout.md).

## How layers stack

<!--LY-14-->The vendor manual describes the stacking: an active higher layer overrides lower ones, a
transparent key falls through to the layer below, and priority follows the layer number, not the
order of activation[^man-c]. <span class="tag doc">DOC</span> Module bays behave differently: a bay
set to `78` inherits from the BASE layer (layer 0), not from the next lower layer.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03. See [Modules](modules.md).

<!--LY-22-->The manual also says a layer can be activated while held (momentary), absolutely (to) or
as a toggle, and that a power cycle resets the active layers to the base[^man-c].
<span class="tag doc">DOC</span>

<!--LY-15-->The layer-switch records live in the layer data: `05` momentary (hold), `0b` sticky,
`0c` TO, `0d` toggle, and the hold half of a `03` layer-tap (kind `05`). A toggle to layer 0 strands
the keyboard until a power cycle. See [Keymap records](keymap.md).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09

## Restoring the lighting by rewriting the list

<!--LY-13-->Rewriting the FULL layer list to the left half, byte for byte what it holds, drops BOTH
halves back to their stored animations and colors in one frame and changes nothing stored. It
clears a runtime effect (from an LED key or `ed/1011`), which survives layer-data, LED-map and module
writes, and it clears the lighting state a half comes back with after passing through the bootloader
(a darker amber once, plain white once, maps unchanged). Otherwise only a power cycle clears a
runtime effect. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10; 2026-09-20/22

!!! warning "Lighting restore (tested)"
    This is still a write, so send exactly the bytes you just read, to the left half only.
    Measured on 3.41.0 on 2026-09-10 and 2026-09-20/22.

    1. Read the list: `aa 00 50 00 30 04 10 01 00 00 11 04`.
    2. Take the reply's entries (everything after the status byte and the index echo).
    3. Write them back unchanged with `30/1002`, params `00 00` + all the entries.
    4. Expect the ack `00 00`; both halves return to their stored animations and colors.

## The layer list and a factory format

!!! danger "`30/10ca` wipes the board"
    `30/10ca` formats the keyboard's data partition. None of the restore steps below has been run
    on a board we measure; first attempts belong on a donor board. See
    [Factory reset](../storage/factory-reset.md).

<!--LY-16-->naya-create-kb reports that `30/10ca` also wipes the layer list: after a format,
`30/1001` and `30/1003` answer status `16` (nothing stored), and a keymap and LED restore alone
leaves hold-to-layer keys broken until a stock NayaFlow flash re-adds the list, whose "Failed to
verify written data" message is then reproducible and harmless (3.41.0, 2026-09-19 and
2026-09-22)[^kb-fr]. <span class="tag reported">REPORTED</span> (We found no step named
`ADD_DEFAULT_DATA`, the name the report gives, in NayaCore 6.11.0's or NayaFlow 1.25.1's strings.)

<!--LY-17-->A candidate that avoids the stock flash: read and save `30/1001` before `30/10ca`, then
write the saved entries back first with `30/1002`, before the layers and LED maps. The write form is
measured; the procedure is untested after a format. <span class="tag measured">MEASURED</span>
(form, 3.41.0, 2026-09-01) + <span class="tag inferred">INFERRED</span> (procedure)

## Open questions

- <span class="tag open">OPEN</span> Whether a single-entry delete is fully equivalent to
  NayaCore's doubled form ([details](../open-questions.md#oq-p16)).
- <span class="tag open">OPEN</span> Whether a layer-list write disturbs a toggled-on layer, and
  whether it clears an `ed/1050` override ([details](../open-questions.md#oq-p17)).
- <span class="tag open">OPEN</span> The value of `MAX_LAYERS` ([details](../open-questions.md#oq-p15)).
- <span class="tag open">OPEN</span> Restoring after `30/10ca` by writing the saved list back
  first: untested ([details](../open-questions.md#oq-p18)).

## Sources

[^kb-transport]: naya-create-kb, [protocol/transport](https://nemezzizz.github.io/naya-create-kb/protocol/transport/) (commit 7668067).
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-keymap]: naya-create-kb, [protocol/keymap](https://nemezzizz.github.io/naya-create-kb/protocol/keymap/) (commit 7668067).
[^kb-index]: naya-create-kb, [index](https://nemezzizz.github.io/naya-create-kb/) (commit 7668067).
[^kb-fr]: naya-create-kb, [storage/factory-reset](https://nemezzizz.github.io/naya-create-kb/storage/factory-reset/) (commit 7668067).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs); raw data decoded by us, never copied.
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading).
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings, and its default templates (static reading).
[^man-c]: Naya Create User Manual v1.1.x, pp. 16-17 (layers) and p. 25 (troubleshooting), see [Manuals](../product/manuals.md).

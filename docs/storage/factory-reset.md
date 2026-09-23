# Factory reset

This page covers the keyboard's "clear all data" command, `30/10ca`: what it is, how the vendor
software sends it, what it wipes according to the one third party who has fired it, what it may
spare, what to save first, and how to restore afterwards, including the layer list that a keymap and
LED restore alone misses. The thing to know first: NayaFlow's own "Clear all keymap data" button
sends this command, with no confirmation dialog, and none of the restore steps on this page has been
run on the boards we measure.

!!! danger "Data-destroying command. Untested by us."
    `30/10ca` wipes the keymap, the LED maps, the settings and the layer list. It has been fired by a
    third party on 3.41.0 (macOS), never on the owner's boards. Take and verify a complete snapshot
    first, send it to the left half only, and make first attempts on a donor board. Safety level HIGH.

!!! note "At a glance"
    - `30/10ca` is CLEAR_ALL_DATA; NayaCore sends it to the left half with params `00 00`, then resets the board.
    - NayaFlow's Danger Zone "Clear all keymap data" (`clear_data`) runs it.
    - naya-create-kb fired it with params `01`; whether both forms act the same is open.
    - A restore must include the **layer list**, or hold-to-layer keys type their base letter.
    - What it spares (split-link pairing, bonds, timeouts, the module bundle) is open.

## What `30/10ca` is

REMAP `30/10ca` is CLEAR_ALL_DATA: nayactl names it, and NayaCore has a matching
ClearAllData operation. It is destructive, and nayactl does not gate it: it goes out through `raw`
without `--force` <span class="tag static">STATIC</span>[^nx][^nc]. naya-create-kb describes it as a hidden device-side format of the
LittleFS data partition <span class="tag reported">REPORTED</span>[^kb-fr]; the device side is encrypted firmware, so how it clears the data
is unknown.

The vendor's help center had a "Clearing Keymap Data" troubleshooting page; its body is
lost, and only its first line ("Symptoms") is archived <span class="tag doc">DOC</span>[^wb-help].

## How the vendor software reaches it

NayaFlow's Danger Zone button "Clear all keymap data" sends the ZMQ event `clear_data`. The
vendor's text says the board "will perform a clear operation, then restart", and that the only known
cause of a failing FLASH CREATE is a corrupted keymap, fixed by clearing and reflashing <span class="tag static">STATIC</span>[^nc-flow].
In NayaCore, `clear_data` is event 5 of its command table; it leads through `si_clearAllData_req_source`
and the ClearAllData operation (`doClearAllDataOperations`) to `_remapClearFlash`, which queues
`30/10ca` <span class="tag static">STATIC</span>[^nc-disasm]. So the stock interface does send `30/10ca`, and it does so without a
confirmation dialog. naya-create-kb says direct wire access is the only path; the static route above
shows otherwise.

NayaCore's ClearAllData steps are Clearing, ReadData and VerifyDataCleared, with the log
lines "Reconnected to device %1 after clear all data" and "Data is cleared for device %1". After the
command it requests a reset of the board and rechecks the Bluetooth status of the linked halves.
Its "Data is cleared" check compares what it reads back with an **empty** profile: the profile it
builds for that comparison (`Profile(ADD_DEFAULT_DATA)`) is constructed with its default-data flag
off, so nothing default is written to the board <span class="tag static">STATIC</span>[^nc][^nc-disasm]. naya-create-kb gives the same
function chain from `si_clearAllData_req_source` to `_remapClearFlash` and
`_handleRemapClearAllDataResponse` <span class="tag reported">REPORTED</span>; two of its details do not hold: `_handleSpiflashFormatPartition`
is not part of this chain (it handles `fa` replies), and no default profile is queued
([corrections](#where-this-differs-from-naya-create-kb)).

NayaCore's ZMQ dispatcher knows 15 command events plus `quit`: `flash_keymap`,
`update_keymap`, `start_device_manager`, `close_device_manager`, `force_touch_start`,
`force_tune_start`, `force_track_start`, `create_pairing_start`, `update_module_fw`,
`update_create_fw`, `update_fw_files`, `repair_flash`, `clear_data`, `clear_ble_devices` and
`set_handshake_frequency`. A `clear_all_data` event is not among them, and NayaCore answers an unknown
event with "Unknown command event:" and an invalid-event code (its two reply sites use error codes 4
and 5) <span class="tag static">STATIC</span>[^nc][^nc-disasm]. Also reported by naya-create-kb, which saw the reply
"invalid_command_event" with error 4. More: [NayaFlow and NayaCore](../software/nayaflow.md).

NayaCore gates the ClearAllData operation, and `30/10ca` itself, at keyboard firmware 3.30.0, left
half only: `naya_fw::create::ClearAllData_MinVersion` is a copy of the ProtocolCDC minimum, set at
start-up from the literal `0.3.30.0` <span class="tag static">STATIC</span>[^nc-gates]. naya-create-kb
names the symbol but calls its value unrecoverable[^kb-functions]. Every gate is listed on
[Differences by firmware](../protocol/firmware-differences.md#minimum-firmware-per-command).

## The command and its parameters

**What NayaCore sends.** NayaCore sends `30/10ca` with params `00 00` (frame
`aa 00 50 00 30 04 10 ca 00 00 da 04`): in our disassembly of NayaCore 6.11.0 (macOS and Windows
builds), `_remapClearFlash` passes one byte `00` <span class="tag static">STATIC</span>[^nc-disasm].
In detail: it builds a `QByteArray` of size 1 with fill value 0 (macOS x86_64 NayaCore, `0x1004a29c0`)
and passes it to `_constructRemapMessages` with `0x10ca`; that function queues remap commands for
`dst 0x50`, and the frame builder puts the flag byte `00` before the data, exactly as for the
`30/1001` read. The only other callers of `_constructRemapMessages` are `1001` to `1004`, `1009` and
`100a` to `100e` <span class="tag static">STATIC</span>.

**What naya-create-kb sent.** naya-create-kb's `01` read the byte array's size argument as its
value; its own tool sends `01` (`aa 00 50 00 30 03 10 ca 01 db 04`: in this site's convention a flag
byte `01` and no data) <span class="tag reported">REPORTED</span>[^kb-fr]. Whether `00 00` and `01`
behave the same stays a donor-board test <span class="tag open">OPEN</span>
([open question](../open-questions.md#oq-f16)). (An earlier inference of ours, `00 01`, was wrong
too.)

**Firing it, as the third party did** (2026-09-18, 3.41.0, macOS): the left port,
`dst 0x50`, params `01`; the reply had status `00` (observed bytes `aa 50 00 00 30 04 10 ca 00 80 ...`);
no reboot was needed to keep talking over CDC <span class="tag reported">REPORTED</span>[^kb-fr]. The left half holds every store
([Flash layout](flash-layout.md#what-each-half-stores)), and NayaCore also sends every remap command
to `0x50` <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>. Safety HIGH (data loss). TESTED (third party, 3.41.0, macOS); UNTESTED by us. When
NayaFlow sends it, NayaCore resets the board afterwards.

A `30/10ca` sent to the right half (`dst 0x51`) cannot restore anything: the right half holds
no configuration store, and what it would clear there (three partitions, one reported Not Detected) is
unknown <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>.

## What it wipes and what it may spare

What the third party observed afterwards: `30/1001` and `30/1003` answer `16 00`; ED
commands still acknowledge; `fe/1002` still answers and the firmware is unchanged; the keymap, LED maps
and settings are default or empty; and the layer list is wiped as well (seen twice, 2026-09-19 and
2026-09-22), so a keymap and LED restore alone leaves hold-to-layer broken (a held momentary-layer key
types its base letter) and layer toggles misbehave <span class="tag reported">REPORTED</span>[^kb-fr]. NayaCore's own check expects exactly
that: after its clear it compares the board with an empty profile <span class="tag static">STATIC</span>.

The first reply byte is a status: `0x16` means nothing is stored for that read (a
header-only reply), and `0x18` the same on a continuation. Measured on 3.28.7 for LED-map reads of
layers that never had a map (writing a map made them read `01` and then `00`) <span class="tag measured">MEASURED</span> (owner's board,
2026-09-19); a third party's stock NayaFlow session on 3.41.0 shows `30/100d` answering `16 00`,
`16 01` and `16 02` for layers 0 to 2 <span class="tag reported">REPORTED</span> (raw data checked). The vendor's name for `0x16` is **open**
(NayaCore's status names include "No Data") ([Transport](../protocol/transport.md);
[open question](../open-questions.md#oq-f17)). naya-create-kb calls it an empty-store error.

What `30/10ca` spares is **open**. naya-create-kb says the split-link pairing most likely
survives (clearing split links is a separate operation), and its post-format sessions show the halves
still linked <span class="tag reported">REPORTED</span>. NayaCore's rechecking of the linked halves after the clear presumes the same <span class="tag inferred">INFERRED</span>.
Whether timeouts, bonds and the module bundle survive is also open ([open question](../open-questions.md#oq-f16)).

## Before you send it: a complete snapshot

Save <span class="tag inferred">INFERRED</span> (a checklist built from the measured stores):

- every layer's 156 positions (both banks) and its 136-entry LED map;
- the **raw layer list** (`30/1001`);
- the module configuration list and every slot (0 to 7);
- the activity timeouts (`fe/100b`);
- the LED settings you use (`ed/1012` to `1014` cannot be read back, so note what you set);
- both halves' own and pair addresses and bond tables (do not publish them);
- the `fa/1001` self-test reply.

Boards can have more than three layers: NayaFlow added layers 3 and 4 in a captured flash,
and a new layer is 156 records, a 136-entry LED map and all eight bays pointing at slot 0. A
three-layer snapshot is not always complete <span class="tag measured">MEASURED</span> (2026-09-01 and 2026-09-03).

naya-create-kb's snapshot holds three layers of keymap, three LED maps and an information block
(firmware, Bluetooth, timeouts, battery, modules) but no layer list <span class="tag reported">REPORTED</span> (raw data checked), which is
why its restore missed the layer list.

## Restoring afterwards

**The third party's restore**: per-record `30/1004` writes (`00 <layer>` plus the record)
and per-entry `30/100e` writes, each section read back and compared ("IDENTICAL"); 468 key records and
408 LED entries restored cleanly. Those counts are 3 layers times 156 positions and 3 times 136 LED
entries: the full two-bank layers and the full LED maps <span class="tag reported">REPORTED</span> <span class="tag inferred">INFERRED</span> (raw data checked: its snapshots hold
exactly those counts). Safety MEDIUM. TESTED (third party); UNTESTED by us.

**The third party's cure for the missing layer list** is a stock NayaFlow flash, which
writes it again. That flash's "Failed verify written data" error is reproducible after `30/10ca`
(2 of 2) and harmless (check by switching layers, not by the dialog), and it reverts four layer-0
records to NayaFlow's stale profile, which it then rewrites with single-record `30/1004` writes
<span class="tag reported">REPORTED</span>[^kb-fr]. Raw data checked: comparing its pre-wipe snapshot with NayaFlow's factory profile gives
seven layer-0 differences, the four it names plus a key set through NayaFlow itself, a module bay
record, and a second-bank record that NayaFlow never clears (see below). Safety MEDIUM. TESTED (third
party, twice); UNTESTED by us.

Why the stock flash behaves that way: NayaFlow does not import the device's keymap (it shows
its own profile), and it writes the layer list only when layers are added or removed; after a wipe the
list is missing, so it is added, and NayaFlow's own profile is pushed with it <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (our captures of
three NayaFlow flashes, 2026-09-01).

**The layer list can be saved and written back directly.** `30/1001` returns the status, one
header byte and a 20-byte entry per layer, `[idx][id][animation][10][uuid16]`. `30/1002` takes wire
params `00 00` followed by entries in the same form, is incremental, and acknowledges `00 00`;
creating `00 00 03 03 00 10 <uuid16>` added layer 3 <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-03 and
2026-09-10). Third-party captures show the same read shape. See [Layers](../protocol/layers.md).

**A proposed restore order** (UNTESTED after a format; the owner has not done it) <span class="tag inferred">INFERRED</span>:

!!! warning "Proposed, untested: Safety MEDIUM (after the HIGH format step)"

1. Before firing, save the raw layer list with the rest of the snapshot.
2. Afterwards, write the layer list first (`30/1002`).
3. Then the layer records (`30/1004`, both banks).
4. Then the LED maps (`30/100e`).
5. Then the module configuration list and slots.
6. Then the timeouts and the LED settings.
7. Check by holding a layer key.

It would replace the stock-flash step and avoid its reverted records and verify error.

After a format, set the LED settings again. The ceiling (`ed/1013`) has no read command, so
re-send the value you want (100) <span class="tag reported">REPORTED</span>[^kb-fr]. Never "probe" an ED setting with an empty payload: it is
zero-filled, so it writes 0 <span class="tag measured">MEASURED</span> ([Flash layout](flash-layout.md#persistent-settings)).

The third party's closing steps after a successful format: re-read the device, restore the
profile, check that the LEDs come back, and re-apply its LED recovery ladder <span class="tag reported">REPORTED</span>[^kb-fr].

## "Failed to verify written data"

NayaFlow's verify error has other causes too <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span>:

| Cause | Effect on typing | Fix | Tested |
|---|---|---|---|
| Second-bank records (double tap, tap plus hold at `KK+0x52`) that NayaFlow's profile does not describe; its sparse flash never clears them | none | write `[KK+0x52] 07 00` at the stale positions, or flash once with a tool that writes an empty second bank for every key it sets | TESTED (us), 3.41.0, 2026-09-09 and 2026-09-17 |
| Its verify renders every record at term 200 and flavor 1, so any hold-tap key mismatches once the term is not 200 | none | ignore the dialog, or keep the term at 200 | TESTED (us), 3.41.0, 2026-09-17 |
| A NayaFlow flash right after `30/10ca` | none | check by switching layers | TESTED (third party) |

Safety LOW to MEDIUM. NayaCore 6.10.2 added handling for a hold-tap action and flavor mismatch on
write[^beta].

## Tested and untested

On the owner's hardware (status 2026-09-23), `30/10ca` has never been sent, and restoring
layers after a wipe has not been done. Every step on this page is either third-party measured or
untested <span class="tag measured">MEASURED</span>.

## Where this differs from naya-create-kb

| naya-create-kb says (factory-reset page) | What the evidence shows |
|---|---|
| `_remapClearFlash` builds the byte `01`, so the frame's payload is `[01]` | It builds one byte `00`; NayaCore sends params `00 00`. The third party's tools sent params `01` |
| Direct wire access is the only path in this build | NayaFlow's "Clear all keymap data" sends `30/10ca` through ClearAllData |
| The ClearAllData chain includes `_handleSpiflashFormatPartition` | That handler serves `fa` replies; it is not part of the clear |
| `doClearAllDataOperations` queues a default profile (`ADD_DEFAULT_DATA`) that a stock flash then writes | The default-data flag is off: the profile is an empty baseline for the "Data is cleared" check; the layer list comes back through NayaFlow's own flash path |

## Open questions

- <span class="tag open">OPEN</span> Whether `00 00` (NayaCore's params) and `01` (naya-create-kb's tool) behave the same: a donor-board test ([details](../open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> Which stores `30/10ca` spares: split-link pairing, bonds, timeouts, the module bundle ([details](../open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> Whether writing the saved layer list back restores hold-to-layer after a format ([details](../open-questions.md#oq-p18)).
- <span class="tag open">OPEN</span> The vendor's name for status `0x16` ([details](../open-questions.md#oq-f17)).

## Sources

[^kb-fr]: naya-create-kb, [storage/factory-reset](https://nemezzizz.github.io/naya-create-kb/storage/factory-reset/).
[^kb-functions]: naya-create-kb, [disassembly/functions](https://nemezzizz.github.io/naya-create-kb/disassembly/functions/).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py`: CLEAR_ALL_DATA and the `--force` list).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings and macOS symbols (ClearAllData steps and messages, ZMQ events, status names, `ClearAllData_MinVersion`).
[^nc-flow]: NayaFlow 1.25.1, renderer strings (Danger Zone texts).
[^nc-disasm]: NayaFlow 1.25.1, macOS x86_64 NayaCore, our disassembly (2026-09-23): the ZMQ name table and `_handleCommandMessage` case 5; `Naya_DeviceManager::doClearAllDataOperations`; `ProtocolCDCProcessWorker::_remapClearFlash` (`0x1004a29c0`: `mov esi, 1; xor edx, edx; call QByteArray(long long, char)`), `_constructRemapMessages` (`0x1004a2bf0`) and the frame builder; the `Profile` constructor. The Windows x64 build's `_remapStartStep` builds the same one-byte `00` array for `0x10ca`. Names and addresses only; see [Disassembly](../software/disassembly.md).
[^nc-gates]: NayaFlow 1.25.1, NayaCore 6.11.0 (macOS arm64, cross-checked on x86_64), our disassembly (2026-09-23): the guarded initializers of the `naya_fw::*_MinVersion` values, `operationMinFWVersion` and `commandMinFWVersion`; see [Disassembly](../software/disassembly.md#version-gates).
[^wb-help]: Wayback Machine index of the vendor's help center, [help.naya.tech captures](https://web.archive.org/web/2026*/help.naya.tech/*).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases), v1.23.1.

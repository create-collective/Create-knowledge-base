# Disassembly

The static-analysis record of NayaFlow's device service NayaCore and its background server: which
builds were read and how anyone can re-derive the findings, what static reading can and cannot
settle, the functions and state machines that matter, the version gates, and the data tables that
turn action names into wire values. The one thing to know: the macOS builds keep their C++ symbols,
so the "arm64-only" readings are checkable by anyone with the public installer; this page gives
names, offsets and behavior only, never decompiled code.

!!! note "At a glance"
    - Builds read: NayaCore 6.11.0 from NayaFlow 1.25.1 for Windows (strings, data tables) and macOS
      (arm64 and x86_64: symbols and code), plus 1.17.3 for comparison.
    - The name maps are nine `naya_zmk::*` QMaps; the key map is filled by 282 inserts (281 names).
    - `clear_data` reaches the ClearAllData operation, which sends `30/10ca`.
    - Every `*_MinVersion` gate is recoverable: REMAP commands need 3.30.0, `be/100c`-`100f` 3.32.0,
      `be/1010` 3.34.0, the activity timeouts 3.36.0.
    - No decompiled function bodies, instruction listings or key-extraction methods are published here.

## Provenance: which builds, and how to re-derive

| Build | Platform | How read | By |
|---|---|---|---|
| NayaCore 6.11.0 (NayaFlow 1.25.1) | Windows x64, `core/NayaCore/NayaCore.exe` | strings with a 2-character minimum, data tables with file offsets, the 60 source paths | us |
| NayaCore 6.11.0 (NayaFlow 1.25.1) | macOS arm64, `NayaCore.app/Contents/MacOS/NayaCore`, 11 883 840 bytes, MD5 `84ded78022b6d312483aae0192584168` | symbols (about 1 800), code, guarded initializers, jump tables | us (2026-09-23); naya-create-kb (`otool -tV`) |
| NayaCore 6.11.0 (NayaFlow 1.25.1) | macOS x86_64, 12 649 584 bytes | symbols and code (cross-check) | us |
| NayaCore of NayaFlow 1.17.3 | Windows | strings | us |

<span class="tag static">STATIC</span>[^nc-mac][^nc]. Our static work is on the Windows build, with a
few functions read in both macOS builds (recorded in create-legacy-firmware[^nh-fp]) and, in 2026-09, the whole
arm64 map and gate machinery. The community KB disassembled the macOS arm64 build: its "installed copy"
has the MD5 of the public 1.25.1 arm64 asset, and it worked from a re-signed copy (MD5
`b3dd3e14c255886d05b4a2728f61ffaa`) whose `otool -tV` dump of `(__TEXT,__text)` has 1 736 507 lines,
1 735 023 of them instructions: the same count as our `__text` section (6 940 092 bytes / 4), and 3 000
random addresses disassemble identically in our copy of the public asset, so the two copies differ
only in the signature <span class="tag static">STATIC</span>; also reported by naya-create-kb[^kb-dis]
(its dump: raw data checked).

- **Re-derive it yourself.** Every stable installer is still public in `NayaTech/NayaFlow-releases`
  (25 releases, GitHub sha256 digests in the release metadata), and create-legacy-firmware mirrors them with a
  manifest. Match a binary by digest before comparing offsets <span class="tag doc">DOC</span>[^rel][^nh-manifest].
- **Use a 2-character minimum** (and a UTF-16 pass) with `strings` before calling a name absent: the
  default 4-6 character minimum hides short literals that matter (`A`-`Z`, `F1`-`F24`, `mo`, `tap`,
  `none`, `trans`, `" + "`, `" - "`). Some names are not strings at all: the ZMQ event `quit` is built
  from an immediate and appears in no `strings` output <span class="tag static">STATIC</span>.
- **Scanning all 25 releases**: read the asar header, find MCUboot images by magic `0x96f3b83d` and walk
  their TLVs, and carve Qt resources (name entry `[u16 len][u32 hash][utf-16be name]`, file node
  `nameOffset = BE32(node+0)`, `dataOffset = BE32(node+10)`, data preceded by a big-endian u32 length).
  Public scripts: create-legacy-firmware `tools/carve_fw.py`, `tools/extract_history.py`, `tools/flash_map.py`
  <span class="tag static">STATIC</span>[^nh].

## Method and what static reading cannot settle

- naya-create-kb's method <span class="tag reported">REPORTED</span>[^kb-dis]: `otool -tV` and
  `strings`; every `construct*Commands` table cross-checked against at least one live frame (20 or
  more); handler maps resolved from jump tables and `ldrsb`/`adrp`/literal-pool reads; extractor
  scripts over the disassembly text (key batches v1-v4, 282 of 282 pairs); reader hunts by `adrp` page
  census. Its jump-table readings hold: the LED builder switches on `w22 - 0x1003` compared with
  `0x4d` (so `0x1003`-`0x1050`), and `operationMinFWVersion` is a switch on the operation
  <span class="tag static">STATIC</span>. The ZMQ dispatch is a name-to-enum table followed by a
  16-way jump table (below), not a compare chain.
- Our method in 2026-09: the arm64 symbol table and function starts, a reference index over the whole
  text section, a small register and stack tracker over the static initializers (it recovers every
  `(name, value)` pair of the maps), guarded-initializer and dyld-bind resolution for the
  `*_MinVersion` values, and jump-table decoding. The x86_64 build stores most map values as
  immediates, which makes it a convenient cross-check <span class="tag static">STATIC</span>.
- **What static reading cannot settle**: values reached only through a run-time object (a base plus an
  offset). The `naya_fw::*_MinVersion` values are zero in the file's data section and have guard
  variables, but they are **not** beyond static reading: each is an inline QString set at start-up by
  a guarded initializer from a UTF-16 literal, or copied from another such variable
  <span class="tag static">STATIC</span>. naya-create-kb calls them unrecoverable[^kb-dis].

## Key functions

Addresses are virtual addresses in the two macOS builds of NayaCore 6.11.0
<span class="tag static">STATIC</span>[^nc-mac]:

| Function | arm64 | x86_64 | What it does |
|---|---|---|---|
| `Binding::param1()` | `0x100589610` | `0x100640e30` | resolves an action name to its first parameter through the `naya_zmk` maps; switches on the action type (0-0x15) |
| `Binding::param2()` | `0x100589bc0` | `0x1006414e0` | the second parameter (Bluetooth, LED and mouse maps only) |
| `Binding::serializeBindingData()` | `0x10058864c` | `0x10063fdd0` | the shared record emitter for keys and module slots |
| `Key::serializeBindingData(int)` | `0x100599bcc` | `0x1006537c0` | offset 0 = the record at `KK`, offset 1 = the second bank at `KK+0x52` |
| `Key::wrapDblTapRecord(h1, h2, inner)` | `0x1005999f8` | `0x100653620` | builds the type-`10` record |
| `Key::hasDoubleTapBindings()` | `0x100599b30` | `0x100653740` | true when slot 2 or 3 is bound |
| `Key::operator==` | `0x10059af58` | `0x100654ab0` | compares offsets 0 and 1 of both keys |
| `ModuleConfig::toByteArray(QList<int>)` | `0x1005cccf8` | `0x10068bdd0` | module-config data for `_remapWriteModuleData`; calls `behaviourSlotStart()` (`0x1005c9e98`) |
| `Slot::serializeSlot()` | `0x100602650` | `0x1006c73d0` | one module slot, through `Binding::serializeBindingData` |
| `_constructLEDMessages` | `0x100320060` | `0x100385340` | LED command construction |
| `_constructRemapMessages` | `0x10041fde0` | `0x1004a2bf0` | REMAP command construction from (static, dynamic) parameter pairs |
| `_remapClearFlash` | `0x10041fb90` | `0x1004a29c0` | builds the `30/10ca` parameters; called from `_remapStartStep` (`0x1004029a8`) |
| `_handleRemapClearAllDataResponse` | `0x10043ba10` | `0x1004c2090` | handles the `30/10ca` reply |
| `Naya_DeviceManager::doClearAllDataOperations` | `0x1001b3da0` | `0x1001edb20` | the ClearAllData operation |
| `ZMQHandler::_handleCommandMessage` | `0x100651a78` | `0x10071f140` | the ZMQ event dispatcher |
| `naya_command_support::operationMinFWVersion` | `0x100145798` | `0x100174fb0` | minimum firmware per operation |
| `naya_command_support::commandMinFWVersion` | `0x100145480` | `0x100174920` | minimum firmware per command |
| `MCUBootWorker::uploadImageToCreateSlot(path)` | `0x1000f3d14` | `0x100115d50` | `uploadImageToSlot(path, 2)` |
| `MCUBootWorker::uploadImageToModulesSlot(path)` | `0x1000f7938` | `0x10011a140` | `uploadImageToSlot(path, 4)` |
| `Naya_Device::setCreateFlashGenerationFromPid` | `0x10014d710` | `0x10017e600` | flash generation from the USB PID |

**Port broker** (`Naya_SerialWorkerBroker::determineDeviceType`) <span class="tag static">STATIC</span>[^nc]:
NayaCore sends `aa 00 50 00 fe 03 10 01 00 11 04` (and the `0x51` form), then the `fe/1002` probe
`aa 00 50 00 fe 03 10 02 00 12 04`; a reply `aa 50 00 00 fe 03 10 01 00 11 04` means "ProtocolCDC Left
detected" (`aa 51 ...` Right); shorter prefixes (`aa 50 00 00 fe 07`, `... fe 07 10`, `aa 50 00 00 fe`)
mean "DEFECTIVE detected". With no binary reply it sends a newline, the text `fwvchk`, then
`keyboard_mode_release_toggle` and `fwvchk` again. Port classes: SystemCDC, Outdated, Legacy,
Manufacturing SystemCDC; "Outdated ProtocolCDC detected on port %1, closing the port". A handler that
does not register within 15 s is quit. These frames settle two wire facts from the vendor's own bytes:
the checksum excludes the size byte (`10 ^ 01 ^ 00 = 11`), and a reply carries the answering half's
address in byte 1 with `00` in byte 2. The broker accepts version replies `fw_version#N.N.N.N`,
`N.N.N.N` and `NNNN.NNNN.NNNN`; with a known version NayaCore adds a port directly as ProtocolCDC.

**Frame checks and retries** <span class="tag static">STATIC</span>[^nc]: received frames are checked
in the order header, sender, destination, ID, type, length, command, status, data, checksum, EOT
("Invalid ... received. Trimming packet."); status names: Final Packet/Success, Multi Packet/Continue,
Invalid Command, Busy, Memory Full, Invalid Format, Save Failed, Load Failed, NVS, No Data, Invalid
ID; NayaCore retries on Busy within a per-command budget ("Max message retries reached").

**Validators NayaCore applies before sending** <span class="tag static">STATIC</span>[^nc]:
SET_BLE_NAME name under 256 bytes; SEL/CLEAR_BLE_PROFILE one byte under 5; SET/UNPAIR_PAIR_ADDRESS 6
bytes; GET_BLE_STATUS reply at least 239 bytes; LEDS_INC/DEC amount under 101; LED_ADJ_BRT 0-100
("Invalid brightness"); LEDS_HUE_SAT hue under 361, saturation under 101; LEDS_RGB_BRT brightness under
101; SEL_LEDS_EFF effect id below the effect count ("Empty effect_id parameter"); SET_HOST_OS one byte
below a bound (0 Windows, 1 macOS by enum order); MODULE_FWUP one byte `module_type`, invalid values
fall back to AUTO_DETECT; SET_RELEASE_MODE, TOGGLE_KEYSCAN_MODE and MODULE_BAT_RECOVERY one of two
values; WAIT is a host-side meta command clamped to a maximum. naya-create-kb lists the brightness,
hue, saturation and effect ranges[^kb-functions].

**LED command construction** (`_constructLEDMessages`): the target (`params[0][0]`) goes into a static
payload and the command data into a dynamic payload, which the message queue joins, so NayaFlow never
sends an empty ED payload; an empty target is refused host-side ("Missing or empty target parameter for
LED command"); out-of-range values are clamped to 100 with a warning. The switch covers `0x1003`-`0x1050`:
`1006`/`1007`, `1008`, `100e`, `1011` and `1050` have their own cases, the target-only commands share one,
and `1012`-`104f` share another. FORCE LEDs ON and OFF are `ed/10d1` and `ed/10d2`, outside that
range: NayaCore's LED command table lists them first and nayactl names them the same way
<span class="tag static">STATIC</span>[^nc][^nc-mac][^nx]; also reported by naya-create-kb[^kb-functions].

**The remap path** <span class="tag static">STATIC</span>[^nc]: step functions `_remapReadLayerList`,
`_remapWriteLayerList`, `_remapReadLayerData`, `_remapWriteLayerData`, `_remapReadModuleConfigList`,
`_remapWriteModuleConfigList`, `_remapReadModuleData`, `_remapWriteModuleData`, `_remapReadColorData`,
`_remapWriteColorData`; interpreters `_interpretLayerListData`, `_interpretLayerData`,
`_interpretModuleConfigListData`, `_interpretModuleConfigData`, `_interpretLedMapData`; no macro step
exists. `_constructRemapMessages` turns its parameter list into frames pair by pair (static payload,
dynamic payload) with no subcommand-specific branch: `_remapReadLayerData` passes `[layer]` + empty for
each layer, which the wire shows as params `00 <layer>` <span class="tag static">STATIC</span>[^nc-mac]
<span class="tag measured">MEASURED</span>.

**Record serializers** <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc-mac]:

- `Key::serializeBindingData(offset)` and `Binding::serializeBindingData()` exist; "Invalid offset for
  serializeBindingData: %1" shows the offset argument. Offset 0 is the primary record and offset 1
  adds `0x52` to the position (the second bank, which holds double tap and tap + hold on the wire).
- `Key::wrapDblTapRecord(h1, h2, inner)` builds `[h1][0x10][LEN][term lo][term hi][h2][inner...]` with
  LEN = inner size + 3; the term comes from the profile settings and defaults to 200 when there are
  none. `operator==` compares offset 0 and then offset 1 of both keys; `hasDoubleTapBindings()` looks in
  the binding map at `Key+0x18` for slot 2 (double tap) or slot 3 (tap + hold). On the wire every
  captured type-`10` record has h2 = `03` and inner = the 21-byte hold-tap body `[hold kind][tap
  kind][flavor][term u16 LE] hold(4) 00x4 tap(4) 00x4` (27 bytes in all: `[KK] 10 18` + 24) (owner's
  board, 3.41.0, captures 2026-09-03 and 2026-09-21/22).
- `Binding::serializeBindingData` is the shared emitter for keys and module slots: its callers are
  `Key::serializeBindingData(int)` and `Slot::serializeSlot()`; module fields accept the same record
  types as keys (owner's board, 2026-09-03).
- `ModuleConfig::toByteArray(QList<int>)` builds the module-config data `_remapWriteModuleData` sends
  (`30/100c`) and calls `behaviourSlotStart()`.
- A MOD_TAP record is "at least 21 bytes" and a pair with a missing half is rejected
  (`Key::serializeBindingPairData`); NayaCore refuses double-tap bindings on Touch and Tune
  (`Encountered unsupported double tap behaviour for Touch/Tune module type`).
- Display formats: `TO(%1)`, `TOG(%1)`, `MO(%1)`, `SL(%1)`; logs `ZMK Behaviour: (0x%1) %2`,
  `Unimplemented ZMK behaviour: %1`, `Unknown ZMK behaviour: (%1) %2` <span class="tag static">STATIC</span>[^nc].

All of these agree with naya-create-kb's function page, which first named several of them[^kb-functions].

**SPI flash flow** <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nc][^bg]:
`_handleSpiflashTestFlash` -> `_handleConfirmation` -> `_handleSpiflashFormatPartition`; the TestSPIFlash
operation's steps are VerifySPIFlashState, ReformatErrorPartitions, NormalRestart,
VerifySPIFlashStatePostReformat, and its results "No errors ... without reformatting", "after %2
reformat attempts" or "Test SPIFlash operation critically failed. Your unit's SPIFlash may potentially be
damaged." So "Test and Format SPI-Flash" formats only partitions whose self-test fails; on a healthy
board it only tests. The SPIFLASH_TEST opcode exists in NayaCore from 1.17.3; its structured reply
parser only in 1.25.1.

**The clear-all-data chain** <span class="tag static">STATIC</span>[^nc][^nc-mac]:
`ZMQHandler::si_clearAllData_req_source` -> `Naya_ThreadManager::si_clearAllData_req_router2` ->
`Naya_DeviceManager::sl_clearAllData_req_receiver` -> `_startClearAllDataOperations` ->
`doClearAllDataOperations` (`Naya_DeviceManager_ClearAllData.cpp`); completion "Reconnected to device
%1 after clear all data."; "Data is cleared / not cleared for device %1".

- `doClearAllDataOperations` reads the board's profile, builds `naya_remap::Profile(ADD_DEFAULT_DATA)`
  and compares the two (`diffLayerMap`, later `diffConfigMap`); the only process it queues is category
  `0x30` subcommand `0x10ca`, named `clear_all_data`, with an empty parameter list. naya-create-kb reads
  it as also enqueueing the default profile[^kb-functions]; we find it compared, not written.
- NayaCore sends `30/10ca` with params `00 00` (frame `aa 00 50 00 30 04 10 ca 00 00 da 04`): in our
  disassembly of NayaCore 6.11.0 (macOS and Windows builds), `_remapClearFlash` passes one byte `00`
  <span class="tag static">STATIC</span>[^nc-mac]. The remap state machine's start step calls
  `_remapClearFlash`, which builds the parameter list `[QByteArray(1, 0x00), QByteArray()]` and calls
  `_constructRemapMessages(0x10ca, ...)`, the same construction as `30/1001` (`_remapReadLayerList`),
  whose frame our captures show as params `00 00`; `_constructRemapMessages` has no
  subcommand-specific branch. naya-create-kb's `01` read the byte array's size argument as its value;
  its own tool sends `01` (`aa 00 50 00 30 03 10 ca 01 db 04`)
  <span class="tag reported">REPORTED</span>[^kb-functions]. Whether `00 00` and `01` behave the same
  stays a donor-board test <span class="tag open">OPEN</span>
  ([details](../open-questions.md#oq-f16)).
- `ZMQHandler` has 17 request signals (`si_*_req_source`), `si_clearAllData_req_source` among them.
  `clear_all_data` is not an event name; the event `clear_data` (enum 5) is dispatched to
  `si_clearAllData_req_source`. So the ClearAllData chain is reachable from NayaFlow's Danger Zone,
  not dead code as naya-create-kb calls it[^kb-rpc]; the 17-signal count is also its reading.

**The ZMQ event table** <span class="tag static">STATIC</span>[^nc-mac]: a static initializer builds the
name-to-enum table 0 `invalid_command_event`, 1 `quit`, 2 `update_keymap`, 3 `flash_keymap`,
4 `repair_flash`, 5 `clear_data`, 6 `clear_ble_devices`, 7 `start_device_manager`,
8 `close_device_manager`, 9 `force_touch_start`, 10 `force_tune_start`, 11 `force_track_start`,
12 `create_pairing_start`, 13 `update_module_fw`, 14 `update_create_fw`, 15 `update_fw_files`,
16 `set_handshake_frequency`; `_handleCommandMessage` switches on the enum (events 1-16) and emits the
matching request signal (`quit` -> `si_coreQuit_req_source`). The event list, with who sends what, is on
[NayaFlow and NayaCore](nayaflow.md).

**MCUboot worker** <span class="tag static">STATIC</span>[^nh-fp][^nc]: `MCUBootWorker` has
`openSerialDevice`, `sendFramedCommand`, `parseSMPResponse`, `uploadImageToSlot`, `uploadImageChunk`,
`enterLogPortMode`, `pollLogPort`, `onSerialReadyRead`, `keymapUpload`, `testImage`, `confirmImage`; it
runs a data-port "connection test" to tell the SMP port from the log port ("Log port detected, polling
serial for boot log until data port worker finishes"). Chunks are `min(remaining, 512)`; `doStart` calls
only the upload and `restartDevice`, never `testImage` or `confirmImage`.
`setCreateFlashGenerationFromPid` masks the PID with `0xEFFF`, accepts offsets 0, 11 and 22 from `0x64`
(left) and `0xC8` (right), and reads bit `0x1000` as flash generation B (details on
[USB](../connectivity/usb.md) and [Firmware images](../firmware/images.md)).

**nayactl's Ghidra names** for a 1.19.1-era Windows build: `FUN_1403207e0` message serializer,
`FUN_1402bd2c0` `_getDestination`, `FUN_140264070` `_handleKeyscanEvent`, `FUN_14033b170` Bluetooth
diagnostics parser <span class="tag static">STATIC</span> (third party)[^nx].

## Version gates

NayaCore 6.11.0 checks the keyboard's firmware against minimum versions ("Consolidated Firmware
Version Checking", both channels, 2026-07-17) <span class="tag doc">DOC</span>[^rel]. The values are
inline QString variables set at start-up by guarded initializers; the literals read `0.3.30.0` and so
on (the wire form of the version) <span class="tag static">STATIC</span>[^nc-mac]:

| Gate (`naya_fw::create::`) | Minimum keyboard firmware | Set from |
|---|---|---|
| `ProtocolCDC_MinVersion` | 3.30.0 | literal |
| `Keymap_`, `Pair_`, `ClearAllData_`, `TestSPIFlash_`, `UpdateModule_MinVersion` | 3.30.0 | copies of `ProtocolCDC_MinVersion` |
| `BLEStatus_MinVersion` | 3.32.0 | literal |
| `ClearAllSplitLinks_MinVersion` | 3.34.0 | literal |
| `ActivityTimeouts_MinVersion` | 3.36.0 | literal |
| `UpdateFW_MinVersion` | 0.0.0 | literal |
| `naya_fw::module::ProtocolCDC_MinVersion` | module 2.3.0 | literal |
| `naya_fw::dongle::ProtocolCDC_MinVersion` | dongle 0.1.0.2 (as written) | literal |

Each `naya_fw::X_MinVersion` without a namespace copies `naya_fw::create::X_MinVersion`.

**Per operation** (`operationMinFWVersion(device type, operation)`, a switch on operations 0-13):
UpdateModule (operations 3 and 4), UpdateFW (5), Pair (6), Keymap (7), ClearAllData (8), TestSPIFlash (9)
and BLEStatus (10 and 13) for the Create; the dongle's ProtocolCDC value for the dongle; "Unsupported"
or "Unknown" otherwise. Keymap, ClearAllData, UpdateModule and operation 13 apply to the left half only.

**Per command** (`commandMinFWVersion(device type, category, subcommand)`), for the Create halves:

| Commands | Minimum | Note |
|---|---|---|
| `30/1001`-`30/100e`, `30/10ca` | 3.30.0 | left half only ("Unsupported" on the right) |
| `be/1001`-`be/100b` | 3.30.0 | |
| `be/100c`-`be/100f` | 3.32.0 | `be/100c` is "Unsupported" on the right half |
| `be/1010` | 3.34.0 | ClearAllSplitLinks |
| `de/1001`-`de/100b` except `de/1004` | 3.30.0 | |
| `ed/1003`-`ed/1011`, `ed/10d1`, `ed/10d2`, `ed/1050` | 3.30.0 | `ed/1012`-`ed/1014` are "Unknown" to the table |
| `ee/10ae`, `ee/10be`, `ee/10ce` | 3.30.0 | |
| `fa/1001`, `fa/1002`, `fa/1006` | 3.30.0 | |
| `fe/1001`-`fe/1009` | 3.30.0 | |
| `fe/100a`, `fe/100b` | 3.36.0 | activity timeouts |
| all `ca/*` and `f1/*` | 3.30.0 | |

This matches what we measured on old firmware: 3.28.7 answers no Bluetooth opcode from `be/100c` up
<span class="tag measured">MEASURED</span> (donor board, 3.28.7, 2026-09-19). The same literals appear
in beta NayaCore builds from 1.17.1 on, which is why those builds carry version strings that match no
image. naya-create-kb names the mechanism and some of the gates but lists ClearAllSplitLinks and
ActivityTimeouts under the operation switch, and calls the values unrecoverable[^kb-functions]. How
NayaCore acts on a failed gate beyond these return values (refusal, warning) is
<span class="tag open">OPEN</span>. CHECK_HANDSHAKE is "not implemented on version %1.%2.%3 of CORE"
for some firmware <span class="tag static">STATIC</span>[^nc]. The same tables, read as firmware
requirements, are on [Differences by firmware](../protocol/firmware-differences.md#minimum-firmware-per-command)
and [Versions](../firmware/versions.md#minimum-firmware-nayacore-expects).

Device behavior any version gate has to reflect <span class="tag measured">MEASURED</span>: 3.28.7 has no
Bluetooth opcode from `be/100c` up (no frame at all), two CDC interfaces per half, and wedges on any
three-frame write; 3.35.4 does not return the second bank; 3.41.0 changed the LED payload between halves
(donor board 3.28.7, 2026-09-19; owner's board 3.35.4/3.41.0, 2026-09-20/22; create-legacy-firmware[^nh-hw]).

## Device operations

NayaCore names the steps of each operation <span class="tag static">STATIC</span>[^nc]:

| Operation | Steps and notes |
|---|---|
| FWUpdate | OffsetInitialization, Initialize, SpawnBroker, CheckIfDoneBrokering, Brokering, SpawnSystem, SpawnProtocol, RestartingInMCUBoot, RestartingInDFU, Restarting, Reconnecting, MCUBoot_Restart, MCUBoot_Connect, MCUBoot_Upload, Create_PostUpdateVersionCheck, Completed. Version statuses: NotReady, NotFound, Legacy, OutOfDate, UpToDate, Future. The bundled image is picked per half and flash generation; NayaCore refuses when the generation is unknown. After an update that crosses the Bluetooth boundary it runs ClearBLEDevices ("updated to %2 (above BLE version)"). |
| Pairing | `repair_ble_address`, `wait_300ms`, `clear_all_split_links`, `unpair_all_pairs`, `wait_1000ms`, wait for the peer, `normal_reset`; also named ExchangeBLEAddresses, WaitForPairingPeerBeforeNormalReset, VerifyBLEAddresses; refusals "Devices have different firmware versions" and "Pairing failed: missing device(s) (left=%1, right=%2)". The same order was run by hand on one board on 3.35.4 (2026-09-20) and repaired a dead split link, and the owner reports a second repair on 3.41.0 <span class="tag measured">MEASURED</span>; no tool has automated it on hardware. See [Split link](../connectivity/split-link.md). |
| ClearBLEDevices | CheckBLEFWVersion, WaitForPairAddress, StorePairedHalfAddressBeforeClear, ClearConnections (`clear_all_connections`), VerifyBLEFWVersion, VerifyConnectionsCleared, RecheckBLEStatus: the paired half's address is saved before the clear so the split link survives (purpose <span class="tag inferred">INFERRED</span> from the names). |
| TestSPIFlash | VerifySPIFlashState, ReformatErrorPartitions, NormalRestart, VerifySPIFlashStatePostReformat (above). |
| ModuleFwUpdate | ModuleFW_FileVerification, ModuleFW_FileVerificationPostUpload, ModuleFW_Update (per type ModuleFW_Touch_Upload, _Track_Upload, _Tune_Upload, _Read_Upload), ModuleFW_VersionCheck; forced updates exist only for Touch, Track and Tune; statuses `Touch/Track/Tune/Float:IncorrectFW`. Module restart modes `M_NORMAL_RESTART`, `M_MCUBOOT_RESTART`, `M_CLEAR_REMAP_FLASH`. |
| clear_data (ClearAllData) | Clearing, ReadData, VerifyDataCleared (above). |

Per-device facts NayaCore tracks: DeviceType, FWVersion, SPIFlashTestResponse, MacAddressSelf,
MacAddressPair, BLEName, BLEFWVersion, BLEStatus, DeviceProfile, ModuleImage, ModuleType,
ModuleFWVersion, ModuleBatteryVoltage, InternalBatteryVoltage, ChargingSource (`Battery`, `USB_Qi`),
USBVoltage. Device types: CreateLeft, CreateRight, Dongle, ModDock, TypeLeft, TypeRight, TypeOne
<span class="tag static">STATIC</span>[^nc].

## Host maps

NayaCore turns an action name into record parameters through nine QMap globals filled by one static
initializer; they sit on one page of the arm64 build (the community KB's "statics on page
`0x100af0000`", which it reads as members `+0x70` to `+0xb0` of one object) and are separate named
globals <span class="tag static">STATIC</span>[^nc-mac]; also reported by naya-create-kb[^kb-maps]:

| Global | arm64 | x86_64 | Entries | Used by |
|---|---|---|---|---|
| `naya_zmk::FLOW_AT_TO_ZMK` | `0x100af0070` | `0x100bab070` | 13 | nothing (filled and never read) |
| `naya_zmk::BT_CODE_TO_PARAM` | `0x100af0078` | `0x100bab078` | 8 | `param1`, `param2`, `readBytes` |
| `naya_zmk::KEY_CODE_TO_PARAM` | `0x100af0080` | `0x100bab080` | 282 inserts, 281 names | `param1`, `readBytes` |
| `naya_zmk::OUT_CODE_TO_PARAM` | `0x100af0088` | `0x100bab088` | 2 | `param1`, `readBytes` |
| `naya_zmk::LED_CODE_TO_PARAM` | `0x100af0090` | `0x100bab090` | 19 | `param1`, `param2`, `readBytes` |
| `naya_zmk::MODF_CODE_TO_MASK` | `0x100af0098` | `0x100bab098` | 26 | `param1`, `readBytes` |
| `naya_zmk::NAYA_CODE_TO_PARAM` | `0x100af00a0` | `0x100bab0a0` | 8 | `param1`, `readBytes` |
| `naya_zmk::MOUSE_CODE_TO_PARAM` | `0x100af00a8` | `0x100bab0a8` | 15 | `param1`, `param2` |
| `naya_zmk::MOUSE_CODE_TO_PARAM_PAIR` | `0x100af00b0` | `0x100bab0b0` | 13 | nothing (filled and never read) |
| `naya_log::LogManager::s_instance` / `s_instanceMutex` | `0x100af00b8` / `0x100af00c0` | `0x100bab0b8` / `0x100bab0c0` | | the log manager's singleton pointer and its mutex (`instance()` locks, reads, unlocks); not maps |

The same page also holds `naya_remap::FW_KEY_POSITIONS`, `FW_MODULE_CONFIG_POSITIONS`,
`FW_LED_LEFT_POSITIONS` and `FW_LED_RIGHT_POSITIONS` (not extracted here), and the word lists NayaCore
uses to name each half (`naya_device_name::COLOR_ADJECTIVES`, `EMOTION_ADJECTIVES`,
`HOUSEHOLD_APPLIANCES`, `ANIMALS`) sit just before it <span class="tag static">STATIC</span>[^nc-mac].
naya-create-kb read `+0xb8`/`+0xc0` as a mutex-guarded lazy singleton with double-checked locking; the
names confirm singleton and mutex, and `instance()` has no double check.

### Record types and bodies

The record-type table (index = record type byte): `00` bluetooth, `01` key_press, `02` macro, `03`
mod_tap, `04` grave_escape, `05` mo, `06` naya_integrations, `07` none, `08` outputs, `09` rgb_ug, `0a`
sticky_key, `0b` sticky_layer, `0c` to_layer, `0d` toggle_layer, `0e` trans, `0f` mouse; at Windows file
offset `0x3ee220`-`0x3ee2e0`. Length checks exist for key_press, to_layer, toggle_layer, mo,
sticky_layer, bluetooth, rgb_ug, outputs, naya_integrations, mouse; sticky_key, grave_escape and macro
are named but not flashable <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>
(eight types matched against wire captures, owner's board, 3.41.0). Details on [Keymap](../protocol/keymap.md).

`Binding::serializeBindingData` looks up the record type for the Flow action type in a u32 table
(arm64 `0x100a37a78`: action types 0, 6 and 20 -> `01`; 1 -> `0c`; 2 -> `0d`; 3 -> `05`; 4 -> `0b`;
7 -> `0e`; 13 -> `00`; 14 -> `09`; 15 -> `08`; 19 -> `06`; 21 -> `0f`; the rest -> `07`), then picks the
body by bitmask <span class="tag static">STATIC</span>[^nc-mac]:

| Mask | Record types | Body |
|---|---|---|
| `0x3962` | `01`, `05`, `06`, `08`, `0b`, `0c`, `0d` | `[T][04][u32]` |
| `0x8201` | `00`, `09`, `0f` | `[T][08][u32][u32]` |
| `0x4080` | `07`, `0e` | no parameter |

So the community KB's "Type-19" (action type 19, the naya integrations) is record type `06` in the
`0x3962` group, as it says[^kb-maps]. `FLOW_AT_TO_ZMK` holds an older copy of that action-to-record
table: {0:`01`, 1:`0c`, 2:`0d`, 3:`05`, 4:`0b`, 5:`02`, 6:`01`, 7:`0e`, 8:`07`, 9:`06`, 13:`00`,
14:`09`, 15:`08`}; 11 entries match the live table and 5 -> `02`, 9 -> `06` differ. Its only references
are its initializer and a teardown routine; `serializeBindingData` never touches it: a "write-only map",
as naya-create-kb found <span class="tag static">STATIC</span>[^nc-mac][^kb-maps].

Parameters: a two-word map value holds two u32 halves, and two-word wire records carry the high half
first: `[T][08][high u32 LE][low u32 LE]` (for example BT_DEVICE_1 = `00 08 03000000 01000000`). In
NayaCore's own names `Binding::param1()` returns the high half and is written first, `param2()` the low
half; naya-create-kb labels them the other way round with the same wire result. The Windows tables store
pairs as (argument, command) in memory while the wire order is (command, argument)
<span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc-mac] (owner's
board, 3.41.0, 2026-09-08).

### Keys and modifiers

- **Key map**: 282 inserts of `(name, u32)` from one array, identical in the arm64 and x86_64 builds;
  `KP_CLEAR` is inserted twice with the same value, so the map holds 281 names (names and aliases). As
  a u32: plain keys `0x0007HHHH` (A = `0x04`, F1-F12 = `0x3a`-`0x45`, F13-F24 = `0x68`-`0x73`), shifted
  `0x02..` (modifier bits in the top byte), consumer `0x000cHHHH` (C_MUTE `0xe2`, C_PREVIOUS `0xb6`),
  system `0x0001HHHH` (SYSTEM_POWER / SLEEP / WAKE_UP = `0x81`/`0x82`/`0x83`)
  <span class="tag static">STATIC</span>[^nc-mac]; the 282 count is also naya-create-kb's[^kb-maps],
  whose system-key pattern `0x000100HHHH` has two extra zeros. The Windows build's parameter table is a
  different view: 249 four-byte entries `[usage lo][usage hi][page][mods]` at file offset `0x77a9d8` in
  ZMK `keys.h` order (page `0x07` 248 names, `0x01` system, `0x0C` consumer 27 names, of which the
  catalog exposes 11) <span class="tag static">STATIC</span>[^nc].
- **Name quirks**: DELETE `0x4c` with alias DEL; KP_CLEAR `0xd8`; K_LOCK, K_SCREENSAVER, K_COFFEE all
  `0xf9`; PIPE2 = shift + NON_US_BACKSLASH (`0x64`); CLEAR2 = shift + KP_NUMLOCK (`0x53`); INTn /
  INTERNATIONAL_n and LANGn / LANGUAGE_n alias families <span class="tag static">STATIC</span>; also
  reported by naya-create-kb[^kb-maps].
- **CLEAR is `0x9c`** (HID Keyboard Clear) and `SINGLE_QUOTE` is `0x34`, in both macOS builds (arm64
  computes `0x70090 + 0xc`; x86_64 stores the immediate `0x7009c`) <span class="tag static">STATIC</span>[^nc-mac].
  naya-create-kb reads CLEAR as `0x34`, the quote key[^kb-maps]; that is not what NayaCore's map holds.
- **Modifier bits** (`MODF_CODE_TO_MASK`, 26 names; the Windows u32 table at `0x77a9b8`): LCTRL 1,
  LSHIFT 2, LALT 4, LGUI 8, RCTRL 16, RSHIFT 32, RALT 64, RGUI 128. Accepted names: the eight HID
  modifiers plus CTRL, LEFT_CTRL, SHIFT, LEFT_SHIFT, ALT, LEFT_ALT, GUI, META, CMD, LEFT_GUI, LEFT_META,
  LMETA, LCMD, LWIN, LEFT_WIN, LEFT_COMMAND, RIGHT_CTRL, RIGHT_SHIFT. There is no RIGHT_ALT, RIGHT_GUI,
  RIGHT_META, RIGHT_WIN, RIGHT_COMMAND, RMETA, RCMD or RWIN <span class="tag static">STATIC</span>[^nc][^nc-mac].
  naya-create-kb says 27 names; its own list has 26.
- Composite codes are split on `" + "`: each extra part ORs its modifier bit into the top byte, so
  `Shift + A` = `0x02070004`. Bracketed modifiers in NayaFlow shortcuts (`[LALT] + TAB`) mean "already
  held" and are not set in the record (`2b 00 07 00`). Module axis codes are written `kind - NEG - POS`
  and split on `" - "` <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>
  (a NayaFlow capture of 80 shortcuts, 79 byte-exact).

### Bluetooth, outputs, LED and mouse

| Map | Values | Evidence |
|---|---|---|
| Bluetooth (8) | BT_CLEAR `0`, BT_NEXT `0x100000000`, BT_PREV `0x200000000`, BT_SELECT_SL `0x300000000`, BT_DEVICE_1..4 `0x300000000 + n`. On the wire BT_DEVICE_n is `[KK] 00 08 03000000 0n000000` (one-based; device 1 = profile slot 1 in the `be/100c` numbering; slot 0 only through SELECT_SL, which the catalog does not offer); BT_CLEAR is a real (0, 0) record. The catalog offers BT_DEVICE_1-4 and BT_CLEAR only. naya-create-kb writes DEVICE_n as `0x30000000 + n` (one zero short). | <span class="tag static">STATIC</span>[^nc-mac][^nc] <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-08/10) |
| Outputs (2) | USB_DEVICE = 1, BT_OUT = 2; on the wire `08 04 01000000` / `08 04 02000000` (record type `08`, outputs, not a layer switch) | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (2026-09-08) |
| LED (19) | EFFECT_ON_OFF `0`, BRIGHTNESS_UP/DOWN `0x7`/`0x8` << 32, SPEED_UP/DOWN `0x9`/`0xa` << 32, EFFECT (cycle) `0xb` << 32, effect select `0xd` << 32 with SOLID 0, BREATHE 1, SWIRL 2, SPEC(trum) 3; colors `0xf` << 32 with the low word `(h << 16) + (s << 8) + b`: RED 25700 (h0 s100 b100), ORANGE 1991780 (h30), YELLOW 3957860 (h60), GREEN 7890020 (h120), CYAN 11822180 (h180), BLUE 15754340 (h240), MAGENTA 17720420 (h270), PINK 19686500 (h300), WHITE 100 (h0 s0 b100). This is ZMK's `RGB_COLOR_HSB` packing, every color at brightness 100, and WHITE is regular. In the initializer ORANGE's value is built first and RED, GREEN, YELLOW, CYAN and BLUE are derived from it by hue arithmetic (a compiler detail). naya-create-kb's packing `S + (B << 8) + (H << 16)` with B = 70 and a "raw" WHITE do not hold: its own RED value 25700 = `0x6464` gives B = 100. | <span class="tag static">STATIC</span>[^nc-mac][^nc] <span class="tag measured">MEASURED</span> (the stock System layer read back 2026-09-08: WHITE `64 00 00 00`, RED `64 64 00 00`, GREEN `64 64 78 00`, BLUE `64 64 f0 00`) |
| Mouse (15) | (function, signed value): MOUSE_LEFT (0, -1), RIGHT (0, 1), UP (1, -1), DOWN (1, 1), SCROLL_UP (4, 1), SCROLL_DOWN (4, -1), SCROLL_LEFT (6, -1), SCROLL_RIGHT (6, 1), ZOOM_IN (8, 1), ZOOM_OUT (8, -1), M1-M5 = (3, 1/2/4/8/16). On a key: M1 = `[KK] 0f 08 03000000 01000000` (a real left click); mask 16 = X-button 2 (browser Forward); a short `0f 04 01000000` is stored and does nothing; a `(4, -1)` record scrolled a Windows page down. The motion codes are offered only in the module editor, never on keys. | <span class="tag static">STATIC</span>[^nc-mac][^nc] <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-06/07, 2026-09-16) |
| Mouse pairs (13) | `MOUSE_CODE_TO_PARAM_PAIR`: the same pairs without ZOOM_IN/OUT, with the two halves swapped (MOUSE_LEFT = `0xffffffff00000000`); filled and never read in 6.11.0. naya-create-kb guessed a read-back index. | <span class="tag static">STATIC</span>[^nc-mac] |

### Naya integrations and motion categories

- **Naya integrations** (record type `06`, u32 LE id): TUNE_MODE_L 150, TUNE_MODE_R 151, WINDOWS_OS 200,
  MAC_OS 201, SCROLL_DIRECTION_L 300, SCROLL_DIRECTION_R 301, MODULE_CHARGING 400, MODULE_FORCE_CHARGING
  401 (`NAYA_CODE_TO_PARAM` in the macOS builds; names at Windows file offset `0x77bdb0`, ids at
  `0x77ae60`). Only 401 is in the 1.25.1 catalog and only 401 has a wire sample: `3e 06 04 91 01 00 00`
  (position 62 of the stock System layer) <span class="tag static">STATIC</span>
  <span class="tag measured">MEASURED</span> (2026-09-08). TUNE_MODE_L would be `[KK] 06 04 96 00 00 00`
  <span class="tag inferred">INFERRED</span>. naya-create-kb says type 6 has no genuine wire sample; it has.
- NayaCore also knows app action types `configuration_rude_toggle`, `_l`, `_r`, `core`,
  `core_toggle_hold_morph` that no catalog record uses <span class="tag static">STATIC</span>
  ([details](../open-questions.md#oq-s07)).
- **MODULE_FORCE_CHARGING** acts only on the half whose key is pressed (bind one per side): that half's
  LEDs go out, its bay force-charges the module, the module is not usable meanwhile, the mode ends by
  itself and a restart clears it <span class="tag measured">MEASURED</span> (donor board 3.28.7,
  2026-09-19; owner's board 3.41.0) <span class="tag doc">DOC</span> (catalog tooltip "recover module
  from a critically drained battery ... Restart your keyboard to turn OFF this mode"[^bg]).
- **Motion categories** (the first u32 of a two-word `0f` record in a module field; a 9-entry map at
  arm64 `0x100aedfe8`, apart from the `naya_zmk` maps): MOUSE_HORIZONTAL 0, MOUSE_VERTICAL 1,
  MOUSE_STATIC 2, MOUSE_BUTTONS 3, MOUSE_SCROLL_VERTICAL 4, STATIC_SCROLL_VERTICAL 5,
  MOUSE_SCROLL_HORIZONTAL 6, STATIC_SCROLL_HORIZONTAL 7, STATIC_ZOOM 8. Measured: 0 pointer X, 1 pointer
  Y, 3 buttons, 4 vertical scroll, 6 horizontal scroll, 8 zoom (-1 pinch, +1 spread); 2, 5 and 7 are
  accepted but give no useful motion; the category is not tied to the field. They are values, not
  "behavior slots" as naya-create-kb calls them <span class="tag static">STATIC</span>
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-02 to 09-18). See
  [Module fields](../protocol/module-fields.md).

### Renderer icon vocabulary

The renderer's icon registry (`action-icons.json`) has 860 names: 12 consumer icons (C_BRIGHTNESS_DEC/INC,
C_FAST_FORWARD, C_JIS, C_MUTE, C_NEXT, C_PLAY_PAUSE, C_POWER, C_PREVIOUS, C_REWIND, C_VOL_DOWN/UP),
MB1-MB12, 20 KP_ icons, layer families MO_LAYER / TO_LAYER / TOGGLE_LAYER / HOLD_LAYER for ids 0-35
(with zero-padded aliases 00-09 and `$ID` templates), BT_DEVICE_1-5 (5 has no map entry), LED_GEN,
LED_GEN_2 and LED_BRIGHTNESS beyond the 19-name LED map, modifier variants LOPT/ROPT, LSHFT/RSHFT, RGUI,
`_JIS` and `_MAC` forms. Icon names are not wire actions <span class="tag static">STATIC</span>[^rend].
naya-create-kb counts 854 names; every family it lists is there[^kb-maps]. Many icon actions are proven
on the wire, not only MO: layer switches (`05` MO, `0b` sticky layer, `0c` TO, `0d` TOG), Bluetooth keys
(`00`), LED keys (`09`), output keys (`08`), mouse buttons (`0f`), MODULE_FORCE_CHARGING (`06`)
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-06 to 09-10).

NayaCore is 60 source files over a C++ `naya_remap` model (Binding, Key, Layer, Slot, ModuleConfig) on
top of ZMK behavior names; the firmware-side naming is <span class="tag inferred">INFERRED</span> from
the host <span class="tag static">STATIC</span>[^nc]. See [ZMK](../firmware/zmk.md).

## Open questions

- <span class="tag open">OPEN</span> Whether `30/10ca` with `00 00` (NayaCore, STATIC) and `01` (naya-create-kb's tool) behave the same: a donor-board test ([details](../open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> How NayaCore acts on a failed version gate beyond the returned value ([details](../open-questions.md#oq-f17)).
- <span class="tag open">OPEN</span> What the MCUboot worker's "connection test" sends to tell the data port from the log port ([details](../open-questions.md#oq-s06)).
- <span class="tag open">OPEN</span> The naya-integration ids other than 401, and what `configuration_rude_toggle*`, `core` and `core_toggle_hold_morph` do ([details](../open-questions.md#oq-s07)).
- <span class="tag open">OPEN</span> The contents of the `FW_*_POSITIONS` lists (not extracted yet).

## Sources

[^nc]: NayaFlow 1.25.1 for Windows, `core/NayaCore/NayaCore.exe` (NayaCore 6.11.0): strings and data tables (file offsets as given); NayaFlow 1.17.3 NayaCore for comparison.
[^nc-mac]: NayaFlow 1.25.1 for macOS, `NayaFlow.app/Contents/core/NayaCore.app/Contents/MacOS/NayaCore` in `NayaFlow-1.25.1-arm64-mac.zip` (MD5 `84ded78022b6d312483aae0192584168`) and `NayaFlow-1.25.1-mac.zip` (x86_64): symbols, static initializers, jump tables and code, read 2026-09-23.
[^bg]: NayaFlow 1.25.1, `flow/flow-bg-server.exe`: strings (catalog tooltips, vendor texts).
[^rend]: NayaFlow 1.25.1, `resources/app.asar`: the renderer's icon registry.
[^rel]: Vendor release notes of NayaFlow 1.25.0, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases) and the beta channel.
[^nh]: create-legacy-firmware, [`tools/`](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/tools) (`carve_fw.py`, `extract_history.py`, `flash_map.py`).
[^nh-manifest]: create-legacy-firmware, [`MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/MANIFEST.json).
[^nh-fp]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Slot ids" and "Product ids"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L158-L248) (the MCUboot worker and PID functions in both macOS builds).
[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py`, `docs/cdc-wire-format.md`, `bluetooth.py`).
[^kb-dis]: naya-create-kb, [disassembly](https://nemezzizz.github.io/naya-create-kb/disassembly/).
[^kb-functions]: naya-create-kb, [disassembly/functions](https://nemezzizz.github.io/naya-create-kb/disassembly/functions/).
[^kb-maps]: naya-create-kb, [disassembly/host-maps](https://nemezzizz.github.io/naya-create-kb/disassembly/host-maps/).
[^kb-rpc]: naya-create-kb, [software/rpc-zmq](https://nemezzizz.github.io/naya-create-kb/software/rpc-zmq/).

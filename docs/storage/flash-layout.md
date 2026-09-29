# Flash layout

This page covers where a Create half keeps its firmware slots and its data: the internal flash and
the external QSPI flash, what the read-only SPI-flash self-test reports, what the left half stores
that the right half does not, which settings persist, and one table of what survives what (power
cycles, resets, bootloader passes, firmware flashes, the vendor's repair and clear buttons, and
`30/10ca`). The thing to know first: the **left** half holds every configuration store, a firmware
flash leaves all of it alone, and nothing reads the flash over USB.

!!! note "At a glance"
    - Each half has an external QSPI NOR flash; the MCUboot secondary slot and LittleFS data live there.
    - `fa/1001` is a read-only self-test: 5 partitions on the left, 3 on the right.
    - The left half stores the keymap, LED maps, layer list, module configurations and the module firmware bundle; the right stores none of them.
    - LED settings and activity timeouts are stored and survive reboots; there is no read command for the LED settings.
    - `fa/1002`, `fa/1006` and `30/10ca` destroy data; NayaFlow's "Clear all keymap data" sends `30/10ca`.

## Where things live

Each half has an external QSPI NOR flash beside the SoC: the silkscreen reads `QSPI_CS`,
`QSPI_CLK` and `QSPI_SIO0` to `SIO3`, the right half's chip carries a Winbond wordmark, and the
leadless package is about 4 mm square. The part number and capacity are unreadable in the filed photos
<span class="tag doc">DOC</span>[^fcc-ip][^parts]. naya-create-kb also describes an external SPI flash on each half.

The MCUboot secondary slot (648 KiB) is on the QSPI: two 648 KiB slots plus the bootloader
exceed the nRF52840's 1 MB internal flash, and NayaCore's flash test names a "Slot1 Partition
(Secondary Image - RAW)" <span class="tag inferred">INFERRED</span> <span class="tag static">STATIC</span>[^nc]. The primary slot is presumably in internal flash <span class="tag inferred">INFERRED</span>. Slot sizes:
[Bootloader](../firmware/bootloader.md#slots-and-upload-ids).

Nothing reads the flash over USB. The JEDEC id is not exposed; category `fa` has only
`1001` (test), `1002` (format partition) and `1006` (erase chip); `GET_SLOTX_ADDR` returns a slot
address, not contents; category `f1` FIRMWARE is declared without subcommands; and the bootloader's
file and read commands are not supported <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^nx] (owner's board, 2026-09-01).

The nRF52840's QSPI controller can encrypt on the fly; whether Naya stores QSPI contents
encrypted is unknown <span class="tag inferred">INFERRED</span> <span class="tag open">OPEN</span>[^nordic] ([open question](../open-questions.md#oq-f20)).

## The SPI-flash self-test

The QSPI data is organized as LittleFS partitions: NayaCore's flash-test code prints
LittleFS return codes (`LFS_ERR_CORRUPT` -84, `EINVAL` -22), and the partitions report "Mounted"
<span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc] (owner's board, 2026-09-10). naya-create-kb cites the same strings (`LFS_ERR_CORRUPT`,
`FORMAT_PARTITION`, `SPIFLASH_TEST`); its "VERIFY FLASH" is nayactl's name for `ff/1001`.

`fa/1001` is SPIFLASH_TEST, a read-only self-test that NayaCore sends on every connect. Its
reply is the status byte `00`, then 2 header bytes, then one 6-byte block per partition: a status
byte and five signed return codes (open, mount, file open, file read, file write; the order follows
NayaCore's print order and is **open**) <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc] (2026-09-10). It is not "device info", as some
naya-create-kb pages call it. Details: [Command map](../protocol/commands.md).

Counted after the status byte, the left half answers 32 bytes (5 partitions; NayaCore's
"CreateLeft" and "Dongle" shape) and the right half 20 bytes (3 partitions, "CreateRight"); NayaCore
rejects any other length ("Invalid data length received") <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc].

Partition status values: 0 Not Detected, 1 Detected, 2 Formatted, 3 Mounted, 4 Erased.
Return codes: 0 Success, -1 Generic Error, -22 EINVAL, -84 LFS_ERR_CORRUPT <span class="tag static">STATIC</span>[^nc].

A healthy 3.41.0 board <span class="tag measured">MEASURED</span> (owner's board, 2026-09-10):

| Half | Status | Header | Partition blocks |
|---|---|---|---|
| left | `00` | `01 00` | five times `03 00 00 00 00 00` (all Mounted, all codes 0) |
| right | `00` | `01 00` | one Not Detected block, then two Mounted blocks |

Header byte 0 = 1 fits the status of the "Slot1 Partition (Secondary Image - RAW)"
(Detected); header byte 1 is not the partition count <span class="tag inferred">INFERRED</span>.

The `fa/1001` opcode and the "Slot1 Partition" string are in NayaCore since at least
NayaFlow 1.17.3; the structured per-partition parser appears only in 1.25.1 (NayaCore 6.11.0); the
user-facing "Test and Format SPI Flash" button arrived with NayaCore 6.4.0 (beta 1.18.0, 2026-03-12;
stable 1.19.1) <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nc][^cl-250][^beta].

## Partitions

Candidate partition names: strings next to the flash-test code include `Layout`,
`Setting`, `Reserve` and `M_Firmware`. How they map to the five (left) or three (right) partitions is
**open**. `Battery` and `USB_Qi`, which sit in the same run of strings, are the charging-source
names, and there is no "Log" partition name <span class="tag static">STATIC</span> <span class="tag open">OPEN</span>[^nc] ([open question](../open-questions.md#oq-f18)).

## What each half stores

The **left** half holds every configuration store: the whole keymap (both banks), all LED
maps, the layer list, the module configuration list and slots, and the module firmware bundle; every
keymap write goes to `dst 0x50`. The right half holds none of them and reports key positions over the
split link <span class="tag measured">MEASURED</span> (owner's boards, 2026-09 captures and 2026-09-20). naya-create-kb also says the flash
stores the keymap profiles. NayaCore itself addresses every keymap command to `0x50` <span class="tag static">STATIC</span>[^nc].

The module bundle store is the left half's 1 MiB LittleFS partition (candidate
`M_Firmware`, 4 096-byte blocks), written by an SMP upload to id 4 with the left half in its
bootloader and read back with `de/100a`; the right half reports three partitions and has no module
store <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> ([Module firmware](../firmware/modules.md#where-the-keyboard-keeps-the-bundle)).
naya-create-kb also describes module apps and HASH files staged in flash for module updates.

Bluetooth bonds and the split-link pairing record are stored per half and survive firmware
flashes byte for byte; the pairing record also survives a firmware mismatch that stops the link from
working <span class="tag measured">MEASURED</span>[^fp-measured] (owner's board, 2026-09-20). Which partition holds them is **open**
([open question](../open-questions.md#oq-f19)).

The firmware's own settings store is not readable over USB on 3.41.0: the old
`dump_settings` text command answers nothing <span class="tag measured">MEASURED</span> (2026-09-11).

Configuration writes take effect immediately; there is no commit step <span class="tag measured">MEASURED</span> (2026-09-07).
naya-create-kb's writer also uses none.

## Persistent settings

Three LED settings are stored: `ed/1012` scan mode, `ed/1013` the maximum LED brightness (a
ceiling), and `ed/1014` the LED action override (0 = an LED action lasts until restart, 1 = until the
next layer change). They survive reboots, and there is no command that reads them back <span class="tag measured">MEASURED</span> (owner's
board, 3.41.0, 2026-09-13 and 2026-09-16). The ceiling scales the whole key array: 30 dimmed every key
and 100 restored them (2026-09-13) <span class="tag measured">MEASURED</span>. So a stored ceiling of 0 is a board that stays dark across
reboots <span class="tag inferred">INFERRED</span>, as the nayactl PR #6 author reports <span class="tag reported">REPORTED</span>[^nx-pr6]. The same author reports that module LEDs
are outside the ceiling <span class="tag reported">REPORTED</span>. naya-create-kb names the same three settings. See [LEDs](../protocol/led.md).

naya-create-kb names the stored keys `scanmode_pwm`, `led_layer_override` and "max LED
Brightness", and quotes the log line "No max LED Brightness found in the settings table. Resorting to
default." Those strings belong to NayaCore, the host service, not to the keyboard. The log line
follows NayaCore's query on NayaFlow's own SQLite settings table on the computer, and `scanmode_pwm`
and `led_layer_override` are field names in NayaCore's "Settings mismatch: ... Write=%1 Read=%2"
checks <span class="tag static">STATIC</span>[^nc]. What the keyboard's firmware calls these settings is unknown, because the firmware is
encrypted <span class="tag open">OPEN</span>.

**Activity timeouts.** `fe/100a` SET and `fe/100b` GET ACTIVITY TIMEOUTS carry three
32-bit little-endian millisecond values: LED idle, sleep, and a third field NayaCore names
`sleep_battery_time_ms` whose effect is unidentified <span class="tag static">STATIC</span>[^nc]. NayaFlow's default write is params
`00 90 5f 01 00 e0 93 04 00 30 75 00 00`: 90 000, 300 000 and 30 000 ms <span class="tag measured">MEASURED</span>. A board NayaFlow had not
yet written held 90 000, 600 000 and 15 000 ms <span class="tag reported">REPORTED</span> (raw data checked: its `fe/100b` reply
`00 90 5f 01 00 c0 27 09 00 98 3a 00 00` in naya-create-kb's maintainer's published captures). It is
a stored setting, which is why it is stable across reboots. On 3.41.0 values under 30 s are refused
with status `ea` and nothing is stored; 0 turns idle or sleep off (0 is not accepted for the third
field) <span class="tag measured">MEASURED</span> (owner's board, 2026-09-11). Details: [Settings and timing](../protocol/settings.md).

Whether `30/10ca` resets the timeouts is **open**; naya-create-kb's restore advice implies
that they survive only in its snapshot, not on the device <span class="tag inferred">INFERRED</span> ([open question](../open-questions.md#oq-f16)).

**Short ED writes are zero-filled, not rejected.** ED params are `00 <target> <value>` (the
flag byte, a target byte whose value is ignored, and the value), and a payload that stops early is
completed with zeros and acknowledged, so a one-byte "brightness" write stores 0. This is how a board
ends up with a zero ceiling <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-09 and 2026-09-10, one frame at a
time). naya-create-kb describes the same mechanism.

## What survives what

One table for every event. Rows with our measurements are marked MEASURED; rows that rest
on naya-create-kb are marked REPORTED.

| Event | Stores (keymap, LED maps, layer list, modules) | Persistent settings (LED settings, timeouts) | Live lighting | Evidence |
|---|---|---|---|---|
| Power cycle or USB replug | kept | kept | reset to the stored state | <span class="tag measured">MEASURED</span> (LED map byte-identical across a power cycle, 2026-09-10; the ceiling persists) |
| Power switch OFF then ON with USB plugged in | kept | kept | OFF shuts the half off; ON works as a reset | <span class="tag measured">MEASURED</span> (owner, 2026-09-23) <span class="tag doc">DOC</span> (the manual); contradicts naya-create-kb, which says it is not even an MCU reset |
| `ee/10ce` NORMAL_RESET | kept | kept | naya-create-kb: an OFF state and the `ed/1050` override survive it | <span class="tag reported">REPORTED</span> |
| Bootloader pass (`ee/10ae` then `os reset`, or any power-on) | kept | kept | **not** kept: comes back white or darker amber; a layer-list rewrite restores it | <span class="tag measured">MEASURED</span> (2026-09-20 and 2026-09-22) |
| Firmware flash, 3.35.4 and 3.41.0 both ways | kept byte-identical (both banks, layer identities, module slots) | not recorded: brightness came back low after the 3.41.0 upgrade, and re-sending the ceiling fixed it | not kept (as above) | <span class="tag measured">MEASURED</span> (2026-09-20 and 2026-09-22) |
| NayaFlow "Clear all keymap data" (`clear_data`) | wiped: it sends `30/10ca` (params `00 00`) and resets the board | naya-create-kb says the LED settings survive it, which conflicts with its report that `30/10ca` clears its dark-board state; whether the params form matters is open | | <span class="tag static">STATIC</span> (the route) <span class="tag reported">REPORTED</span> |
| NayaFlow "Test and Format SPI Flash" (`repair_flash`) | kept on a healthy flash; a failing partition is formatted | kept on a healthy flash | | <span class="tag static">STATIC</span> <span class="tag reported">REPORTED</span> |
| `30/10ca` CLEAR_ALL_DATA | wiped: keymap, LED maps, settings, layer list | settings reset per naya-create-kb; timeouts **open** | | <span class="tag reported">REPORTED</span> (untested by us) |

naya-create-kb says every row of its own survival table was proven live. Its firmware-flash and
repair rows agree with ours; its switch row is contradicted by the owner's measurement; its
clear-keymap row conflicts with the static route above.

## Destructive storage commands

FORMAT_PARTITION `fa/1002` (a one-byte partition selector, inferred) and ERASE_CHIP
`fa/1006` are destructive; ERASE_CHIP would take the staged firmware and all data on the device.
NayaCore's format results are success, ENODEV, ENOTSUP, EIO and LFS_ERR_CORRUPT. We have never run
either <span class="tag static">STATIC</span>[^nc][^nx]. Both are on the [never-send list](../troubleshooting.md#the-never-send-list).

`30/10ca` CLEAR_ALL_DATA clears the configuration data, as a device-side operation whose
internals are unknown (the firmware is encrypted); naya-create-kb calls it a format of the LittleFS
data partition <span class="tag reported">REPORTED</span>. NayaFlow's Danger Zone "Clear all keymap data" (`clear_data`) runs exactly this
command: ZMQ event 5 leads through NayaCore's ClearAllData operation to `30/10ca` with params `00 00`
<span class="tag static">STATIC</span>[^nc-disasm]. Details: [Factory reset](factory-reset.md).

!!! danger "`fa/1002`, `fa/1006` and `30/10ca` destroy data"
    None of them has been sent by us. `fa/1001` is the only safe `fa` command. `30/10ca` needs a
    complete snapshot first ([Factory reset](factory-reset.md#before-you-send-it-a-complete-snapshot)).

## The vendor's repair and clear buttons

NayaFlow's "Test and Format SPI Flash" (`repair_flash`) runs VerifySPIFlashState,
ReformatErrorPartitions, NormalRestart and VerifySPIFlashStatePostReformat: it formats only the
partitions that fail the self-test. Its outcomes: "No errors detected ... operation complete without
reformatting", "Errors detected ... failed after %2 reformat attempts", and "Test SPIFlash operation
critically failed. Your unit's SPIFlash may potentially be damaged." The interface warns that keymaps
may be overwritten. Its ZMQ form is `repair_flash` with `{"target_devices":[],"target_partitions":[]}`
<span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nc]. naya-create-kb also says it formats only after a failed self-test.

If the failing partition is the secondary slot or the module store, the repair's format
would lose a staged image or the module bundle <span class="tag inferred">INFERRED</span>. On a healthy board it formats nothing and reports that it completed without reformatting <span class="tag static">STATIC</span>[^nc].

!!! warning "The repair runs without a confirmation dialog"
    Safe on a healthy flash, destructive on a failing one. NayaFlow's other Danger Zone actions
    (`clear_data`, `clear_ble_devices`) have no confirmation dialog either.

NayaFlow's "Factory Reset" (in its General settings: "Reset all changes to Naya Flow")
resets the app's own settings, such as language and theme. It is not a device wipe, and it has no
ZMQ event of its own <span class="tag static">STATIC</span>[^nc]. Also reported by naya-create-kb.

## Things filed under storage that belong elsewhere

Deleted layers are not cleared by the firmware: a deleted layer's records and LED map stay
on the index <span class="tag measured">MEASURED</span> (2026-09-03). See [Layers](../protocol/layers.md).

The macro store is a stub: the macro list never returns entries, and macro writes are
acknowledged and discarded on 3.41.0; 3.28.7 answers the macro commands with status `11` (not
implemented) <span class="tag measured">MEASURED</span> (2026-09-07 and 2026-09-19).

The tapping term is not a device-wide header. It is stored in every hold-tap record (a
16-bit little-endian value in ms) next to the flavor, in both banks. NayaFlow writes its one global
value into every record: changing it from 200 to 180 changed exactly `c8 00` to `b4 00` in each
record <span class="tag measured">MEASURED</span> (USB capture, 2026-09-17). See [Keymap](../protocol/keymap.md).

`4b 02 00` is not a dirty flag: position `0x4B` is the Touch-right module bay, and its type
byte `02` points that bay at module configuration slot 2 <span class="tag measured">MEASURED</span> (2026-09-03). See
[Modules](../protocol/modules.md).

## Host-side storage

NayaFlow keeps its own data in an SQLite database, `user-data.db`, with automatic backups
(every 30 minutes when something changed, a ring of 10) and manual backups in a separate folder
<span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^cl-284]. Details: [App data](../software/app-data.md).

## Where this differs from naya-create-kb

| naya-create-kb says (storage pages) | What the evidence shows |
|---|---|
| Every store sits on each half | The left half holds every store; the right half has three partitions and no configuration or module store |
| A switch flip with USB plugged in is not even an MCU reset | It is a reset (owner, 2026-09-23), as the manual says |
| Nothing in the stock interface formats the data partition; only the hidden `30/10ca` | "Test and Format SPI Flash" formats failing partitions, and "Clear all keymap data" sends `30/10ca` |
| `fe/100b` is a "timeouts token" | It is GET ACTIVITY TIMEOUTS, a stored setting (hence stable) |
| The tapping term `c8 00` in the records mirrors a profile header | There is no device-wide term; it is stored per hold-tap record in both banks |
| `4b 02 00` is a sticky dirty flag | Position `0x4B` is the Touch-right bay pointing at configuration slot 2 |
| `scanmode_pwm` and `led_layer_override` are the keyboard's stored keys | They are NayaCore's field names; the "settings table" is NayaFlow's database on the computer |

## Open questions

- <span class="tag open">OPEN</span> The QSPI part number and capacity, and whether generation B uses a larger part ([details](../open-questions.md#oq-f06)).
- <span class="tag open">OPEN</span> Which partition name maps to which index; why the right half's first partition is Not Detected; the order of the five return codes; the meaning of header byte 1 ([details](../open-questions.md#oq-f18)).
- <span class="tag open">OPEN</span> Where bonds, settings and timeouts live, and whether `30/10ca` resets timeouts or bonds ([details](../open-questions.md#oq-f19)).
- <span class="tag open">OPEN</span> Whether the QSPI contents are encrypted at rest ([details](../open-questions.md#oq-f20)).
- <span class="tag open">OPEN</span> Whether module LEDs are really outside the brightness ceiling (third-party report only).

## Sources

[^fcc-ip]: FCC ID 2BQ4V0825CRL internal photos, exhibit 1, p9, and 2BQ4V0825CRR internal photos, exhibit 1, p8; see [Regulatory records](../hardware/regulatory.md).
[^parts]: [Parts list](../hardware/parts.md) (the QSPI part, unconfirmed readings).
[^nordic]: Nordic Semiconductor, nRF52840 Product Specification (QSPI peripheral).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings and macOS symbols (flash test and format, partition names and statuses, activity timeouts, settings checks and queries, repair state machine; NayaFlow renderer strings for the Danger Zone and General settings).
[^nc-disasm]: NayaFlow 1.25.1, macOS x86_64 NayaCore: the ZMQ name table maps `clear_data` to event 5; `_handleCommandMessage` case 5 emits `si_clearAllData_req_source`, which reaches `Naya_DeviceManager::doClearAllDataOperations`; `ProtocolCDCProcessWorker::_remapClearFlash` (`0x1004a29c0`) builds a one-byte array filled with `00` and passes it to `_constructRemapMessages` with `0x10ca`, which queues it for `dst 0x50`. See [Disassembly](../software/disassembly.md).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py`).
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6), description by its author.
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384).
[^cl-250]: create-legacy-firmware, [`CHANGELOG.md` L250 and L263](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L250-L263) (NayaFlow 1.19.1, NayaCore 6.4.0).
[^cl-284]: create-legacy-firmware, [`CHANGELOG.md` L81 and L284](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L284) (periodic and manual backups).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases), v1.18.0.

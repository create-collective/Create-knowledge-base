# Troubleshooting

This page lists problems people actually hit, as symptom, cause and what to do, each scoped to the
firmware it was seen on; the vendor's own list of known bugs by firmware; and the site's one list of
commands never to send, or to send only with a recipe at hand. Long procedures live on
[Recovery](recovery.md). The thing to know first: many "failures" are not failures (an
acknowledgement with a second byte, a half that answers with empty payloads, a silent bootloader
swap), and a few innocent-looking commands are writes that cannot be undone.

!!! note "At a glance"
    - Check the firmware version of **both** halves before anything else.
    - One program per serial port; NayaFlow holds the ports while it runs.
    - A write acknowledgement proves the frame parsed, not that it took effect.
    - An empty or short ED payload is a zero-filled write, not a read.
    - The never-send list is at the [bottom of this page](#the-never-send-list).

| Symptom | Entry |
|---|---|
| Port busy, "Access is denied", "Resource busy" | [Host and port problems](#host-and-port-problems) |
| Writes "fail" on layers 1 and 2 | [Failures that are not failures](#failures-that-are-not-failures) |
| The right half "never answers" | [The right half](#the-right-half) |
| Board dark but typing; dim board; odd brightness | [LEDs and brightness](#leds-and-brightness) |
| Firmware update stuck at the start or silent at 100 % | [Firmware update problems](#firmware-update-problems) |
| Double-tap keys missing or firing wrong | [Keymap surprises](#keymap-surprises) |
| Battery percentage looks wrong; empty dock reads | [Modules and battery readings](#modules-and-battery-readings) |
| Anything after a vendor update | [Vendor-known bugs by firmware](#vendor-known-bugs-by-firmware) |

## Scope and first checks

Entries here were observed on 3.28.7, 3.35.4 or 3.41.0 (Windows host), or, where marked
REPORTED, by the third party the entry names. The beta-only firmware (3.39.4, 3.40.0, 3.40.4) is
unmeasured. Check `fe/1002` on both halves before applying any entry <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span>
([Versions](firmware/versions.md#firmware-in-the-field)).

## Host and port problems

**Port busy or will not open.** Another program holds it: NayaFlow's NayaCore or
flow-bg-server, OpenFlow, or a killed script's leftover Python process. Windows reports "Access is
denied" (error 5) <span class="tag measured">MEASURED</span>. On macOS the error is "Resource busy": NayaCore opens its ports through Qt's
serial-port module, which opens them exclusively, so a second open fails with `EBUSY` (errno 16)
<span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>[^nc]. Quit the other program. OpenFlow can release its ports without the halves re-enumerating. Safety
SAFE. TESTED (us, Windows).

**Windows serial specifics.** pyserial with `dsrdtr=True` can hang the first write
forever: use `dsrdtr=False` and a write timeout. A half that dropped off uncleanly can come back on a
new COM number while the old one stays listed (a "ghost" port). After a power cycle a held handle
fails with "WriteFile failed ... The device does not recognize the command". Docking or undocking a
module re-enumerates that half's USB, so open handles go stale and NayaFlow relaunches <span class="tag measured">MEASURED</span>[^nx-pr2]
(owner's board, 2026-09-10 and 2026-09-18). More on [Platforms](tools/platforms.md).

**Linux.** Each half is a `/dev/ttyACM*` device owned by `root:dialout`; ModemManager
probes new serial ports for seconds after they appear; a udev rule for vendor `37d1` (ModemManager
ignore plus `uaccess`) fixes both. OpenFlow ships such a rule; nayactl's README describes the port
ownership <span class="tag static">STATIC</span> <span class="tag reported">REPORTED</span> <span class="tag inferred">INFERRED</span>[^nx]. Nothing here has been measured on a Linux machine with a keyboard
attached ([USB](connectivity/usb.md)).

**Two ports per half on 3.28.7.** 3.28.7 shows two COM ports per half (interfaces MI_00
plus MI_02 or MI_03, the same serial number, both "OK"); only one answers, and which one is not
predictable. 3.41.0 exposes one <span class="tag measured">MEASURED</span> (owner's boards, 2026-09-19 and later).

## Failures that are not failures

**Writes that "NACK" on layers 1 and 2.** The acknowledgement of a keymap write is status
`00` followed by the layer index: `00 00` on layer 0, `00 01` on 1, `00 02` on 2. The second byte is
data, not an error, so a matcher that accepts only `00 00` fails every write above layer 0.
Non-final frames of a chunked write are acknowledged with status `01` plus the index; status `ea`
means the firmware refused the value and stored nothing <span class="tag measured">MEASURED</span> (owner's board, 2026-09-07 and
2026-09-11). Frame details: [Transport](protocol/transport.md).

**An acknowledgement proves parsing, not effect.** The firmware acknowledges writes it
discards (macro writes) and stores records it will not act on (short parameters). Read back, and for
behavior, press the key <span class="tag measured">MEASURED</span> (2026-09-07).

**LED map writes need the layer byte.** A single-entry `30/100e` write is
`00 <layer> <KK> <H_lo> <H_hi> <S>`: the second byte picks the layer, and the acknowledgement echoes
it. NayaFlow's own writes to layers 0, 3 and 4 carry it (our capture, 2026-09-01), and OpenFlow's
writes to layers 1 and 2 read back per layer (owner's board, 2026-09-16) <span class="tag measured">MEASURED</span>. So a writer that always
sends `00` in that position writes layer 0. See [LEDs](protocol/led.md).

## The right half

The right half does answer. On its own port it answers the connect handshake (`fe/1001`
MEDIA_ID_REQUEST and `fe/1002`) and system, Bluetooth, module and `fa/1001` reads <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>. `30/1001`
is READ LAYER LIST, not a handshake, and the right half has no layer list: every configuration store
is on the left. To reach the right half from the left port, address `dst 0x51`: only the central
routes. Not everything sent that way answers for the right half: the firmware-version read does
(owner's board, 2026-09-22)[^fp-measured], but the Bluetooth identity reads sent to `0x51` through the
left answer for the **left** half ([Split link](connectivity/split-link.md)). The right half also
answers `ed/1013` on its own port (owner's board, 3.35.4 and 3.41.0, 2026-09-20 and 2026-09-22) <span class="tag measured">MEASURED</span>.

While the halves run different firmware, the peripheral's own port answers the handshake
and then returns empty payloads to every command. It still types, and its version stays readable
through the central's port at `dst 0x51`: the left port read the right half's version 3.35.4 while
the right half's own port was hollow <span class="tag measured">MEASURED</span>[^fp-measured]. OpenFlow never built an automatic retry
through that route; the route itself is measured. See [Recovery R3](recovery.md#r3-halves-on-different-firmware).

## LEDs and brightness

**Short ED payloads are zero-filled, not rejected.** ED params are `00 <target> <value>`;
the target byte's value is ignored (0, 1, 2, 3 and 200 behaved the same), and a payload that stops
early is completed with zeros and acknowledged. A one-byte brightness write leaves the half dark; a
one-byte effect write always selects effect 0. Always send the target byte and the value <span class="tag measured">MEASURED</span>
(owner's board, 3.41.0, 2026-09-09 and 2026-09-10, one frame at a time). This differs from
naya-create-kb, which describes an empty `ed/1013` as a read returning a bare
acknowledgement[^kb-troubleshooting]: by this rule that frame stores a ceiling of 0 and darkens the
keys <span class="tag inferred">INFERRED</span>. See [LEDs](protocol/led.md).

**There is no read command for the LED settings** (`ed/1012`, `1013`, `1014`), and an
empty-payload "read" is not harmless: it is a zero-filled write, so it stores scan mode 0 or a ceiling
of 0 <span class="tag inferred">INFERRED</span> (from the measured zero-fill).

**Dim board after a firmware update.** After the 3.41.0 upgrade both halves came up so dim they
looked off until the ceiling was re-sent to each half's own port (`ed/1013` 100, params `00 00 64`),
and both relit <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20 and 2026-09-22).
Whether the flash changed the stored ceiling or only the live level was not recorded. Re-sending the
ceiling: Safety LOW, TESTED (us, 3.41.0).

**Board dark but typing.** See [Recovery R6](recovery.md#r6-board-dark-but-typing). A stored
setting can do it: the ceiling scales the whole key array and persists, and short ED writes store
zeros, so a zero ceiling would give a dark board that types <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>; the nayactl PR #6
author revived a board that had been dark for weeks by re-sending the ceiling
<span class="tag reported">REPORTED</span>[^nx-pr6]. It is not the only cause: a runtime lighting state after a
bootloader pass or an LED effect also darkens a half until a layer-list rewrite or a power cycle
(Recovery R5) <span class="tag measured">MEASURED</span>. A firmware flash does not help, because the stores survive it, and neither
does the vendor's flash repair on a healthy flash <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>. NayaFlow's "Clear all keymap
data" is no light fix either: it sends `clear_data`, which runs ClearAllData and `30/10ca` with params
`00 00` (frame `aa 00 50 00 30 04 10 ca 00 00 da 04`) and wipes the stored configuration
<span class="tag static">STATIC</span>[^nc] ([Factory reset](storage/factory-reset.md#the-command-and-its-parameters)).
This differs from naya-create-kb, whose own tool sends params `01`, having read the byte array's size
argument as its value <span class="tag reported">REPORTED</span>[^kb-troubleshooting].

**A logged "success" in NayaFlow** means the command ran, not that anything changed:
the flash test, for example, reports "No errors detected ... operation complete without reformatting"
while changing nothing <span class="tag static">STATIC</span>[^nc]. The reverse happens too: NayaFlow
once reported a failed flash that had in fact landed, and only NayaCore's log told the truth; and its
verify fails on multi-binding keys whose writes did apply <span class="tag measured">MEASURED</span> (owner's board, 2026-09).

**Right half dark while the board types.** Check first that both halves run the same firmware: a
mismatch darkens the peripheral's LEDs until the halves match <span class="tag measured">MEASURED</span> (owner's board, 3.35.4 and
3.41.0, 2026-09-20; [Recovery R3](recovery.md#r3-halves-on-different-firmware)). If they match and the
right half's keys do not arrive either, the split link is the suspect: NayaCore's pairing order, run
by hand, fixed a dead link <span class="tag measured">MEASURED</span>
([Recovery R4](recovery.md#r4-right-half-scans-but-its-keys-never-arrive)), and clearing the
computer's Bluetooth bonds does not help, because the link lives in the halves <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>. After LED
writes sent to the right half's port, see
[Recovery R7](recovery.md#r7-right-half-dark-after-led-commands-sent-to-it). The firmware check is
Safety SAFE.

## Firmware update problems

**Stuck at the start**: the first chunk waits while the bootloader erases 648 KiB (6 to
17 s; once 55 s in an interface run). **Silent after 100 %**: the bootloader is swapping (about
100 s). **A half dark afterwards** is usually still in its bootloader because the reset did not take:
re-send `os reset` ([Recovery R1](recovery.md#r1-half-dark-and-not-typing-shows-up-as-a-bootloader-device)).
Never unplug during any of these. Re-sending the reset: Safety LOW, TESTED (us, 2026-09-20 and
2026-09-22) <span class="tag measured">MEASURED</span>[^fp-measured]. Details: [Flashing](firmware/flashing.md#failure-modes).

**A half can silently miss a vendor update.** One board arrived with its right half still
on 3.35.4 in both slots while the left ran 3.41.0 <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20).

## Keymap surprises

**Double-tap and tap-plus-hold keys look missing on 3.35.4**: its layer read stops at
position `0x51` and never reports the second bank; on 3.41.0 the same keys appear <span class="tag measured">MEASURED</span> (owner's board,
2026-09-22).

**A double-tap binding fires only if the key's primary record is a hold-tap.** With a
plain key-press primary the key fires on press and the second bank is never consulted (typing "aa"
instead of "a" then "b"). Use a hold-tap primary with an empty hold. Safety MEDIUM (a keymap write).
TESTED (us, 3.41.0, 2026-09-21) <span class="tag measured">MEASURED</span>. See [Keymap](protocol/keymap.md).

**NayaFlow's "Failed to verify written data"**: second-bank records its profile does not
describe, a tapping term other than 200 (its verify assumes 200 and flavor 1) <span class="tag measured">MEASURED</span>, or a flash right
after `30/10ca` <span class="tag reported">REPORTED</span>. Fixes: [Factory reset](storage/factory-reset.md#failed-to-verify-written-data).

## Modules and battery readings

**Battery percentages are computed on the host.** `fe/1006` is the half's own cell in mV
(take the median of five samples), and `de/100b` the module cell in mV <span class="tag measured">MEASURED</span>. NayaFlow's module
percentage is `(clamp(mV, 3300, 4200) - 3300) * 100 / 900`, truncated, then clamped to 1-100 %, from
the `de/100b` millivolts <span class="tag static">STATIC</span> (NayaCore 6.11.0)[^nc]: 9 mV per
point, 100 % from 4200 mV; it reports 0 (shown as "?") when there is no valid reading, and NayaFlow
shows the keyboard's own cell only in millivolts. nayactl puts both cells on the same 3.3 to 4.2 V
line[^nx-4]. That line reads a full half low on newer firmware: on USB, halves on 3.28.7 held about
4193 and 4207 mV and halves on 3.41.0 about 4068 and 4091 mV, steady over 30 minutes, which the line
shows as 85 and 87 % <span class="tag measured">MEASURED</span> (owner's boards, 2026-09-26). OpenFlow
therefore scales the keyboard's cell so that the voltage its firmware holds reads 100 % (4060 mV from
firmware 3.30 on), and keeps NayaCore's formula for modules. NayaFlow's own notes admit a 5 to 10 %
fluctuation <span class="tag doc">DOC</span>[^beta]. Module firmware 2.1.2 does not implement `de/100b` (about 1.09 s timeout); use
`de/1009`, in 0.1 mV units <span class="tag measured">MEASURED</span>. See [Power and batteries](hardware/power.md).

**Empty dock readings.** With no module docked, the right half answers `de/100b` with
zeros flagged invalid (`00 00 00 01`) while the left reports a phantom 4 192 mV flagged valid
(`00 10 60 00`) <span class="tag reported">REPORTED</span> (raw data checked)[^kb-troubleshooting]. So a
valid-looking battery reading does not prove a module is there: presence comes from the module
handshake and detect commands and from the dock address (`0xF0` means nothing answered), not from the
battery reading <span class="tag measured">MEASURED</span> ([Modules](protocol/modules.md)).

**A Tune two-finger swipe bound to a one-shot action** (play or pause) fires it 11 to 20
times: two-finger swipes stream events as the fingers move, while one- and three-finger gestures send
one event on release <span class="tag measured">MEASURED</span> (owner's board, module 2.3.3, 2026-09-05). See
[Module fields](protocol/module-fields.md).

## Settings and timing

**`fe/100a` is not a "commit".** It is SET ACTIVITY TIMEOUTS (`00` followed by three
32-bit little-endian millisecond values), and NayaFlow sends it on every flash, with `fe/100b` to read
it back. Configuration writes apply live without any commit <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>. Replaying another session's
`fe/100a` writes that session's timeouts, nothing more: NayaFlow's captured frame, sent verbatim seven
times on two boards at 3.41.0 (2026-09-16 to 2026-09-21), wedged nothing <span class="tag measured">MEASURED</span>. This differs from naya-create-kb, which reports that replaying sniffed
`fe/100a` frames wedged its state machine <span class="tag reported">REPORTED</span>[^kb-troubleshooting].
See [Settings and timing](protocol/settings.md).

The keyboard would not enter Bluetooth pairing while on USB power <span class="tag measured">MEASURED</span> (owner's board,
3.41.0, 2026-09-11).

The LED idle timeout did not run with the cable in and USB output selected; on battery the
LEDs went off at the first timeout (90 s) and one tap restored them. Whether the power source or the
output mode gates it is **open** <span class="tag measured">MEASURED</span> <span class="tag open">OPEN</span> (2026-09-11).

**The power switch on USB is a reset.** Switching a half OFF while it is plugged in shuts
it off, and switching it back ON works as a reset: the half reboots and re-links. Use it as a
one-half reset without unplugging <span class="tag measured">MEASURED</span> (owner, 2026-09-23). It agrees with the manual, which says the
Create respects the ON/OFF state even while connected over USB <span class="tag doc">DOC</span>[^man-create]. Safety SAFE. TESTED
(owner, 2026-09-23).

## The vendor's tools

`clear_all_data` sent over NayaFlow's ZMQ bridge fails with an invalid-event answer,
because NayaCore's event list does not contain it <span class="tag static">STATIC</span>[^nc].
`clear_data` is on the list, and it runs NayaCore's ClearAllData operation, which sends `30/10ca`
with params `00 00` <span class="tag static">STATIC</span> ([Factory reset](storage/factory-reset.md#how-the-vendor-software-reaches-it)).

nayactl gates only a handful of commands behind `--force` (three resets, format partition,
erase chip, `mcuboot_reset`, `clear_bonds`); `30/10ca`, the Bluetooth unpair and split-link clears,
MODULE_FWUP and the module recovery commands go out through its `raw` command without it <span class="tag static">STATIC</span>[^nx].

NayaFlow runs its Danger Zone actions (`repair_flash`, `clear_data`, `clear_ble_devices`)
without a confirmation dialog, and Ctrl+D (Cmd+D) in its Hardware Manager starts a firmware update of
both halves without one <span class="tag static">STATIC</span>[^nc-flow].

The vendor's manual FAQ: layers can be set to activate while held, as an absolute
activation or as a toggle, and a power cycle resets active layers; if modules do not respond in
wireless mode, connect by USB and flash an up-to-date keymap; Y-cables are "known to cause issues" for
updates and pairing, so use two direct USB-C cables <span class="tag doc">DOC</span>[^man-create][^man-modules][^nc-flow].

## Acknowledgement bytes and resets

**An ED acknowledgement carries no data.** It is status `00` followed by the checksum, so the
byte after the status is `10` XOR the command's low byte XOR `00`: `03` for `ed/1013`, `18` for
`ed/1008`, `40` for `ed/1050`. It is neither the written value nor a slot id
<span class="tag inferred">INFERRED</span> (from the checksum rule we measure on every frame;
[Command map](protocol/commands.md)).

`ee/10ce` NORMAL_RESET reboots a half through its bootloader: its port drops at once (7.7 ms on
3.35.4, 2026-09-20), the bootloader identity shows for about 1.3 s, and the application is back about
3 s after the command (owner's board, left half, 3.41.0, 2026-09-23) <span class="tag measured">MEASURED</span>. On Windows 11,
restarts after the first two in a row left the half off USB until its cable was replugged
<span class="tag measured">MEASURED</span>. See [Recovery](recovery.md#resets-and-power).

## Vendor-known bugs by firmware

From the vendor's release notes; a board on older firmware still has these
<span class="tag doc">DOC</span>[^cl][^beta]:

| Problem | Fixed in |
|---|---|
| Two hold-tap keys sticking when activated together | 3.28.7 |
| LED colors out of sync between the halves | 3.31.1 |
| Power cycling with a low internal battery and a depleted module | 3.39.4 (beta only; announced as 3.39.3) |
| The right half waking the left at idle; Track not keeping the Create awake; LEDs stuck half on and half off; module updates failing unless the effect is Solid | 3.40.4 (beta only), so 3.41.0 on the stable channel |
| LED colors landing on the wrong keys during rapid updates; Tune phantom ticks when switching layers | 3.41.0 |
| Tune phantom ticks near detents | module 2.3.3 |
| Interrupt Flavor and Tapping Term not applied | NayaCore 6.1.4 |
| A silently failing pairing workflow | NayaCore 6.9.2 |
| A hold-tap flavor mismatch failing a write | NayaCore 6.10.2 |
| Communication breakdown on corrupted data | NayaCore 6.10.3 |
| A dongle crash | NayaCore 6.11.0 |

## The never-send list

This is the site's one list of commands never to send, or to send only with a recipe at hand. Other
pages link here.

!!! danger "Commands that can brick, wedge or wipe"
    Each row names the firmware it was observed on. "All" means the risk follows from what the
    command is, not from a measurement.

| Command or action | Why | Firmware | Evidence |
|---|---|---|---|
| `ee/10be` DFU_RESET | never observed by anyone we know of; the mode it enters and its PIDs are unknown | all | <span class="tag static">STATIC</span> |
| `ee/10ae` MCU_BOOT_RESET | not "never": it is the first step of every firmware update, but the half stays dark in its bootloader until `os reset` on the data port ([Recovery R1](recovery.md#r1-half-dark-and-not-typing-shows-up-as-a-bootloader-device)); only with that recipe at hand | 3.35.4, 3.41.0 | <span class="tag measured">MEASURED</span> |
| `fa/1002` FORMAT_PARTITION, `fa/1006` ERASE_CHIP | destroy stored data, and possibly a staged image | all | <span class="tag static">STATIC</span> |
| `30/10ca` CLEAR_ALL_DATA | formats the data partition: the one reported firing wiped the keymap, the LED maps, the settings and the layer list (3.41.0); only with a complete snapshot ([Factory reset](storage/factory-reset.md)). NayaCore sends it with params `00 00` (frame `aa 00 50 00 30 04 10 ca 00 00 da 04`), also from NayaFlow's "Clear all keymap data" button (`clear_data`), with no confirmation dialog | all | <span class="tag static">STATIC</span> (NayaCore's params, the button) <span class="tag reported">REPORTED</span> (the effect) |
| `be/1004` UNPAIR_ALL | drops every bond, computers included; save the addresses first | 3.35.4 | <span class="tag measured">MEASURED</span> |
| text commands `clear_bonds`, `mcuboot_reset` | the text channel was retired in 3.31.1 and is silent on 3.41.0; the danger applies to 3.30.1 and older | 3.30.1 and older | <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span> |
| a replayed `fe/100a` | writes another session's timeouts (values under 30 s are refused with `ea` on 3.41.0); seven verbatim replays wedged nothing | 3.41.0 | <span class="tag measured">MEASURED</span> |
| short or empty ED payloads | zero-filled writes: brightness 0, ceiling 0, effect 0 | 3.41.0 | <span class="tag measured">MEASURED</span> |
| `ed/1013` with value 0 | the ceiling is stored, so 0 means a board that stays dark across reboots | 3.41.0 | <span class="tag inferred">INFERRED</span> <span class="tag reported">REPORTED</span> |
| a hold-tap flavor of 4 or more | every key stops until the board is unplugged (a power cycle) | 3.41.0 | <span class="tag measured">MEASURED</span> |
| a `&tog 0` binding | strands the board on the upper layer until a power cycle | 3.41.0 | <span class="tag measured">MEASURED</span> |
| any configuration write of three frames | wedges the half until it is unplugged | 3.28.7 only | <span class="tag measured">MEASURED</span> |
| `30/100e` writes of 241 or 41 bytes | the nayactl PR #6 author: they wedged the parser until a power cycle; frames up to 253 bytes were accepted on 3.41.0 | 3.41.0 | <span class="tag reported">REPORTED</span>[^nx-pr6] <span class="tag measured">MEASURED</span> (253 bytes) |
| wireless output with no host, on battery | freezes the board until a power cycle | 3.41.0 | <span class="tag measured">MEASURED</span> |
| a burst of `ed` recovery writes (RESUME `ed/1010` and the RGB override `ed/1050` among them) sent to the right half's own port (`dst 0x51`) | one reported burst of nine such writes left the right half and its docked module dark while it still typed; a single `ed/1013` sent there was answered and parked nothing (owner's board, 3.35.4 and 3.41.0, 2026-09-20 and 2026-09-22); the LEDs of both halves are driven from the left half's stores ([Recovery R7](recovery.md#r7-right-half-dark-after-led-commands-sent-to-it)) | 3.41.0 | <span class="tag reported">REPORTED</span>[^kb-recovery] (the burst) <span class="tag measured">MEASURED</span> (the single write) |
| SMP `image upload` to `image` 0 or 1 | writes the primary slot directly: the first chunk erases the running image, with no swap to fall back on | all | <span class="tag inferred">INFERRED</span> |
| SMP `image state` write | not implemented (rc 8): no test swap, nothing is armed | 3.35.4, 3.41.0 | <span class="tag measured">MEASURED</span> |

## Open questions

- <span class="tag open">OPEN</span> Which stores `30/10ca` spares (split-link pairing, bonds, timeouts, the module bundle), and the bytes NayaFlow's "Clear all keymap data" puts on the wire: a donor-board test ([details](open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> What gates the LED idle timeout: the power source or the output mode.
- <span class="tag open">OPEN</span> What wedged the parser in the nayactl PR #6 author's `30/100e` writes of 241 and 41 bytes, given that single frames up to 253 bytes are accepted on 3.41.0 ([details](open-questions.md#oq-f21)).
- <span class="tag open">OPEN</span> Which firmware versions besides 3.28.7 fail on three-frame writes.

## Sources

[^kb-troubleshooting]: naya-create-kb, [troubleshooting](https://nemezzizz.github.io/naya-create-kb/troubleshooting/).
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (README; `constants.py`).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (Windows serial fixes).
[^nx-4]: nayactl, [issue #4](https://github.com/Qonfused/nayactl/issues/4) (battery readings).
[^nc-flow]: NayaFlow 1.25.1, renderer strings (Danger Zone, Hardware Manager, the Y-cable warning).
[^nc]: NayaFlow 1.25.1: NayaCore 6.11.0 strings, macOS symbols and our disassembly (macOS and Windows builds, 2026-09-23): the flash-test messages, the ZMQ event table, its dispatcher and invalid-event answers, `doClearAllDataOperations` and `_remapClearFlash`, `Naya_Device::getModuleBatteryPercentage`; and the Qt serial-port module in its macOS app bundle. See [Disassembly](software/disassembly.md).
[^man-create]: Naya Create User Manual v1.1.0, pp. 5 and 25; see [Manuals](product/manuals.md).
[^man-modules]: Naya Track and Tune User Manuals v1.1.0, p7; see [Manuals](product/manuals.md).
[^cl]: create-legacy-firmware, [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md) (vendor release notes).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6), description by its author.
[^kb-recovery]: naya-create-kb, [recovery](https://nemezzizz.github.io/naya-create-kb/recovery/).

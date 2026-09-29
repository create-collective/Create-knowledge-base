# Differences by firmware

This page says which wire behavior was measured on which keyboard and module firmware, what the
vendor's release notes say changed in each version, and what halves on different firmware do. The
one thing to know first: read `fe/1002` on **both** halves before following any recipe on this
site, because several behaviors (three-frame writes, the second keymap bank, the Bluetooth status
commands) differ between versions, and a mismatched pair behaves unlike either.

!!! note "At a glance"
    - `fe/1002` replies `00 00 <major> <minor> <patch>`: 3.41.0 is `00 00 03 29 00`, 3.35.4 is
      `00 00 03 23 04`.
    - 3.28.7 wedges on any three-frame write and has no `be/100c` to `be/100f`; 3.41.0 accepts
      both.
    - Three keyboard versions shipped only on the beta channel: 3.39.4, 3.40.0 and 3.40.4.
    - Halves on different firmware still type, but the peripheral's LEDs go dark and its own port
      answers empty payloads.
    - A firmware flash keeps the Bluetooth bonds and the keymap; re-send the LED ceiling afterwards.

A cell that says "not recorded" means nobody we know of measured it. MEASURED means measured on the
owner's boards (a 3.41.0 board and a donor board on 3.28.7) unless a source is named.

## Read the version first

<!--FD-01-->Read `fe/1002` on each half before anything else (params `00`). The reply is
`00 00 <major> <minor> <patch>`: 3.41.0 is `00 00 03 29 00`, 3.35.4 is `00 00 03 23 04`, and 3.30.1
is `00 00 03 1e 01`. The vendor writes the same firmware as `v0.3.29.1` in some notes and `3.29.1`
in others (the NayaFlow 1.14.5 notes say 0.3.28.7, the 1.15.0 notes say 3.29.1), so the reply's
leading `00` is the vendor's leading 0; [Versions](../firmware/versions.md) explains the four-part
form once. <span class="tag measured">MEASURED</span> 3.41.0, 3.35.4 (2026-09-20)
<span class="tag reported">REPORTED</span> (3.30.1)[^nx-pr5] <span class="tag doc">DOC</span>[^nh-cl]

!!! note "Before you follow a recipe"
    Send `aa 00 50 00 fe 03 10 02 00 12 04` on the left half's port and
    `aa 00 51 00 fe 03 10 02 00 12 04` on the right half's port (both read-only). If the two
    versions differ, fix that first (see [below](#halves-on-different-firmware) and
    [Flashing](../firmware/flashing.md)). The module's own version is `de/1008`; the module bundle
    stored on the keyboard is `de/100a` (see [Modules](modules.md)).

## Which versions exist

<!--FD-02-->Keyboard firmware, by the first release that carries the image (the image itself, not
the release note). Beta images carry no readable version, so each beta version is named by its
strongest witness (the same bytes as a known image, NayaCore's version literal, the app's firmware
constant) before the release note.

| Keyboard firmware | Channel | First release carrying it | `fe/1002` reply | Evidence |
|---|---|---|---|---|
| 3.28.7 | stable | NayaFlow 1.14.5 | `00 00 03 1c 07` | <span class="tag static">STATIC</span> (image) <span class="tag inferred">INFERRED</span> (bytes) |
| 3.29.1 | stable | 1.15.0; also betas 1.16.0, 1.16.1 and 1.17.0, which ship the stable 1.15.x images byte for byte although the 1.16.0 note announces 3.31.1 | `00 00 03 1d 01` | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (bytes) |
| 3.30.1 | none | in no public release on either channel (the nayactl maintainer's board; a factory build is the likelier reading) | `00 00 03 1e 01` | <span class="tag reported">REPORTED</span>[^nx-pr5] <span class="tag inferred">INFERRED</span> (origin) |
| 3.31.1 | beta, then stable | beta 1.17.1 (2026-02-11); stable 1.17.2 | `00 00 03 1f 01` | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (bytes) |
| 3.35.4 | beta, then stable | beta 1.18.0 (2026-03-12) through beta 1.21.0; stable 1.19.1 (2026-04-03) | `00 00 03 23 04` | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> 2026-09-20 |
| **3.39.4** | beta only | beta 1.22.0 (2026-05-18); its release note says 3.39.3, but the app's firmware constant and NayaCore's version string both say 3.39.4 | `00 00 03 27 04` | <span class="tag static">STATIC</span> <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> (bytes) |
| **3.40.0** | beta only | beta 1.23.0 (2026-05-21) and 1.23.1 | `00 00 03 28 00` | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (bytes) |
| **3.40.4** | beta only | beta 1.24.0 (2026-06-09) | `00 00 03 28 04` | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (bytes) |
| 3.41.0 | both | 1.25.0 on both channels (2026-07-17); beta 1.25.0 carries generations A and B | `00 00 03 29 00` | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> 2026-09-01 |

Beta 1.10.0 carries no firmware. Every beta image before 1.25.0 is generation A only; all beta
images use the stable signing key hash and the same pre-armed permanent-swap trailer (MCUboot header
version 1.2.3+4). <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^nh-beta][^beta]
The `fe/1002` bytes for versions nobody has read follow the encoding above and are not measured.
Generations, signing and the trailer are explained on [Images](../firmware/images.md).

<!--FD-03-->Module firmware, by the first release that carries the bundle:

| Module firmware | First release carrying it | Notes | Evidence |
|---|---|---|---|
| 2.1.1 | NayaFlow 1.14.3 | | <span class="tag static">STATIC</span> |
| 2.1.2 | 1.14.5 (with keyboard 3.28.7) | measured on our donor board's modules and on a right-docked Touch of the 3.41.0 board | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> |
| 2.2.0 | 1.15.x; also betas 1.16.0 to 1.17.0, although the 1.16.0 note announces 2.3.2 | | <span class="tag static">STATIC</span> <span class="tag doc">DOC</span> |
| 2.2.2 | in no public release on either channel | measured on the nayactl maintainer's modules, with keyboard 3.30.1 | <span class="tag reported">REPORTED</span>[^nx-pr5] |
| 2.3.2 | beta 1.17.1; stable 1.17.2 to 1.21.0; beta 1.22.0 still carries it | | <span class="tag static">STATIC</span> |
| 2.3.3 | beta 1.23.0; stable 1.25.0 | the Tune and Track on the 3.41.0 board | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> |

The version bytes read by `de/1008` and `de/100a` follow the keyboard's scheme: `de/100a` answers
`00 00 02 03 03` for 2.3.3. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16
<span class="tag doc">DOC</span> (the bundle's LittleFS VERSION file)[^nh-beta]

## Minimum firmware per command

<!--FD-22-->NayaCore 6.11.0 checks each board against minimum keyboard firmware versions, per
operation and per command. The values are readable in the binary: inline string variables set at
start-up from literals such as `0.3.30.0` <span class="tag static">STATIC</span>[^nc-gates]. In short:
3.30.0 for REMAP and most operations, 3.32.0 for `be/100c`-`be/100f`, 3.34.0 for `be/1010` and 3.36.0
for `fe/100a` / `fe/100b`. Per command, for the Create halves:

| Commands | Minimum keyboard firmware | Note |
|---|---|---|
| `30/1001`-`30/100e`, `30/10ca` | 3.30.0 | left half only ("Unsupported" on the right) |
| `be/1001`-`be/100b` | 3.30.0 | |
| `be/100c`-`be/100f` | 3.32.0 | BLEStatus; `be/100c` is "Unsupported" on the right half |
| `be/1010` | 3.34.0 | ClearAllSplitLinks |
| `de/1001`-`de/100b` except `de/1004` | 3.30.0 | |
| `ed/1003`-`ed/1011`, `ed/10d1`, `ed/10d2`, `ed/1050` | 3.30.0 | `ed/1012`-`ed/1014` are "Unknown" to the table |
| `ee/10ae`, `ee/10be`, `ee/10ce` | 3.30.0 | |
| `fa/1001`, `fa/1002`, `fa/1006` | 3.30.0 | |
| `fe/1001`-`fe/1009` | 3.30.0 | |
| `fe/100a`, `fe/100b` | 3.36.0 | ActivityTimeouts |
| all `ca/*` and `f1/*` | 3.30.0 | |

Per operation: Keymap, Pair, ClearAllData, TestSPIFlash and UpdateModule need 3.30.0 (copies of the
ProtocolCDC minimum), BLEStatus 3.32.0, and UpdateFW has no minimum (0.0.0); Keymap, ClearAllData and
UpdateModule apply to the left half only. Modules need 2.3.0 for their ProtocolCDC and the dongle
0.1.0.2 (as written) <span class="tag static">STATIC</span>[^nc-gates].

These are the host's gates, not a list of what older firmware can do: 3.28.7 answers REMAP reads
although its gate is 3.30.0, while its missing `be/100c`-`be/100f` fits the 3.32.0 gate
<span class="tag measured">MEASURED</span> 2026-09-19. How NayaCore acts on a board below a gate
(refusal or warning) is <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-f17)). The same tables are on [Versions](../firmware/versions.md#minimum-firmware-nayacore-expects);
how they were read is on [Disassembly](../software/disassembly.md#version-gates).

## Behavior by keyboard firmware

Each cell is tagged; "not recorded" means nobody we know of measured it.

| Behavior | 3.28.7 | 3.30.1 | 3.35.4 | 3.39.4 to 3.40.4 (beta) | 3.41.0 |
|---|---|---|---|---|---|
| <!--FD-04-->CDC interfaces per half | two (right MI_00 + MI_02, left MI_00 + MI_03), one serial, only one answers <span class="tag measured">MEASURED</span> 2026-09-19 | not recorded | not recorded | not recorded | one (MI_00) <span class="tag measured">MEASURED</span> |
| <!--FD-05-->`be/100c` to `be/100f` | no frame at all, both halves <span class="tag measured">MEASURED</span> 2026-09-19 | not recorded | "BLE v2" arrives <span class="tag doc">DOC</span> | not recorded | answered; `be/100f` replies `00 02` <span class="tag measured">MEASURED</span> |
| <!--FD-06-->Three-frame writes | wedge the half until unplugged (three-chunk reads are fine) <span class="tag measured">MEASURED</span> 2026-09-19 | not recorded | not recorded | not recorded | NayaFlow's three-frame writes accepted <span class="tag measured">MEASURED</span> 2026-09-01 |
| <!--FD-07-->Second keymap bank on `30/1003` | not recorded | not recorded | never returned; reads stop at position `51` <span class="tag measured">MEASURED</span> 2026-09-21/22 | not recorded | returned, padded with `07 00` (156 records) on our board even for layers with no second-bank record <span class="tag measured">MEASURED</span> 2026-09-01; 82 records per layer, for layers that apparently never held a second-bank record, in a third-party capture <span class="tag reported">REPORTED</span> (raw data checked)[^kb-raw] |
| <!--FD-08-->LED data between the halves | not recorded | not recorded | differs from 3.41.0: a 3.41.0 left with a 3.35.4 right leaves the right half's LEDs dark <span class="tag measured">MEASURED</span> 2026-09-20/22 | not recorded | see the 3.35.4 cell |
| <!--FD-09-->LED-map read of a layer with no map | status `16` with a header only; the layer renders uniformly white until a map is written <span class="tag measured">MEASURED</span> 2026-09-19 | not recorded | not recorded | not recorded | status `16` in a third-party capture <span class="tag reported">REPORTED</span> (raw data checked)[^kb-raw] |
| <!--FD-10-->Macro opcodes `30/1005` to `1008` | status `11` (not implemented) <span class="tag measured">MEASURED</span> 2026-09-19 | not recorded | not recorded | not recorded | writes acked and nothing kept (2026-09-07); the one captured list read (params `00`) answered status `11` (2026-09-01) <span class="tag measured">MEASURED</span> |
| <!--FD-11-->Text channel (SystemCDC) | untested | answered <span class="tag reported">REPORTED</span>[^nx-pr2] | untested | retired since 3.31.1 <span class="tag doc">DOC</span>[^nh-cl] | zero bytes on both halves <span class="tag measured">MEASURED</span> 2026-09-01 |
| <!--FD-12-->30 s floor on activity timeouts (status `ea` below it) | not recorded | not recorded | not recorded | timeout controls first shipped with 3.39.4; 3.40.4 fixed three timeout bugs <span class="tag doc">DOC</span>[^beta] | measured <span class="tag measured">MEASURED</span> 2026-09-11 |

<!--FD-06b-->NayaCore never sends the macro opcodes (its REMAP switch has no case for them).
<span class="tag static">STATIC</span>[^nc-disasm] On 3.41.0, whether a layer read returns 82 or
156 records seems to follow what is stored (layers written before any second bank existed read
82) rather than the firmware alone. <span class="tag inferred">INFERRED</span> The binding format
itself was identical between 3.35.4 and 3.41.0 (82 records on each of three layers compared,
2026-09-21/22). <span class="tag measured">MEASURED</span> On 3.35.4 the LED map read before the
upgrade and re-read after it differed; the nature of the change was not recorded.

!!! danger "3.28.7: no three-frame writes"
    On 3.28.7 never send a write that needs three frames; the half stops typing and answering until
    it is unplugged. Split writes into two-frame writes of whole records (see
    [Transport](transport.md#chunked-writes)).

<!--FD-13-->The module battery command `de/100b` depends on the MODULE firmware, not the keyboard's:

| Module firmware | `de/100b` (millivolts) | `de/1009` (0.1 mV units) |
|---|---|---|
| 2.1.2 | absent: no data, about 1.09 s of timeout per request | answers |
| 2.2.2 | absent: no reply | answers |
| 2.3.3 | present | answers |

<span class="tag measured">MEASURED</span> (2.1.2 and 2.3.3 on the owner's boards)
<span class="tag reported">REPORTED</span> (2.2.2, the nayactl maintainer)[^nx-issue4] Details on
[Modules](modules.md).

<!--FD-14-->Stable across every version measured: the dock address map (3.28.7, 3.30.1, 3.41.0), the
136-entry LED map (3.28.7, 3.41.0), the frame format and the command ids.
<span class="tag measured">MEASURED</span> <span class="tag reported">REPORTED</span> (3.30.1)[^nx-pr2]

## Halves on different firmware

<!--FD-15-->When the two halves run different keyboard firmware, the peripheral's port goes "hollow"
(it completes the handshake and answers every command with an empty payload), its LEDs go dark, and
typing still works on both halves. The halves report mutually correct pair addresses through a dead
link, and NayaCore's pairing repair refuses with "Devices have different firmware versions".
Matching the firmware restores everything; the central dropped off USB for about 2 s as the halves
re-linked. Measured with a newer left half (3.41.0) and an older right half (3.35.4). The
mismatched peripheral's version stays readable through the central's port at `dst 51`: the left
port read the right half's version (3.35.4) while the right half's own port returned empty
payloads. Relaying is partial: Bluetooth identity reads sent that way answer for the left half (see
[Transport](transport.md#addressing-and-relaying)).
<span class="tag measured">MEASURED</span> 2026-09-20/22[^fp-mismatch] <span class="tag static">STATIC</span>[^nc]
More on [Split link](../connectivity/split-link.md).

!!! warning "Match the firmware first"
    Do not read or write a mismatched peripheral's port as if it were healthy: it answers empty
    payloads. Only newer-central with older-peripheral has been measured; flash the central (left)
    half first and then the right, and check `fe/1002` on both afterwards.

## What a firmware flash keeps

<!--FD-16-->Across a keyboard firmware flash (3.35.4 to 3.41.0 and back, both halves), the Bluetooth
bond tables stayed byte-identical, so pairing survives an update. After the upgrade both halves were
very dim until the LED ceiling `ed/1013` was re-sent with 100; whether the flash changed the stored
ceiling or only the live level was not recorded. The keymap lives in the data partition and is not
part of the firmware image. <span class="tag measured">MEASURED</span> 2026-09-20[^fp-measured][^fp-mismatch]
The flashing procedure itself (upload the whole resource, then reset; no separate mark step) is on
[Flashing](../firmware/flashing.md).

!!! warning "If the board is dim after an update"
    Re-send the LED ceiling before anything else: `ed/1013` params `00 00 64`, whole frame
    `aa 00 50 00 ed 05 10 13 00 00 64 67 04`. This is a write of a persistent setting; it fixed a dim
    board on 2026-09-20/22. See [LEDs](led.md).

## Vendor change notes that touch the wire

<!--FD-17-->Keyboard firmware, first version carrying each change (vendor release notes):

| Version | Changes |
|---|---|
| 3.28.7 | hold-tap keys sticking when two activated together, fixed |
| 3.29.1 | module update method prevents installing the wrong firmware |
| 3.31.1 | SystemCDC retired; LED PWM power control; LED colors out of sync between halves on boot and after sleep, fixed |
| 3.35.4 | BLE v2 (see [Bluetooth](../connectivity/bluetooth.md)); module battery management |
| 3.39.4 (the note says 3.39.3) | firmware-side LED remapping; LED notifications; power cycling on a low internal plus depleted module battery, fixed; reduced Bluetooth traffic between the halves |
| 3.40.0 | per-LED OFF |
| 3.40.4 | activity-timeout fixes; lower low-battery LED threshold; LED remap no longer overwrites LED actions; module update no longer needs the Solid effect |
| 3.41.0 | LED action override setting; colors offset onto the wrong keys during rapid updates, fixed; Tune phantom ticks on a layer switch, fixed |

The stable 1.25.0 note merges the changes of 3.39.4 to 3.41.0 into one list under
"v3.35.4 -> v3.41.0" and names no version in between. <span class="tag doc">DOC</span>[^nh-cl][^beta][^nh-beta]

<!--FD-18-->Module firmware notes: 2.1.2 fixed the Track's Z-scroll being too easy; 2.2.0 added
Force Module Update support and brightness sync for animations; 2.3.2 lowered the Tune's LED power
by about 20 % and made tick counting exact; 2.3.3 fixed Tune phantom ticks near detents and
disabled the battery blink. <span class="tag doc">DOC</span>[^nh-cl][^beta]

<!--FD-19-->NayaCore (host) changes that touch the wire: 5.8.1 made flashing up to 2.5x faster;
6.1.2 retired SystemCDC on the host side (a breaking Flow-to-Core message change); 6.1.4 fixed
Interrupt Flavor and Tapping Term sometimes not being applied; 6.4.0 added BLE v2 support, the SPI
flash test and format, and Clear BLE Devices; 6.9.2 redesigned device detection and fixed a pairing
workflow that could fail silently; 6.10.2 handles a hold-tap flavor mismatch on write; 6.10.3 fixed
modules not following the color map and a communication breakdown on a bit flip; 6.11.0 added
Double Tap and Tap and Hold, the three LED setting commands, generation-B (`_64`) image updates,
consolidated minimum versions, pairing error codes, a post-update BLE version check, ProtocolCDC
command timeouts and a dongle crash fix. <span class="tag doc">DOC</span>[^nh-cl][^beta]

## Which versions are likely in use

<!--FD-20-->Which firmware a reader runs is uncertain: 3.41.0 shipped weeks before the vendor
stopped, a half can silently miss an update (one right half stayed on 3.35.4 while its left got
3.41.0), and the public installer download counts are highest for the releases carrying 3.29.1
and 3.35.4. Downloads are not flashes, and the Windows counts include auto-updates, so this is a
weak reading. <span class="tag doc">DOC</span>[^nf-rel][^beta] <span class="tag inferred">INFERRED</span>
Check `fe/1002` on both halves.

## Safety

- On 3.28.7 never send a write that needs three frames.
- With halves on different firmware, do not treat the peripheral's port as healthy; match the
  firmware first, central first.
- After an update, re-send `ed/1013` 100 before trying anything more drastic for a dim board.

## Open questions

- <span class="tag open">OPEN</span> Every "not recorded" cell above, in particular nearly all
  behavior on 3.35.4, and anything on the beta-only 3.39.4, 3.40.0 and 3.40.4 (images archived in
  create-legacy-firmware; no board on them has been read); which versions besides 3.28.7 fail on three-frame
  writes ([details](../open-questions.md#oq-p24)).
- <span class="tag open">OPEN</span> Which firmware first lacks a USB serial number (tools fall back
  to side and product id) ([details](../open-questions.md#oq-c03)).
- <span class="tag open">OPEN</span> What changed in the LED data exchanged between the halves in
  3.41 ([details](../open-questions.md#oq-p19)).
- <span class="tag open">OPEN</span> Why some 3.41.0 layers read 82 records and others 156
  ([details](../open-questions.md#oq-p11)).

## Sources

[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) and its comments (a board on 3.30.1: text channel, dock addresses).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) and its comments (`fe/1002` on 3.30.1; modules on 2.2.2).
[^nx-issue4]: nayactl, [issue #4](https://github.com/Qonfused/nayactl/issues/4) (module battery readings by module firmware).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): the pairing refusal.
[^nc-disasm]: NayaFlow 1.25.1, NayaCore 6.11.0 (Windows x64), our disassembly (2026-09-23): `ProtocolCDCProcessWorker::_remapStartStep`.
[^nc-gates]: NayaFlow 1.25.1, NayaCore 6.11.0 (macOS arm64, cross-checked on x86_64), our disassembly (2026-09-23): the guarded initializers of the `naya_fw::*_MinVersion` values, `operationMinFWVersion` and `commandMinFWVersion` and their tables; see [Disassembly](../software/disassembly.md#version-gates).
[^nh-cl]: create-legacy-firmware, vendor release notes, [changelogs/](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (NayaFlow 1.14.5 to 1.25.1).
[^nh-beta]: create-legacy-firmware, [`firmware-history-beta/MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/firmware-history-beta/MANIFEST.json) (commit 7b511ca: per beta release, the note's version, the app constant, NayaCore's literals and the carved images), with [`FIRMWARE-HISTORY.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FIRMWARE-HISTORY.md).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (1.10.0 to 1.25.0).
[^nf-rel]: Vendor release pages, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases) and the beta repository (download counts, snapshot 2026-08-28).
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384) (commit cdd897c; flow corrected in 6ef80e2: upload the whole resource, then reset, no mark step).
[^fp-mismatch]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Pairing and firmware mismatch"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L369-L384) (commit cdd897c).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (a USB CDC capture log, keyboard 3.41.0); raw data decoded by us, never copied.

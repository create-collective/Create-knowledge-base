# Tools

One neutral table of the tools and projects that exist for the Naya Create, what each can and
cannot do, where it runs and under which license, followed by the house rules every tool user
should follow. The one thing to know: every tool that writes can damage a keymap or park a half in
its bootloader, and each was measured only on the firmware versions named below.

!!! note "At a glance"
    - Quit NayaFlow completely before running any other tool: one program owns a port at a time.
    - Read `fe/1002` on both halves before any recipe; the halves can run different firmware.
    - [OpenFlow](https://github.com/create-collective/openflow/releases) is the full configurator; nayactl is a read-mostly command line; Create
      Companion maps module gestures per app; create-legacy-firmware archives every release and firmware image.
    - The never-send list lives on [Troubleshooting](../troubleshooting.md); it is not repeated here.

## Golden rules

1. **One owner per port.** Quit NayaFlow completely (the app, flow-bg-server and NayaCore) or release
   OpenFlow's ports before running a script. On Windows a busy port reports "Access is denied"; a
   killed script can leave a Python process holding the port, which looks like a dead keyboard
   <span class="tag measured">MEASURED</span> (owner's machine, Windows, 3.41.0 and 3.28.7,
   2026-09-10 to 09-19).
2. **Wake the halves first.** The first connect can take about 1 s; nayactl retries its opener at
   0.3, 0.7 and 1.0 s <span class="tag static">STATIC</span>[^nx]. The first `fe/1001` on a freshly
   opened port often gets no reply even with both halves awake on USB (23 of 30 nayactl connections),
   so retry it <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01; see
   [Transport](../protocol/transport.md)). How an idle or sleeping half answers is not measured yet.
3. **Check the firmware of both halves.** Read `fe/1002` on each half's own port and through the
   left at `dst 0x51`: halves can run different firmware, and a half can miss a vendor update
   without any warning (a board arrived with left 3.41.0 and right 3.35.4). While they differ, the
   right half's own port answers with empty payloads, but the version read through the left port at
   `dst 0x51` still reaches it <span class="tag measured">MEASURED</span>[^nh-hw].
4. **Read before you write.** Save a read of every store you are about to change; OpenFlow reads
   only until you flash <span class="tag static">STATIC</span>.

## Comparison

| Tool | What it does | Platforms | License | Measured on | Limits |
|---|---|---|---|---|---|
| [OpenFlow](https://github.com/create-collective/openflow/releases) | Configurator and NayaFlow rebuild: keymaps with up to four behaviors per key, LED maps, modules, settings, Bluetooth slots, firmware flashing of the vendor's images, read-only bootloader probe | Windows, macOS (arm64, Intel), Linux | open source | keyboard 3.28.7, 3.35.4, 3.41.0 | recovery operations and pairing repair ship switched off; Linux untested with a keyboard |
| nayactl | Command line: status, module, Bluetooth and LED reads, key-scan listen, raw frames | Linux, macOS, Windows | Apache-2.0 | 3.30.1, 3.41.0 | no REMAP read or write, no flashing (details below) |
| Create Companion | Maps module gestures (sent as F13-F24) to per-app actions on the host | Windows, macOS | MIT | module 2.3.3 | needs one module flash first |
| create-legacy-firmware | Archive of every stable NayaFlow release and the firmware images carved from them; flashing procedure | any | Apache-2.0 (its own files) | 3.35.4 and 3.41.0 (flashes of 2026-09-20) | installers kept out of git |
| createflow-dongle | Open firmware and flasher turning an nRF52840 stick into a Bluetooth-to-USB bridge | macOS, Windows, Ubuntu 24.04 (flasher) | Apache-2.0 | keyboard 3.41 | fixed report map; no configuration over Bluetooth |

Which tool for which job: read the state of a board (nayactl `status`, OpenFlow, the
[Python recipes](recipes-python.md)); change the keymap or LEDs (OpenFlow, NayaFlow); flash firmware
(OpenFlow with the images from create-legacy-firmware, or NayaFlow's bundled image); recover a parked half (see
[Recovery](../recovery.md)); bridge Bluetooth to USB (createflow-dongle); per-app actions for modules
(Create Companion).

## OpenFlow

OpenFlow is an open-source configurator for the Naya Create and an independent rebuild of NayaFlow:
an Electron shell, a React (Vite) renderer and a Python FastAPI backend on a vendored nayactl, over
USB CDC. It keeps NayaFlow's process split and HTTP contract (the same route and SSE names, default
port 3001, the renderer's fallback), so NayaFlow's `user-data.db` imports directly
<span class="tag static">STATIC</span> ([OpenFlow](https://github.com/create-collective/openflow/releases)).

| Fact | Evidence |
|---|---|
| It does keymaps with up to four behaviors per key (called "OneKey"), the full 136-entry LED map, module configs and gestures, timeouts and LED settings, Bluetooth slots, firmware flashing of the vendor's own images, and a read-only bootloader probe; recovery operations and pairing repair ship switched off. | <span class="tag static">STATIC</span> |
| Safety gates: the only writing route `/rpc/flash` needs `{"confirm": "FLASH"}` and an explicit profile; firmware flashing needs `OPENFLOW_ENABLE_FIRMWARE_FLASH=1`, pairing repair `OPENFLOW_ENABLE_PAIRING_REPAIR=1`, recovery operations `OPENFLOW_ENABLE_RECOVERY_OPS=<list>`; a flash holds one lock across every frame so the status poll cannot slip between frames. | <span class="tag static">STATIC</span> |
| It splits every write into at most two frames on record boundaries, which keeps firmware 3.28.7 from wedging. | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (donor board, 3.28.7, 2026-09-19) |
| `/rpc/release-device` and `/rpc/reconnect-device` free and retake the ports without a USB re-enumeration, so NayaFlow or a script can use the keyboard while OpenFlow runs (the NayaFlow side is not yet verified). | <span class="tag measured">MEASURED</span> (donor board, 2026-09-19) <span class="tag static">STATIC</span> |
| Its single-file probe (`naya-probe.py`, pyserial only, read-only) lists Naya PIDs, reads versions and bond tables (and the partner's version through the left half; it does not show Bluetooth reads through that route, because they answer for the half you are plugged into), reads both slots of a half in MCUboot and names them against the firmware catalog's hashes, captures the bootloader console, and writes JSON. It sends no reset, upload or pairing command. | <span class="tag static">STATIC</span> |
| It ships a firmware catalog of 63 images across the 25 stable releases (26 keyboard images, 6 module bundles, 30 `.sfb` files, 1 dial image) with sizes and hashes; the images themselves come from create-legacy-firmware. | <span class="tag static">STATIC</span> |
| Reference data: `app-shortcuts.json` (150 applications, 19 853 chords, merged from ShortcutMapper (MIT) and the Create Companion catalog; every chord checked by OpenFlow's encoder), `shortcut-dictionary.json` (95 entries: 79 captured from a real NayaFlow flash, 13 computed, 3 from the encoder), `action-chords.json` (610), `nayaflow-action-names.json` (860), key geometry as NayaFlow 1.25.1 draws it, NayaCore vocabularies, stock module profiles. | <span class="tag doc">DOC</span> |
| Module-profile exchange format `openflow.module-profile` v1: `moduleType` required (TOUCH, TRACK, TUNE, FLOAT), `bindings` keyed by gesture id, axis pairs written `"<kind> - <minus> - <plus>"`, optional `split` with `-` (left, up, counter-clockwise) and `+` (right, down, clockwise) halves, `variant`; importing always creates a new profile. | <span class="tag doc">DOC</span> |
| It logs every device exchange (category, subcommand, payload prefix, port, time, result) in a 500-entry ring plus daily files kept 14 days; its bug report strips hardware ids, Bluetooth addresses, USB serials and UUIDs by default and shows the payload before sending. | <span class="tag static">STATIC</span> |
| Packages: a Windows NSIS installer and a portable exe, macOS arm64 and Intel (unsigned dmg), a Linux AppImage and deb built on the oldest Ubuntu runner (Ubuntu 22.04, Debian 12, Fedora 36 and newer). Version and download links at release. | <span class="tag static">STATIC</span> |

## nayactl

nayactl is a Python command-line tool by Cory Bennett (Qonfused), Apache-2.0, Python 3.10+, click and
pyserial (pyzmq optional and unused); `main` at `8049c9f` (2026-09-07). Commands: `scan` (the only
one that opens no port), `status`, `module info/battery/status`, `ble address/pairs/status`,
`led on/off/brightness/effect`, `keyscan`, `listen`, `text`, `raw CAT SUBCMD [PAYLOAD]`. It
reverse-engineered the framing, the XOR checksum, the categories and the opcode map independently
(from a NayaFlow 1.19.1-era NayaCore). Five binary commands and two text commands need `--force`
<span class="tag static">STATIC</span>[^nx].

Limits of upstream `main`, as read on 2026-09-22 <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nx][^nx-pr2][^nx-pr6]. In short:

- No REMAP read or write (no continue flag, so `raw` reads stop at the first chunk; no byte-3
  countdown).
- No SMP, so no firmware flashing and no view of a half in its bootloader (the recovery, third-mode
  and generation-B PIDs are unknown to `scan`).
- `led brightness N` and `led effect N` send one byte, which 3.41.0 zero-fills to level 0 / effect 0.
- Its Bluetooth status decode differs from the measured 239-byte layout past the header.
- The destination follows `--side` (default left), so always pass `--side`.
- Text commands only work on firmware older than 3.31.1; the dongle's port does not answer its opener.
- ZMQ discovery is Linux-only and no ZMQ transport exists.
- On 3.28.7 it may open the half's non-answering second CDC interface; a USB re-enumeration mid-read
  crashes `status` (issue #3); `nayactl -v status` crashed on a Windows cp1252 console.

History <span class="tag doc">DOC</span>[^nx]: pull request #2 (merged 2026-09-07: module type from
the dock address, Windows serial fixes `dsrdtr=False` + `write_timeout=2.0`, multi-line text
replies), #5 (merged 2026-09-07: precise module battery is millivolts), #6 (open, another
contributor: `ed/1012`-`1014`, LED map reads), issue #1 (open: detection for NayaCore 6.9.2 and
later), issue #3 (open: crash on disconnect), issue #4 (closed by #5). Pull requests #2 and #5 came
from the OpenFlow author. OpenFlow vendors nayactl at `72a6af2` (the #2 merge) unmodified and
imports only `constants`, `transport`, `discovery`, `protocol`, `util`, `types`; #5's fix sits in
`cli/status.py`, so library users do their own millivolt handling
<span class="tag static">STATIC</span>.

## Create Companion

Create Companion (Rust, Windows and macOS, MIT) flashes a module once so that its gestures send
spare function keys F13-F24 (HID `0x68`-`0x73`), then maps those keys per foreground application on
the host <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^cc].

- Default Tune transport on Windows: dial clockwise / counter-clockwise F24 / F23, one-finger tap
  F22, one-finger swipes left / right / up / down F20 / F19 / F18 / F17 (macOS has no F21-F24 and
  uses F20-F14).
- Modifier namespaces let two modules share keys (a modifier counts if it went down within 100 ms
  before the key); streamed gestures collapse to one action within a 300 ms gap unless "Follow
  swipe" is on; host-side dial acceleration curves; exports `openflow.module-profile` files; a
  catalog of 162 applications, websites and systems with 22 646 shortcuts. v0.1.0 2026-09-06,
  v0.2.0 2026-09-07.
- Its measurements of what a module sends (two-finger Tune swipes stream 11-20 events by motion;
  one- and three-finger gestures fire once on release; modifiers arrive per event) are the public
  source for [Module fields](../protocol/module-fields.md) <span class="tag measured">MEASURED</span>
  (owner's board, module 2.3.3, 2026-09-05). Because the firmware has no macro table, a host engine
  like it is where macros belong <span class="tag inferred">INFERRED</span>.

## create-legacy-firmware

create-legacy-firmware (public) is the archive of all 25 stable NayaFlow releases (`MANIFEST.json` with
GitHub digests, `CHANGELOG.md`, `changelogs/`), the firmware images carved from each release's
NayaCore (`firmware-history/`, OpenFlow's firmware library, described in `FIRMWARE-HISTORY.md`), the
beta channel's record (`firmware-history-beta/MANIFEST.json` for all 16 beta releases, plus the six
keyboard images of 3.39.4, 3.40.0 and 3.40.4, kept apart so no flasher offers them),
`FLASHING-PROCEDURE.md` (including the section measured on hardware on 2026-09-20), and the scripts
`download.py`, `verify.py`, `tools/carve_fw.py`, `tools/extract_history.py`, `tools/flash_map.py`.
The installers stay out of git. License: Apache-2.0, matching OpenFlow, covering the repository's
own documents, manifests and tools, not the vendor firmware images or installers it archives
<span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nh]. Its
`FIRMWARE-HISTORY.md` says the beta regeneration script is not published yet.

## createflow-dongle

createflow-dongle (Apache-2.0, not affiliated with Naya) is open firmware plus an Electron flasher
that turns an nRF52840 USB stick (EBYTE E104-BT5040U or Nordic PCA10059) into a Bluetooth-to-USB
bridge for the Create: it pairs with the keyboard as a Bluetooth central and HID-over-GATT client and
presents the keyboard's own report map over USB. Firmware 0.1.3 (DFU package v18); releases 0.1.1 to
0.1.3 (2026-09-10/11); Zephyr on nRF Connect SDK 3.4, no MCUboot, Nordic's open DFU bootloader; the
flasher is tested on macOS, Windows and Ubuntu 24.04 <span class="tag doc">DOC</span>[^cfd].

- The replacement stick enumerates as VID `0x1915` PID `0x520F` "createflow Dongle": a device with that
  identity is this project, not Naya's dongle. Its limits: a fixed report map and no configuration
  over Bluetooth <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^cfd].
- Its published Bluetooth measurements on 3.41 (the GATT table, the idle `0x1234`/`0x5678` pipe that
  answers no configuration frame, the 212-byte HID report map, encryption level 2 with a Just Works
  central, the stock dongle's behavior) are cited on [Bluetooth](../connectivity/bluetooth.md)
  <span class="tag reported">REPORTED</span> (createflow-dongle's own measurements)[^cfd].

## The vendor's release repositories

`NayaTech/NayaFlow-releases` (25 stable releases) and `NayaTech/NayaFlow-beta-releases` (16) are still
public; they let anyone re-derive the static findings on this site. They are vendor-owned and may
disappear; create-legacy-firmware mirrors the stable channel's assets and records every beta release's firmware
<span class="tag doc">DOC</span>[^rel][^beta][^nh].

## Commands no tool should send casually

The canonical never-send list is on [Troubleshooting](../troubleshooting.md) and the recovery steps on
[Recovery](../recovery.md). For tool authors, two notes:

- `ee/10be` (DFU reset), `fa/1002` (format partition) and `fa/1006` (erase chip) are never-send.
  `ee/10ae` parks a half in its bootloader (no lights, no typing, looks bricked) but is the first step
  of every stock update and is undone by an SMP `os reset` sent to the port that answers SMP (back in
  about 8 s) <span class="tag measured">MEASURED</span>[^nh-hw]. The text commands `clear_bonds` and
  `mcuboot_reset` are answered only by firmware older than 3.31.1 <span class="tag doc">DOC</span>.
  `fe/100a` is SET ACTIVITY TIMEOUTS, and NayaFlow sends it on every flash
  <span class="tag measured">MEASURED</span> (captures, 2026-09-01).
- Hazards to add to any tool's list (each measured): a hold-tap flavor byte of 4 or more (stops every
  key until the board is unplugged, 3.41.0); any write needing three frames on 3.28.7 (the half
  wedges until replugged); `BT_OUT` on battery with no reachable host (the keyboard froze until a
  power cycle, 3.41.0); `&tog 0` from a higher layer; `ed/1013` value 0 (persistent dark keys); a
  one-byte ED payload (zero-filled); nayactl's `raw` sends `30/10ca` and Bluetooth unpair or clear
  without `--force` <span class="tag measured">MEASURED</span> (owner's board 3.41.0, 2026-09-03/11;
  donor board 3.28.7, 2026-09-19) <span class="tag static">STATIC</span>[^nx].

## Open questions

- <span class="tag open">OPEN</span> Whether OpenFlow's "release device" lets NayaFlow open the ports while OpenFlow runs ([details](../open-questions.md#oq-s11)).
- <span class="tag open">OPEN</span> OpenFlow on Linux with a real keyboard and the udev rule ([details](../open-questions.md#oq-s10)).

## Sources

[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (README, `constants.py`, `transport.py`, issues #1, #3, #4), read 2026-09-22.
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) and its comments.
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6).
[^cc]: Create Companion, [github.com/create-collective/create-companion](https://github.com/create-collective/create-companion) (README, `docs/PLAN.md`, `presets/default-config.toml`).
[^nh]: create-legacy-firmware, [github.com/create-collective/create-legacy-firmware](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb) (README, `MANIFEST.json`, `FIRMWARE-HISTORY.md`, `firmware-history-beta/MANIFEST.json`, `FLASHING-PROCEDURE.md`, `LICENSE`).
[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^cfd]: createflow-dongle, [github.com/mediaandmerch/createflow-dongle](https://github.com/mediaandmerch/createflow-dongle) (README, `firmware/VERSION`, `firmware/src/usb_hid.c`, `docs/findings.md`, releases).
[^rel]: [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases).
[^beta]: [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).

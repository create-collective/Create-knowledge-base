# Flashing keyboard firmware

This page describes how a stock keyboard image is written to a half: the way NayaCore does it, and
the way it was measured on real hardware in both directions (upgrade and downgrade), with timings,
the two risk windows, how to verify the result, what a flash keeps, the failure modes, and what has
and has not been tested. Flashing uses the bootloader's SMP serial recovery, not the configuration
protocol. The thing to know first: every stock upload arms a **permanent** swap, so there is no
trial run and no automatic way back.

!!! danger "You can damage a half. Read the safety notes first."
    Everything here was measured on generation-A halves, flashing between 3.35.4 and 3.41.0 in both
    directions, on a Windows host (owner's board, 2026-09-20 to 2026-09-22). Nothing has been
    measured on a generation-B half, on other firmware versions, or with a power loss during a
    flash. Make first attempts on a donor board, not a daily driver. Module firmware is flashed
    differently: see [Module firmware](modules.md).

!!! warning "Correction: no trial boot, no automatic revert"
    naya-create-kb's signing page says a new image boots on trial and that the bootloader reverts
    automatically if it fails or crashes before confirming itself, which would make firmware
    experiments safe on a daily driver. On the Create the upload itself arms a **permanent** swap
    (every stock resource carries a pre-written trailer), and the bootloader refuses the
    `image state` write that could request a test swap (rc 8). A signed image that boots badly stays;
    the way back is another upload through serial recovery <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-trailer][^fp-measured]. See
    [There is no test mode](#there-is-no-test-mode).

!!! note "At a glance"
    - Send `ee/10ae`, find the port that answers SMP, upload the whole 663 552-byte resource to
      `image: 2` in 512-byte chunks, wait out the silent swap, send `os reset`, confirm with `fe/1002`.
    - About 1 to 3.5 minutes of upload per half; about 100 s of silent swap; four to ten minutes for
      both halves.
    - Flash the left (central) half first. Halves on different firmware still type.
    - A flash keeps keymaps, LED maps, layers, module slots and Bluetooth bonds; it resets the live
      lighting.

## What you need

- The stock image that matches the half's **side and flash generation**. The four current images
  and how to tell them apart are on [Images](images.md#flash-generations-a-and-b); all stock images
  are in nayaHistory.
- An SMP (mcumgr) client for the serial port. The framing and its two silent-failure pitfalls are on
  [Bootloader](bootloader.md#smp-over-the-serial-console).
- The vendor's rules for its own updater (NayaFlow 1.25.1): no modules docked on either
  half; both halves switched on; two direct USB-C to USB-C cables (Y-cables "are known to cause
  issues" for updates and pairing); allow up to 3 minutes and wait for the LEDs to come back; update at
  most two halves at a time (connecting "four or more Create halves" may overload it) <span class="tag doc">DOC</span>[^nc-flow].
- Manual v1.1.0: at first setup, connect by USB (3.0) and update the firmware with Naya
  Flow; if that fails, use a standalone USB 3.0 cable and update the halves one by one
  <span class="tag doc">DOC</span>[^man-create].
- One program per port: quit NayaFlow (its NayaCore holds the ports) and any other tool first.

## How it works

Keyboard firmware is flashed over MCUboot serial recovery with the SMP (mcumgr)
`image upload` command. The configuration protocol is used only to send the half into its
bootloader, with `ee/10ae` <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board, six whole-slot writes, 2026-09-20 to 2026-09-22)[^fp-slots].

NayaCore's sequence (NayaCore 6.11.0): enumerate the serial ports; read the USB product id
to derive side and flash generation; pick the matching embedded image, refusing an unknown
generation; open the port; then `MCUBootWorker::doStart` uploads the **whole** resource to
`image: 2` (`uploadImageToCreateSlot`) and resets the half (`restartDevice`, SMP `os reset`). It never
writes `image state` <span class="tag static">STATIC</span>[^fp-current][^fp-trailer].

The upload request's keys are `image`, `off`, `len`, `sha` and `data`; `hash` and
`confirm` (the `image state` write) sit beside them in NayaCore's binary <span class="tag static">STATIC</span>[^fp-slots].

On the device side, MCUboot's `bs_upload` erases the target slot on the first chunk,
writes the bytes verbatim, does not parse `sha`, and accepts a `len` equal to the slot size
<span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot][^fp-trailer].

## The measured sequence

!!! danger "Firmware write: can brick a half"
    Safety level HIGH. TESTED by us on both halves, 3.35.4 to 3.41.0 and back, generation A,
    2026-09-20 (by hand) and 2026-09-22 (from OpenFlow's interface). Untested on generation B and on
    any other firmware. Do not unplug or power off a half at any point between step 5 and step 9.

The sequence as measured <span class="tag measured">MEASURED</span>[^fp-measured]:

| Step | What you send | What the half does | Typical time | What "stuck" looks like |
|---|---|---|---|---|
| 1 | `ee/10ae` MCU_BOOT_RESET, params `00`, on the half's own port (left: `aa 00 50 00 ee 03 10 ae 00 be 04`) | leaves the application; lights go out | immediate | nothing: the half is supposed to go dark |
| 2 | watch USB for the MCUboot PID (`0x006F` left, `0x00D3` right) | re-enumerates with two CDC ports | a few seconds | no bootloader PID: the command did not reach the half |
| 3 | `os echo` on each of the two ports | one port answers (data), the other swallows frames (log) | seconds | neither answers: see [Bootloader](bootloader.md#smp-over-the-serial-console) |
| 4 | `image state` read | reports each slot's hash; name the running image | 4 to 69 s through OpenFlow's retries (right about 25 s, left about 65 s) | a long silence here is normal (cause open) |
| 5 | `image upload`, the whole 663 552-byte resource to `image: 2`, 512-byte chunks | erases the secondary slot on the first chunk, then stores the chunks | 57.6 to 77.7 s by hand; 124 to 207 s in the interface runs | a pause after the first chunk is the erase |
| 6 | (nothing) | the trailer in the last chunk arms a permanent swap | at the last chunk | |
| 7 | wait | MCUboot swaps the slots and decrypts; the port throws or times out, then re-enumerates | about 100 s | silence is the swap; do not unplug |
| 8 | `os reset` (group 0, id 5) on the port that answers SMP; re-send every 30 s | boots the new image | about 8 s once it takes | a dark half: the reset did not take, re-send it |
| 9 | `fe/1002` on the half | reports the new version | | the old version: see [Verifying](#verifying-the-result) |

## Chunking and the upload request

NayaCore sends `min(remaining, 512)` bytes of `data` per request (`uploadImageToSlot`,
x86_64 address `0x100115e95`), so a 663 552-byte resource is 1 296 chunks. 512 bytes is the one chunk
size this bootloader is known to take. The first request carries `len` (the total) and `sha`; later
requests carry `off`. Follow the `off` the device echoes back: trusting a local counter risks a
silently corrupt image after a dropped frame <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-trailer].

## Timings

The first chunk blocks while the bootloader erases the whole 648 KiB secondary slot:
about 6 s (left) and 17 s (right) by hand; in one interface run the first 5 % took 55 s, with one
pause right after the erase. The erase is not finished when the first chunk is acknowledged, so a
chunk shortly after it can block for more than 5 s <span class="tag measured">MEASURED</span>[^fp-measured].

By hand, the whole image took 57.6 s (left) and 77.7 s (right), 8.5 to 11.5 KB/s.
Supervised interface runs took 124 to 207 s including a handful of stalls: the large left image had
11 stalls over 1 s, about 59 s in total; the right had 4, about 17 s. The median and 90th-percentile
chunk time was 40 ms, and the steady rate 12.9 KB/s (each 5 % in 2.6 s). The chunk loop runs at wire
speed <span class="tag measured">MEASURED</span>[^fp-measured].

After the last chunk the bootloader is silent for about 100 s while it carries out the
swap; the port throws an error (on Windows `ClearCommError failed`) or times out, and the half
re-enumerates <span class="tag measured">MEASURED</span>[^fp-measured].

`os reset` returns the half to its application in about 8 s once it takes. Confirming the
new version (reboot plus version report) took about 122 s (left) and 72 to 74 s (right) in supervised
runs, because a reset sent right after an upload often does not take and must be re-sent
<span class="tag measured">MEASURED</span>[^fp-measured].

A whole two-half run, from backup to verdict, took about 10 minutes; supervised runs take
four to ten minutes <span class="tag measured">MEASURED</span> (owner's board, 2026-09-22).

| Phase | Left half | Right half |
|---|---|---|
| First chunk (slot erase), by hand | about 6 s | about 17 s |
| Whole upload, by hand | 57.6 s | 77.7 s |
| Whole upload, interface runs (with stalls; range over all runs) | 124 to 207 s | 124 to 207 s |
| Silent swap after the last chunk | about 100 s | about 100 s |
| `os reset` to the application | about 8 s | about 8 s |
| Version confirmed, interface runs | about 122 s | 72 to 74 s |

## Timeouts that work

These timeouts completed every measured flash; the shorter values each failed a flash that
was in fact perfect <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20 and 2026-09-22; OpenFlow's flasher)[^openflow]:

| Wait | Value | Why | Earlier value that failed |
|---|---|---|---|
| first chunk | 90 s | the slot erase | 5 s (the post-erase stall) |
| later chunks | 20 s | occasional multi-second stalls | |
| after the last chunk | 300 s | the silent swap | 90 s |
| reset re-send | every 30 s, up to 300 s | a reset right after an upload often does not take | |
| both halves re-linked | 90 s | the central reboots when the peer returns | |
| version confirm | (within the above) | | 45 s |

## The two risk windows

1. **During the chunked upload** (about 1 to 3.5 minutes): MCUboot's design leaves the primary
   slot untouched while the secondary is written, so an interruption is expected to leave the half
   as it was <span class="tag inferred">INFERRED</span>[^mcuboot]. Expected, not measured.
2. **During the silent swap after the last chunk** (about 100 s): MCUboot is moving flash sectors.
   This is the one unverified window to treat as a brick risk <span class="tag inferred">INFERRED</span>.

Do not unplug or power off a half in either window. Nobody we know of has tested a power loss in
either one ([open question](../open-questions.md#oq-f07)).

The swap is armed before any host-side check can run (the trailer is inside the uploaded
bytes). What refuses a corrupt or foreign image is MCUboot's own signature check before it swaps.
Verify the running version afterwards either way <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>[^fp-trailer] ([Images](images.md#the-swap-trailer-every-stock-upload-is-permanent)).

## Verifying the result

The swap can complete before the flasher reads back. On both halves the **new** image was
in slot 0 and the image it replaced in slot 1 (left `479e89ba...` over `036059b2...`, right
`2abb2695...` over `959fbae1...`), so a check of slot 1 alone "finds" the old image and calls a
perfect flash corrupt. Recognize completion as: the new hash in slot 0 **and** the previously
running hash in slot 1, when the two differ <span class="tag measured">MEASURED</span>[^fp-measured]. Then read `fe/1002` in the
application.

Nothing about the flash is central-only: the right half's bootloader behaves like the
left's <span class="tag measured">MEASURED</span>[^fp-measured].

## Two halves

Flash one half at a time, the central (left) half first, so the board only passes
through measured states (a newer central with an older peripheral) <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>. Between the two flashes
the unflashed half answers the handshake on its own port and then returns empty payloads, so do not
read it there: read its version through the central's port at `dst 0x51`. When the second half comes
back on matching firmware the halves re-link, and the central reboots through its bootloader (about
2 s off USB, lights out) <span class="tag measured">MEASURED</span>[^fp-measured] ([Bootloader](bootloader.md#passing-through-versus-parked)).

Halves on different firmware still type on both hands (left 3.41.0 with right 3.35.4). A
mismatch breaks two things, and both resolve themselves once the halves match: the peripheral's LEDs
go dark (the LED payload between the halves changed in 3.41), and the peripheral's own USB port
returns empty payloads. The peripheral stays reachable through the central's port at `dst 0x51`
for the version read: the left port read the right half's version 3.35.4 while the right half's own
port returned empty payloads <span class="tag measured">MEASURED</span>[^fp-measured]. Relaying is partial, though: Bluetooth identity reads
sent to `0x51` on the left port answer for the left half ([Transport](../protocol/transport.md)).
OpenFlow never built an automatic retry through that route; the route itself is measured. NayaCore
also refuses its pairing flow with "Devices have different firmware versions": a policy, not a dead
link <span class="tag static">STATIC</span>[^nc-core].

Done on the owner's hardware: halves deliberately put on different firmware and then
matched again <span class="tag measured">MEASURED</span>[^fp-measured].

## Downgrades

Every stock image is signed by the key the bootloader trusts, so a downgrade is an
ordinary flash ([Images](images.md#signing)). Measured: the left half went from 3.41.0 to 3.35.4,
whole resource, 59.8 s upload. Safety HIGH. TESTED (us, 2026-09-20) <span class="tag measured">MEASURED</span>.

Mind the configuration protocol afterwards: on 3.28.7 any configuration write that needs
three CDC frames wedges the half until it is unplugged. That is a limit of the configuration
protocol on that firmware, not of the flash <span class="tag measured">MEASURED</span> (owner's board, 3.28.7, 2026-09-19); see
[Recovery R8](../recovery.md#r8-a-3287-half-stops-answering-after-a-write).

## What a flash keeps

A firmware flash does not touch the data store. Keymap records (both banks), LED maps,
layer identities, module configuration slots and Bluetooth bond tables were byte-identical before
and after two slot erases, writes and swaps per half <span class="tag measured">MEASURED</span>[^fp-measured] (bonds; the rest measured on
the owner's board, 2026-09-20 and 2026-09-22). naya-create-kb also reports that a reflash leaves the
data partition alone.

The keymap record format did not change between 3.35.4 and 3.41.0: 82 records times 3
layers, zero differing positions, and the layer identities were identical after two flashes <span class="tag measured">MEASURED</span>.

Pairing survives a flash. A pairing repair is a remedy for an already broken board, never a
routine step after an update <span class="tag measured">MEASURED</span>[^fp-measured].

What a flash does **not** keep is the live lighting state. A half comes back from the
bootloader white or a darker amber while its stored LED maps are byte-identical. Writing the layer
list back unchanged to the left half (`30/1002` with the bytes just read by `30/1001`) returns both
halves to their stored lighting in one frame. Brightness came back low after the 3.41.0 upgrade;
OpenFlow's restore step re-sends the brightness ceiling (`ed/1013` with the saved value, else 100:
params `00 00 64`). Whether the flash changed the stored ceiling or only the live level was not
recorded. The owner has done this restore on hardware after flashes <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>
([Recovery R5](../recovery.md#r5-lights-wrong-after-a-flash-or-a-bootloader-pass)).

3.35.4 does not report the second binding bank (its layer read stops at position `0x51`);
3.41.0 returns the whole bank, padded with NONE records. A double-tap key at `0x89` was on the board
through an upgrade: invisible before, present after. Cross-version comparisons must treat "absent"
as NONE <span class="tag measured">MEASURED</span> (owner's board, 2026-09-22).

The LED map reads differently across 3.35.4 and 3.41.0 (the payload changed in 3.41), so a
cross-version LED difference is an advisory, not a failed flash <span class="tag measured">MEASURED</span>[^fp-measured].

| Item | After a firmware flash |
|---|---|
| Keymap records, both banks | kept, byte-identical |
| LED maps | kept, byte-identical (reads differ across 3.35.4 and 3.41.0) |
| Layer list and layer identities | kept |
| Module configuration slots | kept |
| Bluetooth bonds and the pairing between the halves | kept |
| Live lighting | not kept: rewrite the layer list |
| Brightness | came back low after the 3.41.0 upgrade; re-send the ceiling |

The same table for every other event (power cycles, resets, the vendor's repair buttons, `30/10ca`)
is on [Flash layout](../storage/flash-layout.md#what-survives-what).

## Failure modes

| Symptom | Cause | What to do |
|---|---|---|
| Stuck at 0 to 5 % | the first chunk waits for the 648 KiB slot erase | wait (90 s timeout) |
| Silent after 100 % | MCUboot is swapping | wait up to 300 s; never unplug |
| Half dark after the flash | still in its bootloader: the reset did not take | re-send `os reset` to the port that answers SMP ([Recovery R1](../recovery.md#r1-half-dark-and-not-typing-shows-up-as-a-bootloader-device)) |
| Slot 1 holds the old image | the swap already happened | check slot 0 for the new hash |
| Halves on different firmware mid-run | expected until the second flash | flash the other half |
| `image state` write refused (rc 8) | not implemented on this bootloader | nothing; do not depend on it |
| Log port says the primary image is not valid | see [Recovery R2](../recovery.md#r2-bootloader-device-only-primary-image-not-valid-untested) | untested |

## There is no test mode

The bootloader answers an `image state` write with rc 8 (not supported). So the route
"upload a bare image, verify it, then arm it through `image state`" cannot work on the Create, and
an image already in the secondary slot cannot be booted by marking it: it must be uploaded again.
NayaCore's `testImage` and `confirmImage` exist in its binary and are never called, for the same
reason <span class="tag measured">MEASURED</span>[^fp-trailer][^fp-measured].

So the advice that firmware trials are safe on a daily driver, because the bootloader
boots new images on trial and reverts automatically, does not hold here <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>
(see the correction at the top of this page).

Never upload to `image` 0 or 1: that writes the **primary** slot directly. The first
chunk erases the whole running image, and with no swap there is no copy to fall back on, so an
interruption, or a decryption the bootloader does not perform, leaves the half with an invalid
primary <span class="tag inferred">INFERRED</span>. MCUboot can be built to decrypt an encrypted image uploaded straight to the primary slot
(`boot_handle_enc_fw`, in upstream since 2023); whether the vendor's build includes that is unknown
<span class="tag doc">DOC</span> <span class="tag open">OPEN</span>[^mcuboot-2024]. Stock images go to `image: 2`, as NayaCore sends them. (A third party's
failed rescue attempts had gone to the primary slot; that report is private and not cited.)

Custom or unsigned firmware cannot be flashed this way: the signature check refuses it
<span class="tag static">STATIC</span> ([Images](images.md#custom-firmware-consequences-only)). naya-create-kb says the same.

## Client notes

Three client pitfalls together cost a 140-fold slowdown (1 h 50 min for an image
NayaCore writes in about 2 minutes): a fixed `read(256)` for a 31-byte reply waited out the full
timeout on every request; a line check that insisted on base64 `=` padding rejected complete
replies; and reopening the port for every request added about 1 s. Reading what is available and
holding one port open per transfer gives 36 ms round trips <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20).

NayaCore tells the data port from the log port with a "data port connection test" whose
content is unknown <span class="tag static">STATIC</span>[^nc-core]. Trying `os echo` on both ports works.

## OpenFlow's flasher

OpenFlow (link at release) implements this procedure.

- Interlocks before any write: the half is in recovery and answers `image state`; the
  running image is in the stock-image table (identified by hash); side and generation agree from
  **both** the USB PID and the running image's table entry; the chosen image is marked flashable;
  the caller passes an arming token equal to the hash the device just reported; a downgrade needs an
  explicit allow. Flashing ships switched off <span class="tag static">STATIC</span>[^openflow].
- It ships only a firmware catalog, fetches a cataloged image on demand (by default
  from nayaHistory) and refuses the bytes unless they hash to the catalog value <span class="tag static">STATIC</span>[^openflow].
- Around the upload: a full backup first; an append-only log flushed per line; the
  central first; the device lock held for the whole run; brightness and lighting restored afterwards;
  a comparison against the backup (bindings, bonds and versions strict; LED and second-bank
  differences across a version change as advisories) <span class="tag static">STATIC</span>[^openflow].

## The stock updater (NayaFlow)

NayaFlow hazards: in its Hardware Manager, Ctrl+D (Cmd+D on macOS) starts `update_create_fw`
on both halves without a confirmation dialog when no warnings are showing. `update_create_fw` with
two empty frames flashes the bundled image, and with a file path flashes that file; NayaCore requires
0 or 2 target devices ("need 0 or 2 HWIDs") <span class="tag static">STATIC</span>[^nc-core][^nc-flow].

NayaCore 5.8.1 (NayaFlow 1.15.0) made keyboard flashing "up to 2.5x faster"; NayaCore
6.11.0 added generation-B ("64-bit") updates <span class="tag doc">DOC</span>[^cl-340][^cl-113].

## Tested and untested

Not yet done by anyone we know of: a generation-B flash; a flash onto a half whose primary
image is invalid ([Recovery R2](../recovery.md#r2-bootloader-device-only-primary-image-not-valid-untested));
a power loss during either risk window; a module-bundle flash ([Module firmware](modules.md)) <span class="tag measured">MEASURED</span>
(absence; status 2026-09-23). Done: both halves in both directions between 3.35.4 and 3.41.0, a
deliberate mismatch and re-match, and the lighting restore afterwards.

## Where this differs from naya-create-kb

| naya-create-kb says | What the evidence shows |
|---|---|
| Serial image upload is unavailable, so stock updates go through the application's CDC protocol (download, secondary slot, reboot, swap) (bootloader and signing pages) | Stock updates go over MCUboot serial recovery with SMP `image upload` to `image: 2`, then `os reset`; the configuration protocol only sends `ee/10ae` |
| New images boot on trial and revert automatically; experiments are safe on a daily driver; a bad build costs one extra reboot (signing page) | Every stock upload is a permanent swap and no test swap can be requested; a bad signed image stays until another upload |

## Open questions

- <span class="tag open">OPEN</span> NayaCore's own upload timing; only our flasher was timed on this bootloader ([details](../open-questions.md#oq-f05)).
- <span class="tag open">OPEN</span> Why identifying the running image takes up to 69 s after entering the bootloader ([details](../open-questions.md#oq-f05)).
- <span class="tag open">OPEN</span> How a generation-B half behaves, including `image slot info` ([details](../open-questions.md#oq-f06)).
- <span class="tag open">OPEN</span> What a power loss does in either window ([details](../open-questions.md#oq-f07)).
- <span class="tag open">OPEN</span> Whether the Create application would confirm a test swap by itself; moot while none can be requested.

## Sources

[^fp-current]: nayaHistory, [`FLASHING-PROCEDURE.md`, "The current procedure (v1.25.1)"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L36-L69).
[^fp-slots]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Slot ids, vendor-exact"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L158-L195).
[^fp-trailer]: nayaHistory, [`FLASHING-PROCEDURE.md`, "The resource is a whole slot, trailer included"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L197-L226) (flow corrected in commit 6ef80e2: upload the whole resource, then reset; no mark step).
[^fp-measured]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384) (commit cdd897c).
[^mcuboot]: MCUboot, [`boot_serial.c`](https://github.com/mcu-tools/mcuboot/blob/main/boot/boot_serial/src/boot_serial.c) (`bs_upload`) and the image encryption design (images are decrypted while being swapped from the secondary slot).
[^mcuboot-2024]: MCUboot at [commit `439930aee115`](https://github.com/mcu-tools/mcuboot/tree/439930aee115e391e064f5ba2a707f2358e5673d) (2024-10-25): `boot/boot_serial/src/boot_serial.c` (a completed upload to the primary slot calls `boot_handle_enc_fw` when image encryption is built in) and `boot_serial_encryption.c`.
[^nc-core]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (pairing refusal, "data port connection test", "need 0 or 2 HWIDs").
[^nc-flow]: NayaFlow 1.25.1, renderer strings (Hardware Manager update texts and the Ctrl/Cmd+D shortcut).
[^man-create]: Naya Create User Manual v1.1.0, p3; see [Manuals](../product/manuals.md).
[^cl-340]: nayaHistory, [`CHANGELOG.md` L340](https://github.com/traviswye/nayaHistory/blob/79eeefb/CHANGELOG.md#L340) (NayaCore 5.8.1).
[^cl-113]: nayaHistory, [`CHANGELOG.md` L113](https://github.com/traviswye/nayaHistory/blob/79eeefb/CHANGELOG.md#L113) (NayaCore 6.11.0).
[^openflow]: OpenFlow (link at release): its flasher and firmware catalog.

# Bootloader

Each Create half boots through MCUboot, and its serial recovery mode over USB is how keyboard
firmware is flashed. This page covers what the bootloader is, how a half gets into it and out of it,
how to talk to it (SMP over the USB serial port), which commands answer, how its slots are addressed,
and how to tell a half that is only passing through it from one that is parked there. The thing to
know first: a half parked in its bootloader has no lights and does not type, so it looks bricked, but
its firmware is untouched, and one SMP `os reset` sent to the right port brings it back.

!!! warning "No trial boot, no automatic revert"
    This bootloader neither boots a stock upload on trial nor reverts one automatically: every stock
    resource carries a pre-written trailer that arms a **permanent** swap, and `image state` writes,
    which could request a test swap, return rc 8 (not supported) <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-trailer][^fp-measured]. See
    [What the bootloader does not offer](#what-the-bootloader-does-not-offer) and
    [Images](images.md#the-swap-trailer-every-stock-upload-is-permanent).

!!! note "At a glance"
    - MCUboot `9ddeffa8169c` on an upstream Zephyr tree; single-image swap using scratch.
    - Every power-on passes through the bootloader for 1 to 1.7 s; `ee/10ae` parks a half there until told to leave.
    - In the bootloader a half is one USB device with two CDC ports: a data port that answers SMP and a log port that does not.
    - Leave with SMP `os reset` (group 0, id 5) on the **data** port; a transport error on that reset means it worked.
    - Build SMP frames as the reference clients do: a version-1 header, a length that includes the CRC, a CRC16 seeded 0; a malformed frame gets no reply at all.

## What it is

The keyboard bootloader is MCUboot. Its banner reads `*** Booting MCUboot 9ddeffa8169c ***`,
and the images are MCUboot images that imgtool reads <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board, left half entering
recovery, 3.41.0, 2026-09-08). The second banner line is
`*** Using Zephyr OS build v3.7.0-5411-g31fea97e05fd ***` <span class="tag measured">MEASURED</span>.

Where that build comes from: Zephyr `31fea97e05fd` is an upstream Zephyr `main` commit
dated 2024-10-25, between v3.7.0 and v4.0.0, not an nRF Connect SDK tag. MCUboot `9ddeffa8169c` is in
none of `mcu-tools/mcuboot`, `nrfconnect/sdk-mcuboot` or `zephyrproject-rtos/mcuboot`, and Zephyr's
manifest at that commit pins a different MCUboot. So this is a vendor-local MCUboot build on an
upstream Zephyr tree <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^zephyr] (commit lookups made 2026-09-23).
The keyboard application it starts is itself a fork of ZMK <span class="tag doc">DOC</span> ([ZMK](zmk.md)).

It is a single-image build: `image slot info` lists only image 0, with two slots <span class="tag measured">MEASURED</span>
(owner's board, left half, 3.41.0, generation A, 2026-09-16)[^fp-slots].

The secondary slot must live on the external QSPI flash: two 648 KiB slots plus the
bootloader do not fit the nRF52840's 1 MB internal flash, and NayaCore's flash self-test reports a
"Slot1 Partition (Secondary Image - RAW)" <span class="tag inferred">INFERRED</span> <span class="tag static">STATIC</span>[^nc] ([Flash layout](../storage/flash-layout.md)).

## The boot banner

The banner line `Primary image: magic=good, swap_type=0x3, copy_done=0x1, image_ok=0x1`
records how the running image arrived. In MCUboot's enumeration, swap type 3 is
`BOOT_SWAP_TYPE_PERM` (NONE 1, TEST 2, PERM 3, REVERT 4): the running image came in by a permanent
swap, which is what the stock trailer produces <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot].

`Scratch: magic=unset` is printed by MCUboot's swap-using-scratch code path, so this build
swaps through a scratch area <span class="tag inferred">INFERRED</span>[^mcuboot].

Our capture of 2026-09-08 (left half entered with `ee/10ae`, 3.41.0) continues with
`Boot source: none`; OpenFlow's console capture of 2026-09-23 (same half and firmware, entered the same
way) shows the lines after it, `Image index: 0, Swap type: none` and `I: Enter the serial recovery mode`
<span class="tag measured">MEASURED</span>. MCUboot of that period prints the first of these inside `boot_go` and the second
when it enters serial recovery on a boot-mode request, in that order <span class="tag doc">DOC</span>[^mcuboot-2024].

## USB identity

Every Naya device uses USB vendor id `0x37D1` <span class="tag measured">MEASURED</span>. NayaCore's
`Naya_Device::setCreateFlashGenerationFromPid` holds the whole product-id table: it masks the PID
with `0xEFFF` and reads bit `0x1000` as the flash generation <span class="tag static">STATIC</span>[^fp-pid]:

| PID (masked) | Half | Mode | Generation-B value | Seen on hardware |
|---|---|---|---|---|
| `0x064` | left | application | `0x1064` | yes |
| `0x06F` | left | MCUboot | `0x106F` | yes |
| `0x07A` | left | third mode | (`0x107A`) | no |
| `0x0C8` | right | application | `0x10C8` | yes |
| `0x0D3` | right | MCUboot | `0x10D3` | yes |
| `0x0DE` | right | third mode | (`0x10DE`) | no |

On the owner's boards we have seen `0x0064`, `0x00C8`, `0x006F` and `0x00D3`, between
2026-09-08 and 2026-09-22 <span class="tag measured">MEASURED</span>. Nobody we know of has seen `0x007A`, `0x00DE` or any generation-B
value. Nothing in NayaCore names the mode behind `0x007A` and `0x00DE`; this site calls it the
"third mode" <span class="tag static">STATIC</span>. The canonical PID table is on [USB](../connectivity/usb.md).

Every Naya device first enumerates at its application PID plus `0x0B` (the MCUboot PID)
and then re-enumerates at its application PID <span class="tag measured">MEASURED</span> (owner's board, halves and dongle, 2026-09-11).
The dongle's short-lived `0x0137` is `0x012C` plus `0x0B`, and NayaCore has a dongle bootloader
client class (`naya_serial::MCUBootWorker_Dongle`), so the dongle runs MCUboot too <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^nc]. The
createflow-dongle author also found MCUboot on the stock dongle, with a vendor key and no serial
recovery window on reset or power-up <span class="tag reported">REPORTED</span>[^cfd].

In MCUboot, each half is one USB device with **two** CDC interfaces: a data port that
answers SMP, and a log port that streams the banner, accepts an open, swallows frames and replies
nothing. The interfaces are not labeled, so a tool must try both <span class="tag measured">MEASURED</span>[^fp-measured].

## Passing through versus parked

Every power-on passes through the bootloader for about 1 to 1.7 s before the application
starts: the right half sat at `0x00D3` for 0.98 s and the left at `0x006F` for 1.40 s (3.41.0,
2026-09-22); 1.6 to 1.7 s per half on 3.28.7 (2026-09-19) <span class="tag measured">MEASURED</span>.

Powering one half on sends **both** through the bootloader: when the peer re-links, the
central (left) half re-enumerates USB for about 2 s, and that is a full reboot through MCUboot (the
left was seen at `0x006F` 2.2 s after the right half's own pass). A one-half power cycle is therefore
a two-half reboot <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-22).

To tell a half passing through from one parked in the bootloader, look twice, at least
3 s apart: a single look at the USB devices cannot tell them apart <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>.

A half sent in with `ee/10ae` does **not** leave by itself. It sat in the bootloader for
well over a minute (2026-09-16) and still answered `image state` minutes later (2026-09-20). There is
no narrow recovery window and nothing needs to race <span class="tag measured">MEASURED</span>[^fp-slots][^fp-measured]. (A note of ours from
2026-09-01 said it recovered by itself after a few seconds; that was wrong.)

A parked half shows no lights and does not type; to a user it looks bricked, but its
primary image is untouched <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20).

!!! note "Is this half parked?"
    1. Look for a USB device at `0x006F` (left) or `0x00D3` (right).
    2. Look again at least 3 s later. Still there: it is parked; gone: it was a boot pass.
    3. Send `os echo` to each of its two serial ports; the one that answers is the data port.
    4. Leave with `os reset` on that port (below). Read-only until step 4.

## Getting in and getting out

**In.** The configuration command RESET/MCU_BOOT `ee/10ae` sends a half into its
bootloader: it re-enumerates at its MCUboot PID with two CDC ports and answers none of the
configuration protocol. This is the first step of every stock firmware update <span class="tag measured">MEASURED</span> (owner's boards,
2026-09-08, 2026-09-16, 2026-09-20). It is a handle-with-care command, not a never-send one
([Troubleshooting](../troubleshooting.md#the-never-send-list)).

!!! warning "Only send `ee/10ae` with the way out at hand"
    Without the exit recipe below, the half stays dark until it is power-cycled, which also works
    only when its primary image is valid. Tested by us on 3.35.4 and 3.41.0.

**Out.** SMP `os reset` (group 0, id 5) sent to the port that answers SMP returns the half
to its application in about 8 s. It schedules nothing. The port drops as the half reboots, so a
transport error on the reset is the reset working <span class="tag measured">MEASURED</span>[^fp-measured].

A reset sent to the log port looks sent and does nothing. Earlier claims that "a power
cycle is required" to leave the bootloader came from exactly that mistake <span class="tag measured">MEASURED</span>[^fp-measured].

Right after an upload, a reset often does not take: re-send it. OpenFlow re-sends it every
30 s for up to 300 s, and one run needed two extra sends. Wait minutes, not seconds <span class="tag measured">MEASURED</span> (owner's
board, 2026-09-20 and 2026-09-22; OpenFlow's flasher).

A power cycle also leaves the bootloader when the primary image is valid <span class="tag measured">MEASURED</span> (owner's
board, 2026-09-20, during the first split-link repair). If the log port says "Image in the primary
slot is not valid", do not rely on it: see [Recovery R2](../recovery.md#r2-bootloader-device-only-primary-image-not-valid-untested).

The configuration protocol has three reset commands: `ee/10ae` MCU_BOOT_RESET, `ee/10be`
DFU_RESET (never observed by anyone we know of) and `ee/10ce` NORMAL_RESET; NayaCore logs them as
"MCU BOOT RESET", "DFU RESET" and "NORMAL RESET" <span class="tag static">STATIC</span>[^nx][^nc]. `ee/10ce` reboots through the
bootloader: after it the left half left USB, showed its MCUboot id `0x006F` from about 0.7 s to about
2 s, and was back at its application id about 3 s after the command <span class="tag measured">MEASURED</span> (owner's board,
3.41.0, Windows 11, OpenFlow's restart probe, 2026-09-23). That is MCUboot's design: it runs on every
reset and starts its console before it boots the image <span class="tag doc">DOC</span>[^mcuboot-2024]. In the same runs only
the first two restarts in a row came back by themselves (4 of 11 over two runs, on different cables
and ports); from the third on, the half reappeared on USB only after the cable was unplugged and
plugged in again <span class="tag measured">MEASURED</span>.

## SMP over the serial console

A request is framed like this: a 2-byte big-endian length (covering the body **and** its
2-byte CRC), the 8-byte SMP header, the CBOR body and a CRC16, all base64-encoded. The first line is
prefixed with the bytes `06 09`, continuation lines with `04 14`, and every line ends with a newline.
NayaCore's binary carries the same `06 09` and `04 14` markers next to `sendFramedCommand`
<span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^fp-slots] (OpenFlow's codec, used live 2026-09-08 to 2026-09-22). Replies come back the same way: MCUboot of this period splits an outgoing
frame into lines of at most 124 base64 characters (127 minus the 2-byte prefix and the newline),
continuing with `04 14` <span class="tag doc">DOC</span>[^mcuboot-2024]. This differs from naya-create-kb, which gives the
continuation prefix as `04 00`[^kb-bootloader].

Header byte 0 carries the operation in bits 0 to 2 and the SMP protocol version in bits 3
and 4 (`(version << 3) + op`). Reference clients send version 1: an image-state read is
`08 00 00 01 00 01 00 00` followed by the CBOR `a0` (an empty map). NayaCore sends version 0 (the same
read as `00 00 00 01 00 01 00 00`), and this bootloader answers both versions <span class="tag measured">MEASURED</span> (our USB
capture of a NayaFlow 1.25.1 module update, left half, 3.41.0, 2026-09-23; OpenFlow's version-1
requests, 2026-09-08 to 2026-09-23). Our first probes, with a version-0 header (`00 00 ...`), got no
reply at all, and switching to version 1 was followed by answers (owner's board, 2026-09-08)
<span class="tag measured">MEASURED</span>. Since version 0 is answered, the version bits were not the cause (MCUboot's 2024
source does not check them either); the same runs also hit a Windows port-open race that kept the data
port untested, which may explain the silence <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot-2024]
([closed question](../open-questions.md#oq-f25)).
Either version works; OpenFlow sends version 1, as the reference clients do.

A length prefix that leaves out the CRC got no reply either <span class="tag measured">MEASURED</span> (2026-09-08).

The CRC16 is XMODEM: polynomial `0x1021`, initial value 0 (check value `0x31C3` for the
ASCII string "123456789"); reply CRCs verify with the same routine <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>. MCUboot seeds its CRC
with 0 and drops a frame whose CRC fails <span class="tag doc">DOC</span>[^mcuboot-2024], so an echo sent with a CRC seeded
`0xFFFF` goes unanswered.

Some Zephyr builds reply with indefinite-length CBOR, so a decoder should accept it <span class="tag static">STATIC</span>.

A worked request, computed with the rules above (MIT):

| Request | SMP header | CBOR | Line sent (after the `06 09` prefix) |
|---|---|---|---|
| `image state` read (group 1, id 0, op 0) | `08 00 00 01 00 01 00 00` | `a0` | `AAsIAAABAAEAAKCvAQ==` |
| `os reset` (group 0, id 5, op 2) | `0a 00 00 01 00 00 00 05` | `a0` | `AAsKAAABAAAABaDgJw==` |
| `os echo` "naya" (group 0, id 0, op 2) | `0a 00 00 08 00 00 00 00` | `a1 61 64 64 6e 61 79 61` | `ABIKAAAIAAAAAKFhZGRuYXlhwAE=` |

```python
import base64, struct

def crc16_xmodem(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def smp_line(op: int, group: int, cmd_id: int, cbor: bytes = b"\xa0", seq: int = 0) -> bytes:
    header = struct.pack(">BBHHBB", (1 << 3) | op, 0, len(cbor), group, seq, cmd_id)  # version 1
    body = header + cbor
    packet = struct.pack(">H", len(body) + 2) + body + struct.pack(">H", crc16_xmodem(body))
    return b"\x06\x09" + base64.b64encode(packet) + b"\n"
```

The baud rate does not matter on USB CDC-ACM: NayaCore opens the port at 1 000 000 baud,
and 115 200 works just as well <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-transport].

## Which commands answer

Measured on 3.35.4 and 3.41.0 <span class="tag measured">MEASURED</span> (owner's boards, 2026-09-01 probe, 2026-09-08,
2026-09-16, and six uploads 2026-09-20 to 2026-09-22):

| Command | Group / id | Result |
|---|---|---|
| `os echo` | 0 / 0 | answers |
| `os reset` | 0 / 5 | answers, then the port drops as the half reboots |
| `image state` read | 1 / 0 | answers with each slot's hash and flags |
| `image upload` | 1 / 1 | answers |
| `image slot info` | 1 / 6 | answers |
| `image state` write | 1 / 0, op 2 | rc 8 (MGMT_ERR_ENOTSUP) |
| file system download | 8 / - | not supported |
| enumeration | 10 / - | not supported |
| os parameters, bootloader info | 0 / - | not supported |

We send echo and reset as op 2 (write) with a version-1 header <span class="tag measured">MEASURED</span>. MCUboot drops any
request whose op is neither 0 (read) nor 2 (write) <span class="tag doc">DOC</span>[^mcuboot-2024], so a request sent as op 1,
which is a read response in mcumgr's numbering, gets no answer <span class="tag inferred">INFERRED</span>. Whether echo and reset
also answer as op 0 has not been tested by us.

Right after entry an `image state` read can take many seconds to answer (see the slow first answers
below), and MCUboot checks both slots (a signature check, and decryption of an encrypted secondary)
before it answers one, so a client that listens for only a second or two sees silence although the
image group is present <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot-2024]. This differs from naya-create-kb, which
concludes from such silence that the image group is compiled out and that stock updates must go
through the application's configuration protocol[^kb-bootloader].

## Slots and upload ids

The slot map read from the device <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-16)[^fp-slots]:

| Image | Slot | Size | `upload_image_id` |
|---|---|---|---|
| 0 | 0 (primary) | 663 552 | 1 |
| 0 | 1 (secondary) | 663 552 | 2 |

This bootloader is built with `MCUBOOT_SERIAL_DIRECT_IMAGE_UPLOAD`, so the `image` field of
an upload is a **slot id**, not an image index: 0 or 1 is the primary slot, 2 the secondary slot, 3
`slot2_partition`, 4 `slot3_partition` (`upload_image_id` = image x 2 + slot + 1) <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^fp-slots].

NayaCore's own constants agree: `MCUBootWorker::uploadImageToCreateSlot(path)` is
`uploadImageToSlot(path, 2)` and `uploadImageToModulesSlot(path)` is `uploadImageToSlot(path, 4)`
(NayaCore 6.11.0, macOS x86_64 `0x100115d50` / `0x10011a140`, arm64 `0x1000f3d14` / `0x1000f7938`)
<span class="tag static">STATIC</span>[^fp-slots].

The modules target (id 4, the left half's 1 MiB `M_Firmware` LittleFS partition) is not an
MCUboot image slot and never appears in `image slot info`. Use id 4 only on a bootloader whose map
numbers the secondary slot 2 <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^fp-slots] ([Module firmware](modules.md)).

!!! danger "Never upload to `image` 0 or 1"
    That writes the primary slot directly: the first chunk erases the running image, and there is
    no swap and no copy to fall back on. Stock keyboard images go to `image: 2` only
    ([Flashing](flashing.md#there-is-no-test-mode)).

## Naming what a half runs

`image state` read returns, per slot, the SHA-256 of the decrypted image plus flags. For
example: slot 0 `479e89ba...` (3.41.0 left, generation A) and slot 1 `036059b2...` (3.35.4 left, the
image the last upgrade replaced) <span class="tag measured">MEASURED</span> (owner's board, 2026-09-08 and 2026-09-16). Match the hash
against the table on [Images](images.md#naming-the-image-a-half-runs) or
[Versions](versions.md#distinct-keyboard-images).

After a swap the secondary slot keeps the previous image, so it records a board's update
history, a "swap footprint" <span class="tag measured">MEASURED</span> (the secondary held 3.35.4, 2026-09-16).

[OpenFlow](https://github.com/create-collective/openflow/releases) ships a read-only field probe, `naya-probe.py` (one file,
pyserial only). It lists Naya PIDs; reads version and bond tables from halves in their application
(and the partner's version through the left half; Bluetooth reads sent that way answer for the left
half, so the probe does not show them); reads both slots of a half in its bootloader and names them
against the stock-image table; captures the console; and writes a JSON report. It sends no reset,
upload or pairing command <span class="tag static">STATIC</span>[^openflow].

nayactl cannot see a half in its bootloader: the MCUboot PIDs are not in its discovery
table, and it has no SMP support <span class="tag static">STATIC</span>[^nx].

## What the bootloader does not offer

There is no flash or file read over USB: nothing in the bootloader (or in the configuration
protocol) dumps firmware <span class="tag measured">MEASURED</span> (the file system and enumeration groups are not supported, 2026-09-01).

`image state` **write** is not implemented (rc 8). There is no test or confirm marking over
serial recovery, and an image already in the secondary slot cannot be booted by marking it: it must be
uploaded again <span class="tag measured">MEASURED</span>[^fp-trailer][^fp-measured] (rc 8 measured 2026-09-20; the flow corrected in create-legacy-firmware
commit 6ef80e2). That fits an MCUboot built without its image-state option
(`MCUBOOT_SERIAL_IMG_GRP_IMAGE_STATE`) <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot-2024]. So there is no trial boot and no
automatic revert.

In MCUboot's serial recovery, an `image state` write without a hash is not "confirm the
running image" (that is the meaning on the application side of mcumgr): `bs_set` calls
`boot_set_pending_multi(0, confirm)`, which would schedule a swap of the secondary slot. It is moot on
this bootloader, which refuses the write <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot][^fp-trailer].

Over Bluetooth the stock keyboard exposes no DFU, SMP or UART GATT service, so on 3.41.0
the bootloader over USB is the only update path. The createflow-dongle author enumerated the services
<span class="tag reported">REPORTED</span>; the conclusion is ours <span class="tag inferred">INFERRED</span>[^cfd].

## NayaCore's side

NayaCore's bootloader client is `naya_serial::MCUBootWorker` (`openSerialDevice`,
`sendFramedCommand`, `parseSMPResponse`, `uploadImageToSlot`, `enterLogPortMode`, `pollLogPort`,
`onSerialReadyRead`). It runs a "data port connection test" (content unknown) to tell the data port
from the log port; it only uploads (it never reads `image state`); `doStart` calls only
`uploadImageToCreateSlot` and then `restartDevice`; `testImage` and `confirmImage` exist in the binary
and are never called. Its source files are `MCUBootWorker`, `_CreateLeft`, `_CreateLeft_Modules` and
`_CreateRight` <span class="tag static">STATIC</span>[^nc][^fp-trailer].

NayaCore's firmware-update state machine runs through OffsetInitialization, Initialize,
SpawnBroker, CheckIfDoneBrokering, Brokering, SpawnSystem, SpawnProtocol, RestartingInMCUBoot,
RestartingInDFU, Restarting, Reconnecting, MCUBoot_Restart, MCUBoot_Connect, MCUBoot_Upload,
Create_PostUpdateVersionCheck and Completed <span class="tag static">STATIC</span>[^nc].

Up to NayaFlow 1.6.10 the SMP upload was done by a bundled Apache mynewt `newtmgr` (a Qt
resource); from 1.11.0 by Naya's in-process SMP client (symbols with an `ERK` suffix, with unsuffixed
names alongside from 1.17.2; the Windows build strips them). The serial rate is 1 000 000 baud in both
eras <span class="tag static">STATIC</span>[^fp-transport].

## Host notes for Windows

Windows can refuse a freshly enumerated bootloader port for a moment ("Access is denied"),
so retry the open. `reset_input_buffer()` fails on these ports ("ClearCommError failed / The device
does not recognize the command"), so drain by reading instead. A second open of the same port within
milliseconds is refused, so use a single discovery path <span class="tag measured">MEASURED</span> (owner's boards, 2026-09-08 and
2026-09-20). More on [Platforms](../tools/platforms.md).

## Slow answers, parking and confirming the exit

**Slow first answers.** After `ee/10ae`, the first SMP answer (identifying the running
image) came 4 to 69 s later across nine runs while OpenFlow re-probed about every 2 s, opening the port
afresh for each request: about 25 s on the right half, about 65 s on the left, with one 3.8 s outlier
(owner's board, 2026-09-20 and 2026-09-22) <span class="tag measured">MEASURED</span>. Holding both of the half's ports open for
the whole visit and reading the console port, as NayaCore does, cut it: the left half named its
running image 19.7 s after entry in each of seven module-bundle updates (3.41.0, 2026-09-23 and
2026-09-24) <span class="tag measured">MEASURED</span>. Why the bootloader answers late at all is **open** <span class="tag open">OPEN</span>.

**Parking.** A valid request that reaches the bootloader during its boot-time wait latches
serial recovery: from then on MCUboot does not leave for the application until a reset, and it does
not restart a timeout <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mcuboot-2024]. That wait is the 1 to 1.7 s pass measured above,
so a tool that sends frames to a booting half can park it; the explicit `ee/10ae` entry never times
out either. Do not flood a booting half with frames.

To confirm the exit, OpenFlow reads `fe/1002` (firmware version) in the application; any
application answer, the read-only SPI-flash self-test `fa/1001` included, shows that the application
is up <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> ([Flash layout](../storage/flash-layout.md#the-spi-flash-self-test)).

## Open questions

- <span class="tag open">OPEN</span> Why some `ee/10ce` restarts in a row come back on USB only after a cable replug ([open question](../open-questions.md#oq-f27)). (That `ee/10ce` passes through the bootloader is answered: [closed question](../open-questions.md#oq-f03).)
- <span class="tag open">OPEN</span> What the third-mode PIDs `0x07A` / `0x0DE` are and what `ee/10be` does; any generation-B PID on real hardware ([details](../open-questions.md#oq-f06)).
- <span class="tag open">OPEN</span> What NayaCore's "data port connection test" sends.
- <span class="tag open">OPEN</span> Why the bootloader takes so long to name the running image after entry: about 20 s on the left half with both ports held open, 4 to 69 s when the port is reopened for each request ([details](../open-questions.md#oq-f05)).
- <span class="tag open">OPEN</span> Whether the dongle's MCUboot (its `0x0137` pass) has a serial-recovery window, and which key it checks ([details](../open-questions.md#oq-f04)).

## Sources

[^zephyr]: Zephyr, [commit `31fea97e05fd`](https://github.com/zephyrproject-rtos/zephyr/commit/31fea97e05fd).
[^mcuboot-2024]: MCUboot at [commit `439930aee115`](https://github.com/mcu-tools/mcuboot/tree/439930aee115e391e064f5ba2a707f2358e5673d) (2024-10-25, the date of the Zephyr build in the banner): `boot/boot_serial/src/boot_serial.c` (`BOOT_SERIAL_FRAME_MTU` 124, CRC seed 0, the op check in `boot_serial_input`, `boot_serial_check_start`), `boot/zephyr/main.c` (console started before `boot_go`; boot-mode serial recovery) and `boot/bootutil/src/bootutil_public.c`. The vendor's build is not in any public tree, so its configuration is inferred.
[^mcuboot]: MCUboot source: [`bootutil_public.c`](https://github.com/mcu-tools/mcuboot/blob/main/boot/bootutil/src/bootutil_public.c) (swap types and swap table), [`boot_serial.c`](https://github.com/mcu-tools/mcuboot/blob/main/boot/boot_serial/src/boot_serial.c) (`bs_set`, `bs_upload`) and the swap-using-scratch code.
[^fp-transport]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Transport to the device"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L82-L95).
[^fp-slots]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Slot ids, vendor-exact"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L158-L195) (device slot map and NayaCore's wrappers; request keys and console markers).
[^fp-trailer]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "The resource is a whole slot, trailer included"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L197-L226).
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384) (commit cdd897c).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings and macOS symbols (`MCUBootWorker`, flash self-test partition names, update state machine, reset names).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py` reset opcodes; `discovery.py` PID table).
[^cfd]: createflow-dongle, [`docs/findings.md`](https://github.com/mediaandmerch/createflow-dongle/blob/main/docs/findings.md) ("The original NAYA-100-1 dongle"; the keyboard's Bluetooth services on 3.41).
[^openflow]: [OpenFlow](https://github.com/create-collective/openflow/releases): `tools/naya-probe.py` and its recovery module.
[^kb-bootloader]: naya-create-kb, [firmware/bootloader](https://nemezzizz.github.io/naya-create-kb/firmware/bootloader/).

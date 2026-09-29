# USB

This page covers what a Naya Create half (and the Speedlink dongle) looks like on USB in every mode:
vendor and product ids, the brief bootloader pass at every power-on, the interfaces each firmware
exposes, which port answers the configuration protocol, the events that re-enumerate a half, and the
host-side behavior that trips up tools. The one thing to know first: a half that shows its bootloader
product id for a second or two is booting normally; only a half that stays there is parked in MCUboot.

Unless another source is named, <span class="tag measured">MEASURED</span> means measured on the
owner's board, with the keyboard firmware and date given beside the tag. Byte strings follow the
[byte convention](../protocol/transport.md#byte-convention). Serial numbers and addresses are never
reproduced.

!!! note "At a glance"
    - Vendor id `0x37D1`; application product ids: left `0x0064`, right `0x00C8`, dongle `0x012C`.
    - Every power-on passes through MCUboot for about 1-2 s (left `0x006F`, right `0x00D3`).
    - On 3.41.0 the left half is CDC + HID and the right half is CDC only; on 3.28.7 each half has two CDC interfaces and only one answers.
    - One program at a time can hold a half's port: quit NayaFlow before running another tool.
    - On USB the half's own power switch (OFF, then ON) resets it.

## Ids at a glance

<!--US-01-->Every Naya USB device uses vendor id `0x37D1`. In application mode the left half is product
id `0x0064` (decimal 100), the right half `0x00C8` (200) and the dongle `0x012C` (300)
<span class="tag measured">MEASURED</span> 3.41.0; dongle 2026-09-11
<span class="tag static">STATIC</span>[^nx].

<!--US-02-->NayaCore 6.11.0 decides what a Create device is from its product id alone
(`Naya_Device::setCreateFlashGenerationFromPid`): it masks the id with `0xEFFF` and accepts exactly
two families of three, and bit `0x1000` marks flash generation B, whose firmware images (`_64`) are
not interchangeable with generation A <span class="tag static">STATIC</span>[^fp-pid]. Only four of
these ids have ever been seen on hardware <span class="tag measured">MEASURED</span>.

| `pid & 0xEFFF` | Half | Mode | Generation B id | Seen on hardware | Evidence |
|---|---|---|---|---|---|
| `0x064` | left | application | `0x1064` | yes (`0x0064`) | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> |
| `0x06F` | left | MCUboot | `0x106F` | yes (`0x006F`) | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> |
| `0x07A` | left | third mode | `0x107A` | never | <span class="tag static">STATIC</span> |
| `0x0C8` | right | application | `0x10C8` | yes (`0x00C8`) | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> |
| `0x0D3` | right | MCUboot | `0x10D3` | yes (`0x00D3`) | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> |
| `0x0DE` | right | third mode | `0x10DE` | never | <span class="tag static">STATIC</span> |
| (outside the table) | dongle | application | none | yes (`0x012C`) | <span class="tag measured">MEASURED</span> 2026-09-11 |
| (outside the table) | dongle | boot pass | none | yes (`0x0137`) | <span class="tag measured">MEASURED</span> 2026-09-11 |

The third mode is unnamed in NayaCore. Nordic's own DFU bootloader would enumerate under Nordic's
vendor id, so calling it "DFU" is only a guess; create-legacy-firmware's product-id table labels `0x07A` /
`0x0DE` "DFU", while this site says "third mode"[^fp-pid]. No generation-B id has ever been seen.
See [Bootloader](../firmware/bootloader.md) for what each mode does.

## The boot pass

<!--US-03-->Every Naya device first enumerates at its application product id plus `0x0B` (left
`0x006F`, right `0x00D3`, dongle `0x0137`) and then re-enumerates at its application id. On the halves
that first identity is MCUboot: each power-on passes through it for about 1 to 1.7 s (donor halves
1.6-1.7 s; on a 3.41.0 board the right half showed `0x00D3` for 0.98 s). Switching only the right half
on also rebooted the untouched left half through MCUboot (`0x006F` for 1.40 s, starting 2.2 s after
the right), because the central reboots when its peer re-links. In a single observation the half's LED
changing from green or red to white marked the re-enumeration
<span class="tag measured">MEASURED</span> 2026-09-10, 2026-09-11, 2026-09-19, 2026-09-22.

<!--US-04-->So a tool should report a half as "in the bootloader" only if it is still at the MCUboot id
a few seconds later (OpenFlow waits 3 s); a one-shot scan can catch a normal boot pass
<span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span> (the waiting
policy is our reasoning from the timings above).

Timeline of a power-on, from the measurements above:

| Event | Left half | Right half | Evidence |
|---|---|---|---|
| Power on (switch or plug) | `0x006F` for about 1-1.7 s, then `0x0064` | `0x00D3` for about 1-1.7 s (0.98 s once), then `0x00C8` | <span class="tag measured">MEASURED</span> 2026-09-10 to 2026-09-22 |
| Only the right half switched on | reboots through `0x006F` (1.40 s), starting about 2.2 s after the right | normal boot pass | <span class="tag measured">MEASURED</span> 2026-09-11 |
| Peer re-links (either half) | the central (left) drops off USB for about 2 s and passes through MCUboot again | | <span class="tag measured">MEASURED</span> 2026-09-22 (see [Split link](split-link.md)) |
| Switch OFF then ON while on USB | the half shuts off, then resets | same | <span class="tag measured">MEASURED</span> 2026-09-23 |

<!--US-30-->**The power switch works on USB.** Switching a half OFF while it is connected over USB shuts
it off, and switching it back ON works as a reset, so on USB the switch alone gives a reset; unplugging
is not needed for one <span class="tag measured">MEASURED</span> owner's board, 2026-09-23. This agrees
with the manual ("Create will respect the ON/OFF state even while connected over USB")
<span class="tag doc">DOC</span>[^man-c]. Whether the half's MCUboot boot
pass was seen on that reset was not recorded
(<span class="tag open">OPEN</span>). A reset does not erase stored settings, so whether a switch reset
clears a stuck LED or settings state is a separate question.

## Interfaces per firmware and mode

<!--US-06-->On 3.41.0 with both halves on USB, the left half exposes `MI_00` CDC plus `MI_02` HID
(keyboard, mouse, consumer), and the right half exposes `MI_00` CDC only, with no HID: the right half's
keys travel over the [split link](split-link.md) and reach the host through the left
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. This matches the Kickstarter campaign's
description of wired mode, in which the halves still link over RF and only the left half sends data
over USB <span class="tag doc">DOC</span>[^ks-camp]. A right half alone on USB was not recorded.

<!--US-07-->On 3.28.7 each half exposes **two** CDC interfaces at once (right `MI_00` + `MI_02`, left
`MI_00` + `MI_03`), both healthy and sharing one USB serial number, and only one of them answers the
protocol: on the donor board the right half answered on `MI_02` and the left on `MI_03`, neither on
`MI_00`, and which one answers is not predictable. 3.41.0 exposes one. A tool must try each interface
of the same serial number and remember which one answered
<span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19.

<!--US-05-->A half sent into MCUboot by `ee/10ae` enumerates at its MCUboot id with **two** CDC ports,
neither labeled: a data port that answers SMP and a log port that accepts the open and silently
swallows frames (a reset sent there does nothing). It stays there (over a minute measured; it does not
time out) until an SMP `os reset` on the data port (back in the application in about 8 s) or a power
cycle (on USB the half's own switch is enough, as above)
<span class="tag measured">MEASURED</span> 3.35.4 and 3.41.0, 2026-09-16, 2026-09-20[^fp-measured].
See [Bootloader](../firmware/bootloader.md).

!!! danger "`ee/10ae` parks a half in MCUboot"
    The half stops typing and lighting until an SMP `os reset` reaches its data port or it is power
    cycled. It is the first step of every stock update, so it is recoverable, but send it only with
    an SMP client ready; `ee/10be` is never to be sent. See the
    [never-send list](../protocol/commands.md#never-send-list).

| Firmware / mode | Left half | Right half | Evidence |
|---|---|---|---|
| 3.41.0, application, both on USB | `MI_00` CDC + `MI_02` HID | `MI_00` CDC, no HID | <span class="tag measured">MEASURED</span> 2026-09-01 |
| 3.35.4, application | not recorded | not recorded | <span class="tag open">OPEN</span> |
| 3.28.7, application | `MI_00` + `MI_03` CDC (one answers) | `MI_00` + `MI_02` CDC (one answers) | <span class="tag measured">MEASURED</span> 2026-09-19 |
| MCUboot (any) | two CDC ports: SMP data port and log port | same | <span class="tag measured">MEASURED</span> 2026-09-16, 2026-09-20 |
| Dongle, application | CDC communication + CDC data (IAD composite) | | <span class="tag measured">MEASURED</span> 2026-09-11 |

<!--US-08-->Descriptors: product strings "Naya Create Left" / "Naya Create Right", interface strings
"Left Keyboard" / "Right Keyboard". The half's USB serial string equals the reply to `fe/1004` and
NayaCore's hardware id (per device, not reproduced) <span class="tag measured">MEASURED</span> 3.41.0.

<!--US-10-->USB endpoints: host frames go OUT on bulk endpoint `0x01` (11-byte frames for commands with
no data); replies come IN on bulk `0x82`, which USBPcap logs one byte per transfer, so a capture must
concatenate the IN stream before it can split frames
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11.

<!--US-22-->Whether the keyboard's own USB HID interface offers the boot protocol is not known; over
Bluetooth the keyboard offers report protocol only (see [Bluetooth](bluetooth.md))
<span class="tag inferred">INFERRED</span> <span class="tag open">OPEN</span>.

## Which port answers what

<!--US-09-->The application CDC port answers the binary protocol (`fe/1001` opens it; see
[Transport](../protocol/transport.md)). On the right half it answers system, Bluetooth and module
reads but no REMAP command, because the right half holds no keymap, LED or module stores. On 3.28.7
only one of the two ports answers. In MCUboot only the data port answers, and only SMP. The text
channel is dead on 3.41.0 <span class="tag measured">MEASURED</span> 3.41.0, 3.28.7.

<!--US-26-->The configuration protocol and the firmware-update protocol (SMP) share the same CDC port;
SMP answers only while the half sits in MCUboot <span class="tag static">STATIC</span>. The
configuration channel stays up when the keyboard's output is switched to Bluetooth with the cable in
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10. So a tool needs the cable, not
USB output mode.

<!--US-24-->NayaCore gives each half's ports roles: Broker, ProtocolCDC (binary), SystemCDC (text),
MCUBootPort1 and MCUBootPort2. It adds a port directly as ProtocolCDC when the firmware version is
known and otherwise brokers it; a ProtocolCDC worker that does not register within 15 s is quit. It
expects exactly two MCUboot ports per half ("duplicate MCUBoot port types", "Log port detected, polling
serial for boot log until data port worker finishes.") <span class="tag static">STATIC</span>[^nc].

<!--US-23-->NayaCore's device types are CreateLeft, CreateRight, Dongle, ModDock, TypeLeft, TypeRight
and TypeOne <span class="tag static">STATIC</span>[^nc]; the last four match later product names
<span class="tag inferred">INFERRED</span>. It keys a device by hardware id and checks it against each
port's USB serial ("HWID mismatch - provided port serial (%1) does not match device HWID (%2)")
<span class="tag static">STATIC</span>[^nc].

<!--US-25-->NayaCore picks the firmware generation from the product id (from NayaFlow 1.25.0) and
refuses to flash bundled firmware when the generation is unknown ("Conflicting Create flash generation
for device %1: observed PID 0x%2 does not match stored generation")
<span class="tag static">STATIC</span>[^nc][^nh-cl].

## Events that re-enumerate a half

<!--US-11-->Docking or undocking a module re-enumerates that half's USB: open handles go stale, and USB
addresses change on every re-enumeration <span class="tag measured">MEASURED</span> 3.41.0. NayaFlow
relaunches itself when a module is re-docked (see [Modules](../protocol/modules.md)).

<!--US-27-->A half sitting in MCUboot neither types nor lights and looks bricked, although its
application image is untouched. Conversely, a half whose USB data link has failed can keep its LEDs lit
from its internal cell and look alive <span class="tag measured">MEASURED</span> 2026-09-20. See
[Recovery](../recovery.md).

Other re-enumerations: every power-on and every peer re-link (the boot pass above), `ee/10ae` (into
MCUboot) and SMP `os reset` (back to the application).

## Identity for tools

<!--US-14-->Key each half by its USB serial string, not by side: two attached Creates are two
legitimate left halves. Join two halves into one keyboard only when the claim is mutual (each half's
`be/1002` pair address equals the other's `be/1008` own address); this works even when the halves run
different firmware and cannot talk, because the pairing record survives while the link is dead
<span class="tag measured">MEASURED</span> two boards attached, 2026-09-20. Some older firmware may
report no USB serial (which one is not recorded); a tool then falls back to side and product id
<span class="tag inferred">INFERRED</span>. A donor board's right half enumerated 1.7 s before its
left, so order halves by side, not by arrival <span class="tag measured">MEASURED</span> 2026-09-20.

## Host notes

<!--US-15-->**One program at a time.** A CDC port can be opened by one program. NayaFlow (its NayaCore
process) holds both ports while it runs, so quit it (or use OpenFlow's release button) before another
tool. On Windows the second opener gets "Access is denied"; a killed script's leftover Python process
can hold the port and look like a dead board <span class="tag measured">MEASURED</span> 3.41.0.

<!--US-16-->**Windows serial settings.** With pyserial `dsrdtr=True`, Windows enables DSR output flow
control; the Create never raises DSR, so the first write blocks forever. Open with `dsrdtr=False` and a
write timeout (fixed upstream in nayactl PR #2[^nx-pr2]). The baud setting is nominal (see
[Transport](../protocol/transport.md)) <span class="tag measured">MEASURED</span> 3.41.0, Windows.
nayactl then asserts DTR and RTS, which is its reading of NayaCore's own port setup
<span class="tag static">STATIC</span>[^nx-serial].

<!--US-17-->**More Windows behavior.** A port whose device detached uncleanly stays listed ("ghost")
and looks live until opened; a half that dropped off USB came back on a new COM number. After a power
cycle a held handle is still "open" but writes fail with "The device does not recognize the command"
(reopen it). The bootloader's CDC does not support comm-state queries, so resetting its input buffer
fails with "ClearCommError failed" (drain by reading instead), and Windows can refuse the bootloader
port for a moment right after it enumerates
<span class="tag measured">MEASURED</span> 2026-09-08, 2026-09-10.

<!--US-12-->In one setup a USB hub gave the halves and the dongle power but no data (nothing
enumerated); captures were then made on a motherboard port. Single observation
<span class="tag measured">MEASURED</span> 2026-09-11.

<!--US-20-->**Captures.** A USB capture of the keyboard includes its HID interface and so records
everything typed during the capture <span class="tag inferred">INFERRED</span>; USBPcap must run from
an already elevated shell <span class="tag measured">MEASURED</span>.

<!--US-18-->**Linux.** Halves appear as `/dev/ttyACM*` owned by `dialout` (`uucp` on Arch) and cannot be
opened by a normal user without a udev rule, and ModemManager probes new CDC ports for seconds after
plug-in <span class="tag reported">REPORTED</span>[^nx]. OpenFlow ships the rule below
<span class="tag static">STATIC</span>[^openflow]. None of this has been measured on a Linux machine
with a keyboard attached: the port ownership is what nayactl's README and OpenFlow's rule header
state, and that the rule fixes both problems is inferred (it was tested in packaging only)
<span class="tag inferred">INFERRED</span>. A read-only check on a Linux host settles it
([open questions](../open-questions.md#oq-s10)).

<!--US-29-->On Linux a half in its recovery bootloader is also a CDC tty, so the same rule covers it
<span class="tag static">STATIC</span>.

```text
# 70-openflow.rules (from OpenFlow)
ACTION!="remove", SUBSYSTEMS=="usb", ATTRS{idVendor}=="37d1", ENV{ID_MM_DEVICE_IGNORE}="1"
ACTION!="remove", SUBSYSTEM=="tty", ATTRS{idVendor}=="37d1", TAG+="uaccess"
```

<!--US-19-->**macOS.** macOS names a USB CDC port `/dev/cu.usbmodem*`, so each half's data port
should be one such node, and a half in MCUboot recovery should add a second, matching the two MCUboot
ports measured on Windows (see the MCUboot interfaces above) <span class="tag inferred">INFERRED</span>
(not checked by us on a Mac; the two ports <span class="tag measured">MEASURED</span> Windows, 2026-09-16).
More per-platform notes are on [Platforms](../tools/platforms.md).

| Symptom | Cause | Fix | Evidence |
|---|---|---|---|
| "Access is denied" / port busy | NayaFlow, another tool or a leftover process holds the port | quit NayaFlow or the other tool; end stray Python processes | <span class="tag measured">MEASURED</span> |
| First write never returns (Windows) | `dsrdtr=True` turns on DSR flow control | open with `dsrdtr=False` and a write timeout | <span class="tag measured">MEASURED</span> |
| Writes fail with "The device does not recognize the command" | handle opened before a power cycle or a module dock | reopen the port | <span class="tag measured">MEASURED</span> |
| "ClearCommError failed" on a bootloader port | MCUboot's CDC lacks comm-state queries | drain by reading | <span class="tag measured">MEASURED</span> |
| A half seems gone, then returns on a new COM number | unclean detach left a ghost entry | rescan ports | <span class="tag measured">MEASURED</span> |
| Two ports per half, one silent (3.28.7) | two CDC interfaces, one answers | try each interface of the same serial | <span class="tag measured">MEASURED</span> 3.28.7 |
| A half sits at `0x006F` / `0x00D3` | parked in MCUboot (normal if it lasts only 1-2 s) | SMP `os reset` on the data port, or the switch | <span class="tag measured">MEASURED</span> |
| Permission denied on `/dev/ttyACM*` (Linux) | `dialout` / `uucp` ownership | udev rule above | <span class="tag reported">REPORTED</span> (nayactl README[^nx]); rule <span class="tag static">STATIC</span>[^openflow] |
| Nothing enumerates through a hub | hub gave power only (one setup) | use a motherboard port | <span class="tag measured">MEASURED</span> once |

## Cabling guidance from the vendor

<!--US-28-->The manual (v1.1.x) says to use a USB 3.0 port and the long end of the Y-cable, 5 V / 1 A
(v1.0.6 said "USB 2.0 or newer"), and to update the halves one at a time on a standalone cable
<span class="tag doc">DOC</span>[^man-c][^um106]. NayaFlow 1.25.1 asks for two direct USB-C to USB-C
cables for updates and pairing ("Y-cables known to cause issues"), refuses to work with four or more
halves connected, and targets "0 or 2 HWIDs" <span class="tag static">STATIC</span>[^nf]. The manual
adds that the keyboard respects its ON/OFF switch even while on USB (see the boot pass section)
<span class="tag doc">DOC</span>[^man-c].

## The dongle and community hardware on USB

<!--US-13-->The Speedlink dongle enumerates with vendor id `0x37D1`, product id `0x012C` (`0x0137`
during its boot pass), device class `EF/02/01` (interface association, composite) with only a CDC
communication (`02`) and a CDC data (`0a`) interface and no DFU class, product string "Dongle", and
`bcdDevice 0x0307` <span class="tag measured">MEASURED</span> 2026-09-11. The halves' bootloader
identities report the same `0x0307` (their applications `0x0300`), so the value most likely reflects
the USB stack's default (Zephyr 3.7), not a dongle firmware version
<span class="tag inferred">INFERRED</span>. It becomes a serial port but does not answer the halves'
opener (`fe/1001` and `fe/1002` at `dst 0x50`, three tries each), alone or with both halves on USB;
instead the port streams ASCII dots (`2e`: a burst of about 1 040 when the port opens, then three
every 200 ms) <span class="tag measured">MEASURED</span> 2026-09-11. No NayaFlow release we archive carries a dongle
image: 1.21.0 bundles only the two keyboard images and the module bundle, and 1.25.1 the four keyboard
images (generations A and B) and the module bundle <span class="tag static">STATIC</span>[^nh-fw]. The
createflow-dongle project reports the same frame protocol with no known address answering, an MCUboot
bootloader with a vendor key and no serial-recovery window, and the same absence of a dongle image
<span class="tag reported">REPORTED</span>[^cfd]. That the dongle runs MCUboot is ours too: its
transient `0x0137` identity has a configuration descriptor byte-identical to the halves' MCUboot
identities <span class="tag measured">MEASURED</span> 2026-09-11, and NayaCore has a dongle bootloader
worker <span class="tag static">STATIC</span>; the vendor key and the missing recovery window are untested
by us ([open questions](../open-questions.md#oq-f04)). The plug is USB-A: Kickstarter update 15 moved it from
a planned USB-C receiver <span class="tag doc">DOC</span>[^ks-15]. Its radio side is on
[Bluetooth](bluetooth.md): the dongle's SAR report describes the radio only as "2.4G SRD" at 2 Mbps.
Hardware details are on [Speedlink dongle](../hardware/dongle.md).

<!--US-21-->A device with vendor id `0x1915`, product id `0x520F` ("createflow Dongle") is the community
createflow-dongle replacement stick (an nRF52840 USB stick acting as a Bluetooth-to-USB bridge for the
Create), not Naya hardware <span class="tag reported">REPORTED</span> (source checked)[^cfd].

## Safety notes

!!! warning "Before you run a tool on a half"
    - Do not unplug a half while a tool is writing to it, and do not run two tools on one port.
    - A half at an MCUboot id for more than a few seconds is parked, not broken: it needs an SMP
      `os reset` on its data port (see [Bootloader](../firmware/bootloader.md)); a reset sent to the
      log port does nothing.
    - To reset a half on USB, its own switch (OFF, then ON) is enough; a recipe does not need
      "unplug, undock and switch" for a plain reset.
    - On 3.28.7, if a write wedges a half (see [Differences by firmware](../protocol/firmware-differences.md)),
      unplug and replug it.

## Open questions

- <span class="tag open">OPEN</span> The third-mode ids `0x07A` / `0x0DE` and every generation-B id have never been seen ([details](../open-questions.md#oq-c01)).
- <span class="tag open">OPEN</span> Interfaces of a right half alone on USB, and interfaces on 3.35.4 ([details](../open-questions.md#oq-c02)).
- <span class="tag open">OPEN</span> Which firmware first lacks a USB serial number ([details](../open-questions.md#oq-c03)).
- <span class="tag open">OPEN</span> What the dongle's CDC port answers, if anything, and whether only while bridging ([details](../open-questions.md#oq-c04)).
- <span class="tag open">OPEN</span> Whether the dongle's MCUboot (its boot identity `0x0137`) has a serial-recovery window ([details](../open-questions.md#oq-f04)).
- <span class="tag open">OPEN</span> USB boot-protocol support of the keyboard's HID interface ([details](../open-questions.md#oq-c05)).
- <span class="tag open">OPEN</span> Whether a power-switch reset on USB shows the MCUboot boot pass ([details](../open-questions.md#oq-c16)).
- <span class="tag open">OPEN</span> Linux behavior with a keyboard attached: nothing has been measured on a Linux machine ([details](../open-questions.md#oq-s10)).

## Sources

[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py` vendor and product ids; README, Linux permissions).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (Windows serial fixes).
[^fp-pid]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Product ids, vendor-exact"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L228-L248) (NayaCore's `setCreateFlashGenerationFromPid`; its table labels the third mode "DFU").
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384) (commit cdd897c: two MCUboot ports, `os reset` to the data port, no narrow recovery window).
[^nh-fw]: create-legacy-firmware, [`firmware-history/`](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/firmware-history) (v1.21.0 and v1.25.1 image sets).
[^nh-cl]: create-legacy-firmware, vendor release notes, [`changelogs/`](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (v1.25.0).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading).
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings (static reading).
[^openflow]: [OpenFlow](https://github.com/create-collective/openflow/releases): its udev rule `70-openflow.rules` and port handling.
[^cfd]: createflow-dongle, [`docs/findings.md`](https://github.com/mediaandmerch/createflow-dongle/blob/main/docs/findings.md) and its firmware README (third party, Apache-2.0).
[^ks-camp]: Kickstarter campaign page, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023), "Connectivity".
[^ks-15]: Kickstarter update 15, [2024-09-03](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4095301).
[^man-c]: Naya Create User Manual v1.1.x ("Turning Create ON/OFF", cabling); see [Manuals](../product/manuals.md).
[^um106]: Naya Create User Manual v1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits ([fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR)).
[^nx-serial]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`transport.py`: opens with `dsrdtr=False`, then asserts DTR and RTS; `docs/cdc-wire-format.md`: NayaCore's serial configuration, DTR and RTS enabled).

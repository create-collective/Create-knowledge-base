# Platforms

The operating-system behavior that trips up anyone scripting the Create: port names and
exclusivity, dead and ghost ports, the boot pass through the bootloader, bootloader-port quirks,
USB capture, Linux permissions and browsers. The one thing to know: our hardware work ran on
Windows 11 (keyboard firmware 3.28.7, 3.35.4 and 3.41.0); macOS rows come from the community KB and
the vendor, and Linux rows from nayactl, createflow-dongle and OpenFlow's packaging. Nobody in this
research has used a Create on Linux or macOS with our own tools.

!!! note "At a glance"
    - One program owns a port at a time on every OS; quit NayaFlow before scripting.
    - Every power-on passes through the bootloader for 1-1.7 s: scan twice before calling a half "in recovery".
    - On Windows use pyserial with `dsrdtr=False` and a write timeout.
    - A USB capture records everything typed; never publish a raw capture.

## What the keyboard looks like to a host

| Fact | Evidence |
|---|---|
| On firmware 3.41.0 each half shows one CDC serial interface (MI_00); the left half also shows an HID interface (MI_02); the right half shows no HID while both halves are on USB (its keys travel over the split link). | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, Windows, 2026-09-01) |
| On firmware 3.28.7 each half shows two CDC interfaces with the same USB serial (right MI_00 + MI_02, left MI_00 + MI_03); both look healthy but only one answers, and which one is not predictable (donor board: right MI_02, left MI_03). Group ports by USB serial and try the siblings. | <span class="tag measured">MEASURED</span> (donor board, 3.28.7, Windows, 2026-09-19) |
| Every power-on passes through the bootloader for about 1-1.7 s (right at PID `0x00D3` for 0.98 s, left at `0x006F` for 1.40 s on 3.41.0; 1.6-1.7 s on 3.28.7), so a single scan can report a half "in recovery" that is only booting: look twice. When one half powers on and re-links, the central re-enumerates for about 2 s (a reboot through the bootloader). | <span class="tag measured">MEASURED</span> (owner's board 3.41.0, donor board 3.28.7, 2026-09-22) |
| Docking or undocking a module re-enumerates that half's USB; open handles go stale and USB device addresses change on every re-enumeration. NayaFlow relaunches itself when a module is docked again. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0) |

VID, PIDs and interfaces are on [USB](../connectivity/usb.md).

## Windows

| Symptom | Cause and fix | Evidence |
|---|---|---|
| "Access is denied" (error 5) when opening a COM port | Another program holds it: NayaFlow's NayaCore, OpenFlow's backend, or a Python process left by a killed script. Quit it; check Task Manager for stray `python.exe`. | <span class="tag measured">MEASURED</span> (owner's machine) |
| The first write blocks forever | pyserial's DSR flow control: the keyboard never asserts DSR. Open with `dsrdtr=False` and a `write_timeout`. | <span class="tag measured">MEASURED</span> (owner's machine, 3.41.0); nayactl pull request #2[^nx-pr2] |
| "WriteFile failed (PermissionError(13, 'The device does not recognize the command.'))" | A dead handle after a power cycle with the port still open. Close and reopen. | <span class="tag measured">MEASURED</span> (owner's machine, 2026-09-10) |
| A COM port that looks live but never answers | A "ghost" port after an unclean detach: the half came back on a new COM number while the old one stayed listed, even after an app restart. | <span class="tag measured">MEASURED</span> (owner's machine, 2026-09-18) |
| Bootloader port: `reset_input_buffer()` fails with "ClearCommError failed / The device does not recognize the command" | Drain by reading instead. The port can be refused for a moment right after it enumerates, and a second open milliseconds after the first is refused: use one discovery path and retry (OpenFlow tries 4 times 0.35 s apart). After the last upload chunk the port throws `ClearCommError` or times out for tens of seconds while the bootloader acts on the trailer, then re-enumerates. | <span class="tag measured">MEASURED</span> (owner's machine, 2026-09-20); nayaHistory[^nh-hw] |
| A tool is slow against the bootloader | Read what is available instead of waiting for a fixed length: a client that read 256 bytes for a 31-byte reply waited out its whole timeout on every request, rejected complete replies for missing base64 `=` padding, and reopened the port per request (first exchange: a timeout, then 0.974 s, then 0.078 s warm). Fixed, a round trip took 36 ms and a 648 KiB upload about 2 minutes instead of 1 h 50 min. | <span class="tag measured">MEASURED</span> (owner's machine, 3.35.4/3.41.0, 2026-09-20) |
| LEDs and layer switching work, nothing types, no `VID_37D1` device appears | A failing cable or Y-cable leg: Device Manager shows "Unknown USB Device (Device Descriptor Request Failed)", code 43, VID/PID `0000:0002`; two failed devices under one hub at the same instant means both legs of a Y-cable failed together. Reseat at the host end, try one plain USB-C cable to the left half, use a port on the machine itself. | <span class="tag measured">MEASURED</span> (first-hand diagnosis on Windows, 2026-09-08) |
| Charging and updates fail through a hub or a Y-cable | The vendor asks for USB 3.0 ports ("5V-1A" for charging) and two direct USB-C to USB-C cables; Y-cables "are known to cause issues" for firmware updates and pairing. | <span class="tag doc">DOC</span> (Create manual v1.1.x p.4 and p.25[^manual]; NayaFlow 1.25.1 update dialog[^bg]) |

- NayaFlow keeps its data in `%APPDATA%\NayaFlow\`; its background server's port changes at every
  launch and is found through that process's listening socket
  <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (details on
  [App data](../software/app-data.md) and [NayaFlow and NayaCore](../software/nayaflow.md)).
- **USBPcap**: start it from an already elevated PowerShell (it elevates itself, so `-Verb RunAs`
  breaks it); hub numbering moves between sessions; the IN endpoint (`0x82`) is logged one byte per
  transfer, so concatenate before decoding; a capture includes the HID interface and so records
  everything typed. In one setup a USB hub or dock gave the halves and the dongle power but no data:
  capture on a motherboard port <span class="tag measured">MEASURED</span>
  <span class="tag inferred">INFERRED</span> (owner's machine, 2026-09-11).
- **nayactl on Windows**: the `nayactl.cmd` launcher tries `.venv\Scripts\python.exe`, then `py -3`,
  then `python`, each with `-B -m nayactl`, and works only once the package is installed in that
  interpreter; `nayactl -v status` crashed on a cp1252 console (an arrow character); always pass
  `--side` <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nx].

!!! warning "Captures record keystrokes"
    Stop typing passwords while capturing, and never publish a raw capture: it also carries USB
    serial numbers and Bluetooth addresses.

## macOS

| Fact | Evidence |
|---|---|
| The halves appear as `/dev/cu.usbmodem*`: `1101`-style names for the left and `21101`-style for the right, an extra node (for example `1103` beside `1101`) while a half is in its bootloader, and "Resource busy" when NayaFlow or its background server holds the port. | <span class="tag reported">REPORTED</span> by naya-create-kb[^kb-recovery][^kb-python]; not checked by us on a Mac |
| NayaFlow's data folder is `~/Library/Application Support/NayaFlow/`; NayaCore sits inside `NayaFlow.app/Contents/core/NayaCore.app/`. | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (the release zip's layout; the app name `NayaFlow` and Electron's `userData` convention); also reported by naya-create-kb[^kb-appdata] |
| Instrumenting NayaCore with `DYLD_INSERT_LIBRARIES` needs a re-signed copy: NayaCore is signed with the hardened runtime (CodeDirectory flag `0x10000`), and its entitlements (`allow-jit`, `allow-unsigned-executable-memory`, `disable-library-validation`) do not allow DYLD environment variables. | <span class="tag static">STATIC</span>[^nc-mac]; also reported by naya-create-kb[^kb-toolkit] |
| macOS has no F21-F24 key codes, so function-key schemes (Create Companion) use F14-F20 there. | <span class="tag doc">DOC</span>[^cc] |
| Apple platforms hold non-Apple Bluetooth devices to a 15 ms minimum connection interval (the vendor's BLE v2 reaches 7.5 ms elsewhere). | <span class="tag doc">DOC</span> (NayaFlow 1.19.1 release notes[^rel]) |
| Vendor-noted macOS issues: Cmd+Return created an empty window on macOS Tahoe 26.2 (disabled in 1.17.2); diagnostics failed on macOS 26 (fixed in 1.25.0); arm64 Macs auto-updated to the Intel build (fixed in beta 1.17.2). | <span class="tag doc">DOC</span> (release notes[^rel][^beta]) |

## Linux

| Fact | Evidence |
|---|---|
| Each half is a `/dev/ttyACM*` port owned by root and group `dialout` (`uucp` on Arch), and so is a half in its bootloader; nayactl's README runs as root or asks for the `dialout` group, and calls Linux its most exercised platform. | <span class="tag static">STATIC</span> (OpenFlow's udev rule and README) <span class="tag reported">REPORTED</span> (nayactl README[^nx]); not measured by us |
| On Linux EACCES/EPERM on open means missing permission, not a busy port. | <span class="tag static">STATIC</span> (OpenFlow, a code note); not measured on a Linux machine with a keyboard attached |
| ModemManager probes new CDC serial ports for several seconds after plug-in and collides with the keyboard's protocol; the udev rule below tells it to ignore the keyboard. | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (OpenFlow's rule and README); tested in packaging only |
| OpenFlow's Linux builds: the AppImage needs libfuse2 (`libfuse2t64` on Ubuntu 24.04, `libfuse2` on 22.04) or `--appimage-extract-and-run`; on Ubuntu 24.04 and later AppArmor blocks Electron's sandbox and the .deb installs an AppArmor profile; the builds target the glibc of Ubuntu 22.04, Debian 12, Fedora 36 and newer. | <span class="tag static">STATIC</span> (OpenFlow README, link at release) |
| What Naya shipped for Linux: an AppImage only for 0.0.1 to 0.1.1 (without a firmware service), and Linux NayaCore builds inside 1.15.0 to 1.17.3 ("Ubuntu 20.04+", X11 libraries) that embed older keyboard images (3.28.7) than Windows and macOS; the BLE v2 notes list Debian Linux among tested hosts. | <span class="tag static">STATIC</span> <span class="tag doc">DOC</span> (installers; 1.17.3 Linux README; 1.19.1 notes[^rel]); see [History](../software/history.md) |
| nayactl's NayaCore (ZMQ) discovery is Linux-only: it looks for the shared-memory port in `/dev/shm/qipc_sharedmemory_*<key>*`, `/tmp/<key>`, `/tmp/qipc_sharedmemory_*<key>*` and checks `/proc/*/cmdline`; there is no ZMQ transport. | <span class="tag static">STATIC</span>[^nx] |
| createflow-dongle's flasher is tested on macOS, Windows and Ubuntu 24.04; its dongle on macOS and Ubuntu 26.04. | <span class="tag doc">DOC</span>[^cfd-rel] |

OpenFlow's udev rule (file `/etc/udev/rules.d/70-openflow.rules` for the AppImage, installed under
`/usr/lib/udev/rules.d/` by the .deb) <span class="tag static">STATIC</span> (OpenFlow, link at
release); tested in packaging only, not yet with a keyboard on a Linux seat:

```text
ACTION!="remove", SUBSYSTEMS=="usb", ATTRS{idVendor}=="37d1", ENV{ID_MM_DEVICE_IGNORE}="1"
ACTION!="remove", SUBSYSTEM=="tty", ATTRS{idVendor}=="37d1", TAG+="uaccess"
```

Install it with `sudo cp 70-openflow.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules && sudo udevadm trigger`,
then replug the halves. Do not run tools as root when a udev rule will do.

## Browsers and mobile hosts

- **Web Serial** (browser configurators) exists in Chromium-based desktop browsers only, over HTTPS
  or localhost <span class="tag inferred">INFERRED</span> (web platform documentation; re-check
  before relying on it). See [JavaScript recipes](recipes-js.md).
- **Phones and tablets** can only be Bluetooth hosts (typing); configuration needs USB. The vendor
  lists Windows, macOS, Debian Linux, iPadOS, iOS and Android as tested hosts for BLE v2; each host
  slot advertises as "NayaCreate BLE n" from BLE v2 on, and some hosts need Bluetooth restarted to
  see the new name <span class="tag doc">DOC</span> (1.19.1 notes[^rel])
  <span class="tag measured">MEASURED</span> (third party: no configuration channel over Bluetooth[^cfd]).

## Open questions

- <span class="tag open">OPEN</span> OpenFlow and the udev rule with a keyboard on a Linux machine; our tools on macOS ([details](../open-questions.md#oq-s10)).
- <span class="tag open">OPEN</span> Whether 3.35.4 shows one or two CDC interfaces per half (not recorded).
- <span class="tag open">OPEN</span> NayaFlow on Linux after 1.17.3 ([details](../open-questions.md#oq-s09)).

## Sources

[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (README, `nayactl.cmd`, `discovery.py`); comment on pull request #2 about the cp1252 crash.
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (Windows serial settings `dsrdtr=False` and `write_timeout`).
[^nh-hw]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^manual]: Naya Create manual v1.1.x (see [Manuals](../product/manuals.md) for archived copies).
[^bg]: NayaFlow 1.25.1, `flow/flow-bg-server.exe`: strings (the update dialog's cabling rules).
[^nc-mac]: NayaFlow 1.25.1 for macOS, `NayaFlow.app/Contents/core/NayaCore.app/Contents/MacOS/NayaCore`: code signature (CodeDirectory flags, entitlements).
[^rel]: Vendor release notes, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases), mirrored in nayaHistory [`CHANGELOG.md`](https://github.com/traviswye/nayaHistory/blob/79eeefb/CHANGELOG.md).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).
[^cc]: Create Companion, [github.com/traviswye/create-companion](https://github.com/traviswye/create-companion) (README).
[^cfd]: createflow-dongle, [`docs/findings.md`](https://github.com/mediaandmerch/createflow-dongle/blob/main/docs/findings.md).
[^cfd-rel]: createflow-dongle, [release 0.1.3](https://github.com/mediaandmerch/createflow-dongle/releases) notes.
[^kb-recovery]: naya-create-kb, [recovery](https://nemezzizz.github.io/naya-create-kb/recovery/) and [firmware/bootloader](https://nemezzizz.github.io/naya-create-kb/firmware/bootloader/).
[^kb-python]: naya-create-kb, [toolkit/python](https://nemezzizz.github.io/naya-create-kb/toolkit/python/).
[^kb-appdata]: naya-create-kb, [software/app-data](https://nemezzizz.github.io/naya-create-kb/software/app-data/).
[^kb-toolkit]: naya-create-kb, [toolkit](https://nemezzizz.github.io/naya-create-kb/toolkit/).

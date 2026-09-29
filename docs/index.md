# Create knowledge base

The Naya Create is a split ergonomic keyboard: two halves, each with its own USB-C port, Bluetooth
radio and firmware, and a module dock on each inner edge that takes a Touch (touchpad), a Track
(trackball) or a Tune (dial with a touch surface and haptics); a Speedlink dongle came in the box
<span class="tag doc">DOC</span>[^man-c][^ks-camp]. The left half is the central that holds the keymap
and talks to the host; the right half reaches it over a Bluetooth link between the halves
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09). This site documents its
hardware, wire protocol, firmware, storage, recovery and host software, from our own measurements,
static reading of the vendor's released software, and public filings.

Naya B.V. has ceased operations and no longer supports the Create. The naya.tech domain now belongs
to another company, so this site never links live naya.tech pages: every vendor web page is cited
through an archived copy (Wayback Machine), or not linked at all.

!!! danger "Writes can brick or wedge a board"
    Every write on this protocol takes effect at once and persists; there is no commit and no undo.
    A firmware flash can leave a half in its bootloader, `30/10ca` wipes the keymaps, some settings
    and records stop every key or darken the board, and firmware 3.28.7 wedges on any write of three
    frames. Read [Recovery](recovery.md) and the
    [never-send list](troubleshooting.md#the-never-send-list) before you send anything that is not a
    read, check the firmware of **both** halves first (`fe/1002`), and make first attempts on a board
    you can afford to lose.

## Start here

- [Overview](product/overview.md): the Create and its family, how the pieces connect, the versions.
- [Transport](protocol/transport.md): the frame, the checksum, addressing, and the byte convention
  every protocol page uses.
- [Command map](protocol/commands.md): every known command by category, with its params and reply.
- [Recovery](recovery.md): a dark board, a wedged half, a half stuck in its bootloader, lost bonds.
- [Tools](tools/index.md): OpenFlow, nayactl, Create Companion, create-legacy-firmware and the recipes.

## How to read the evidence

Every fact that is not common knowledge carries a tag, and a footnote names its source.

| Tag | Meaning |
|---|---|
| <span class="tag measured">MEASURED</span> | observed on a real board; the firmware and date are given, for example "on 3.41.0, 2026-09-20" |
| <span class="tag static">STATIC</span> | read from the vendor's released software: NayaFlow, NayaCore, the firmware images |
| <span class="tag doc">DOC</span> | vendor documents, manuals, FCC and ISED filings, Kickstarter updates, release notes |
| <span class="tag inferred">INFERRED</span> | our reasoning; the reason is given |
| <span class="tag reported">REPORTED</span> | a third party states it and we have not verified it; the source is named. "Raw data checked" means we decoded that party's own published data and it agrees |
| <span class="tag open">OPEN</span> | unknown; each one links to its row on [Open questions](open-questions.md) |

Unless a page says otherwise, MEASURED means measured on the owner's boards: a daily-use board on
3.41.0, a donor board on 3.28.7, and a board flashed between 3.35.4 and 3.41.0.

**Versions** are written 3.41.0 (keyboard) and 2.3.3 (module); the four-part form a half reports on
the wire is explained once, on [Versions](firmware/versions.md). **Byte strings** are lower-case hex
with spaces, commands are named `category/command` (for example `30/1004`), and a params or reply
string starts with the flag or status byte: the convention is declared on
[Transport](protocol/transport.md#byte-convention). **An acknowledgement proves the keyboard parsed a
frame, not that it applied it**: read back what you write
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-07).

## Section map

| Section | What it covers |
|---|---|
| **Product** | [Overview](product/overview.md) of the family and its versions; the vendor [manuals](product/manuals.md), cited by version |
| **Hardware** | [Board inventory](hardware/index.md), [the keyboard half](hardware/half.md), [module dock](hardware/dock.md), [Tune](hardware/tune.md), [Touch](hardware/touch.md), [Track](hardware/track.md), [Speedlink dongle](hardware/dongle.md), [power and batteries](hardware/power.md), [layout and positions](hardware/layout.md), [regulatory records](hardware/regulatory.md) and the [parts list](hardware/parts.md) |
| **Connectivity** | [USB](connectivity/usb.md) identities and ports, [Bluetooth](connectivity/bluetooth.md) hosts and GATT, and the [split link](connectivity/split-link.md) between the halves |
| **Wire protocol** | [Transport](protocol/transport.md), [command map](protocol/commands.md), [keymap](protocol/keymap.md), [layers](protocol/layers.md), [LEDs](protocol/led.md), [settings and timing](protocol/settings.md), [modules](protocol/modules.md), [module fields](protocol/module-fields.md) and [differences by firmware](protocol/firmware-differences.md) |
| **Firmware** | Image format and signing ([images](firmware/images.md)), the [bootloader](firmware/bootloader.md), every [version](firmware/versions.md), the measured [flashing](firmware/flashing.md) procedure, [module firmware](firmware/modules.md) and the [ZMK](firmware/zmk.md) lineage |
| **Storage** | The [flash layout](storage/flash-layout.md), what survives what, and the [factory reset](storage/factory-reset.md) command |
| **Recovery and troubleshooting** | A symptom-to-recipe [recovery](recovery.md) cookbook with safety levels; [troubleshooting](troubleshooting.md), vendor bugs by firmware and the never-send list |
| **Host software** | [NayaFlow and NayaCore](software/nayaflow.md), [app data](software/app-data.md), the release [history](software/history.md) and the [disassembly](software/disassembly.md) method and results |
| **Tools** | [Overview](tools/index.md) of community tools, tested [Python](tools/recipes-python.md) and [JavaScript](tools/recipes-js.md) recipes, and [platform notes](tools/platforms.md) |
| **Reference** | [Open questions](open-questions.md) with how to settle each, the [glossary](glossary.md), and [about](about.md) |

## How this knowledge base was built

From live work over USB on the owner's boards (reads, writes, captures of NayaFlow, firmware
flashing), static reading of every NayaFlow release, the FCC filings, the vendor's manuals and release
notes, and the public work of nayactl, naya-create-kb, createflow-dongle and Create Companion. Every
fact first reported by another project was then checked against our own material where that was
possible. [About](about.md) describes the methods, the sources, the credits, the license (pages
CC BY 4.0, code snippets MIT) and how to send a correction.

## Sources

[^man-c]: Naya Create User Manual Version 1.1.0 (vendor PDF, 2025-11-10); see [Manuals](product/manuals.md).
[^ks-camp]: Kickstarter campaign page, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023).

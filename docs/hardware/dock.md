# Module dock

The dock is the interface between a half and a module: 8 contacts on each side, carrying power in both
directions, a UART, a boot line and an enable, held together by magnets. This page covers the
mechanics, the net names on both sides, what flows through the dock and what does not (USB data), how
the half identifies a docked module, and how module firmware reaches a module. The one thing to know:
no dock contact carries USB data, and the pin-to-signal order is not established, so do not probe the
contacts with a supply.

!!! note "At a glance"
    - 8 contacts on each side: spring pins on the half, flat pads on the module.
    - Net names: UART (`TX`/`RX`), boot select, module battery, 5 V feed, enable, ground; no `D+`/`D-`.
    - Power flows both ways: the half charges the module on USB, the module powers the half off USB.
    - A docked module's address encodes type and side: Touch `0x10`/`0x11`, Track `0x20`/`0x21`, Tune `0x40`/`0x41`; `0xF0`/`0xF1` means nothing booted answers.
    - Each half's bay holds 6 magnets (measured).

## Mechanics

<!-- dock facts 1-4, 32-35, 37 -->
<!-- fcc-images:start -->

<figure markdown="span">
  ![Left half module bay: magnet carrier plate (top) and bay bracket with the dock and pogo boards mounted (bottom)](../assets/images/fcc/boards/half-module-bay.jpg){ width="560" loading=lazy }
  <figcaption>Left half module bay: magnet carrier plate (top) and bay bracket with the dock and pogo boards mounted (bottom). FCC ID 2BQ4V0825CRL, Internal Photos 1, page 5, upper photo. Identifying marks removed.</figcaption>
</figure>

<!-- fcc-images:end -->

Each half has one module bay: a circular through-cutout in the dock section with one straight chord,
where the contacts sit <span class="tag doc">DOC</span> CRR EP p2, p3[^fcc-crr][^um106]. The half side has an 8-position spring-pin
(pogo) block: 8 gold domed pins in two staggered rows of four, a black insulator, through-hole, with no
maker marking visible anywhere in the filings <span class="tag doc">DOC</span> CRL IP2 p15; CRR IP2 p13[^fcc-crl][^fcc-crr]. The pins
are on a small D-shaped pogo board (`Create_L_PogoPin_20250109_V10`, 0.6 mm, about 16 x 17 mm) with 5-6
small ESD diodes, joined to the dock (thumb-key) board by a black flex of about 50 mm <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>.

**Magnets.** Each half's bay holds 6 magnets: one on either side of the contact block and 4 spaced
around the bay <span class="tag measured">MEASURED</span> (owner's board, paper-clip test, 2026-09-23). In the photos they are the two small
light-colored features flanking the contact block on the chord (the manual drawing shows a small
pocket on each side of the pins) and the 4 blocks on the carrier plate; the 5 blocks on the metal bay
bracket did not attract a clip, so they are not magnets <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl][^um106]. Each module base
holds 6 metal blocks, magnet or steel not tested; the manual says there are magnets "in the dock and on
the bottom of the module" <span class="tag doc">DOC</span>[^um106] ([details](../open-questions.md#oq-h13)).

**Docking.** Align the contacts, let the magnets pull the module in and seat it completely flat "for a
proper connection with the data pins"; to remove it, push up through the dock cutout with the keyboard
lifted or tented <span class="tag doc">DOC</span>[^um106][^man-c][^man-to].

**Design history.** The vendor's dock design of late 2023: pogo pins plus magnets strong enough to hold
a module when tented, stabilizing pins against sideways movement and contact wear, and a dock base
enlarged from 66 to 69 mm across, 4 mm high; prototype pogo pins went from a 45-degree to a vertical
arrangement <span class="tag doc">DOC</span>[^ks-04][^ks-08]. A Naya patent on the Float describes a teardrop-shaped indent in the
dock and a matching protrusion on the module to stop rotation, and a variant with a ferromagnetic base;
it describes no contacts or data interface <span class="tag doc">DOC</span>[^wo].

## The contact blocks

<!-- dock facts 5-9 -->
<!-- fcc-images:start -->

<figure markdown="span">
  ![Left pogo board with its flex: contact face (top) and back (bottom)](../assets/images/fcc/boards/pogo-board-left.jpg){ width="560" loading=lazy }
  <figcaption>Left pogo board with its flex: contact face (top) and back (bottom). FCC ID 2BQ4V0825CRL, Internal Photos 2, page 15, upper and lower, stacked. Identifying marks removed.</figcaption>
</figure>

<!-- fcc-images:end -->


| Side | Board | Contacts | Labels as read | Evidence |
|---|---|---|---|---|
| Half | pogo board `Create_L_PogoPin_20250109_V10` | 8 spring pins, two staggered rows of four | pads (left back) `GND_4`, `BOOT_2`, `MZ_VBAT`, `RX_2`, `..._ON1`; (right) `GND_4`, `BOOT_2`, `5V_1`, `RX_2`, `TX`, `USB_5V` | <span class="tag doc">DOC</span> CRL IP2 p15; CRR IP2 p13 |
| Half | dock board and mainboard | (nets toward the pogo board) | dock board `TX_1`, `RX_1`, `BOOT_1`, `MZ_VBAT_1`, `LDO_ON_1`, `USB_5V_2`; mainboard `LDO_ON`, `TX`, `RX`, `POGOPIN_5V` | <span class="tag doc">DOC</span> CRL IP1 p9; CRL IP2 p16; CRR IP1 p12 |
| Tune | main board `J5`, plus 8 flat pads on its base | 8, in a 1-2-2-2-1 stagger | `GND`, `VBAT`, `RX`, `ON`, `GND`, `TX`, a 5 V line, `BOOT1` | <span class="tag doc">DOC</span> CRL IP3 p19; CRL IP2 p17-p18 |
| Touch | pogo board `J2` | 8 domed contacts in two columns of four | `GND`, `VBAT`, `RX`, `…ON`, `BOO…`, `GND` | <span class="tag doc">DOC</span> CRL IP5 p32 |
| Track | `Track_Pogo_Pin_20241122_V08`, fed through a separate interposer | 8 in a 2 x 4 block | `GND`, `VBAT`, `RX`, `ON`; interposer headers `GND`, `RX`, `TX` and `ON`, `5V`, `GND`, plus a `BOOT1` pad | <span class="tag doc">DOC</span> CRL IP6 p37, p40 |

All citations[^fcc-crl][^fcc-crr]. Some earlier readings counted 12 contacts on the Tune and 10 on the
Touch and Track; every board has 8 <span class="tag doc">DOC</span>. The Touch base shows only a single row of 4 contacts through a
slot, although its pogo board has 8; why is not known. Vendor underside renders showing 6 pads in a row
are older marketing art <span class="tag doc">DOC</span>[^fcc-crl][^wb-naya] ([details](../open-questions.md#oq-h11)).

## What the dock carries

<!-- dock facts 10-14, 36, 38 -->
The net set is: UART (`TX`/`RX`), a boot-select line (`BOOT`/`BOOT1`), the module battery line
(`MZ_VBAT`/`VBAT`), a 5 V feed (`USB_5V`/`POGOPIN_5V`/`5V`), an enable (`LDO_ON`/`MODULE_ON`/`ON`) and
ground. No contact label anywhere reads `D+` or `D-` <span class="tag doc">DOC</span>[^fcc-crl]. The functions follow from the names
only; which pin carries which net, and the direction of each line, are not established, because the
schematic is confidential <span class="tag inferred">INFERRED</span> ([details](../open-questions.md#oq-h09)).

The module boards' `VBUS`, `VBUS_5V` and `USB_5V` pads carry the 5 V feed from the dock, not USB data.
The modules' STM32F411 has a USB device, but nothing shows it wired to the dock <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>.

| Net (by name) | Half side | Module side | Direction (inferred) |
|---|---|---|---|
| UART | `TX`, `RX` (`TX_1`, `RX_1`, `RX_2`) | `TX`, `RX` | both, one each way |
| Boot select | `BOOT_1`, `BOOT_2` | `BOOT1` | half to module |
| Module battery | `MZ_VBAT`, `MZ_VBAT_1` | `VBAT` | both |
| 5 V feed | `USB_5V`, `POGOPIN_5V`, `5V_1` | `5V`, `VBUS`, `USB_5V` | half to module |
| Enable | `LDO_ON`, `..._ON1` (`MODULE_ON` on the mainboard) | `ON` | half to module |
| Ground | `GND_4`, `GND3` | `GND` | - |

Pin positions are not established <span class="tag open">OPEN</span>.

Power flows both ways through the dock: the half feeds 5 V to a docked module (which charges it when
the keyboard has power), and a charged module powers the half when there is no USB <span class="tag doc">DOC</span>[^um106][^man-c].
On each module the dock 5 V and the Qi receiver
output (`QI_VBUS`) reach the SGM41523 charger through `SL` Schottky diodes; the Tune and Touch also
carry an SGM62117 buck-boost, whose role (3.3 V from the cell, or 5 V toward the dock) is not established
<span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl]. The modules have no radio and link to the half only through the dock contacts; the Qi
coil is a power receiver <span class="tag doc">DOC</span>[^fcc-crl].

A January 2024 vendor update described a wired full-duplex chain at "10 mb/s" from the right module
through both halves and the left module to the computer; the dock link's actual rate on shipped
hardware is not known, and no wired traffic between the halves has been observed
<span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^ks-10] ([details](../open-questions.md#oq-c15)); see [Split link](../connectivity/split-link.md).

## What the host sees

<!-- dock facts 15-23 -->
Docking or undocking a module makes that half re-enumerate on USB; an open serial handle goes stale and
must be reopened. NayaFlow restarts itself when a module is re-docked <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09).

A docked module's type and side come from its dock address: bit 0 is the side (0 left, 1 right) and the
high nibble is a one-hot type <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-03; a second board, 3.28.7,
2026-09-19; also on the nayactl maintainer's board, 3.30.1[^nx-pr2]):

| Module | Left | Right | Evidence |
|---|---|---|---|
| Touch | `0x10` | `0x11` | <span class="tag measured">MEASURED</span> |
| Track | `0x20` | `0x21` | <span class="tag measured">MEASURED</span> |
| Tune | `0x40` | `0x41` | <span class="tag measured">MEASURED</span> |
| Float (never shipped) | `0x80` | `0x81` | <span class="tag inferred">INFERRED</span> by the pattern; nayactl placeholder[^nx] |
| nothing booted answers | `0xF0` | `0xF1` | <span class="tag measured">MEASURED</span> |

A docked module that has not booted (at about 0-1 % battery) stays dark and answers as `0xF0` (left) or
`0xF1` (right), reporting firmware 0.0.0; an empty dock gives the same reply <span class="tag measured">MEASURED</span> (a second board,
3.28.7, 2026-09-19; the no-answer value on 3.41.0, 2026-09-03). The nayactl maintainer reports that the
module boots once it has drawn enough dock power, at about 1 % <span class="tag reported">REPORTED</span>[^nx-pr2].

- **Presence.** The presence command (`de/1002`) reports presence only (`01` for any module); reading
  it as a type code labels every module a Touch <span class="tag measured">MEASURED</span> (owner's board, 3.41.0)[^nx-pr2].
- **Handshake.** `de/1001` replies `00 01 <addr>` for a docked, booted module (status `00`, handshake
  byte `01`, dock address) and `00 00 f0` when nothing booted answers <span class="tag measured">MEASURED</span>.
- **Which bay.** Use the dock address, not which LEDs look lit, to tell which bay a module is in <span class="tag measured">MEASURED</span>
  (a second board, 3.28.7, 2026-09-19).
- **Per half.** Module queries go to the half the module is docked on, and each half reports only its
  own module <span class="tag measured">MEASURED</span>.
- **Module firmware.** `de/1008` answers on both halves: reply
  `00 <addr> <flag> 00 <major> <minor> <patch>` (the flag byte read `00`, and `01` with an all-zero
  version while a module had not reported yet) <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, both halves, 2026-09-11 and
  2026-09-16; also reported in nayactl pull request 5, `00 20 00 00 02 02 02` Track left and
  `00 11 00 00 02 02 02` Touch right on the maintainer's 3.30.1 board[^nx-pr5]).
- **Versions in the field.** The Tune and Track on the owner's 3.41.0 board report module firmware
  2.3.3, while the Touch on the same board reported 2.1.2 (right-docked, 2026-09-11 and 2026-09-16);
  2.1.2 (also on a second board's modules) and 2.2.2 are in the field too <span class="tag measured">MEASURED</span>[^nx-pr5].
- **Stored bundle.** The stored module-bundle version (`de/100a`) is answered by the left half only,
  because only the left half holds the module firmware store <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-16).

Byte strings follow the convention on [Transport](../protocol/transport.md); the commands are on
[Modules](../protocol/modules.md).

## Configuration and lighting belong to the bay

<!-- dock facts 24-27 -->
Module configurations for both bays live on the left half; NayaFlow writes even the right-docked
module's configuration to the left, and the right half reports no module-config slots <span class="tag measured">MEASURED</span> (owner's
board, 3.41.0, NayaFlow write captures, 2026-09). Each layer's keymap has 8 bay positions
(`0x4A`-`0x51`: Touch, Track, Tune, Float, each left and right) that point to a module-config slot,
inherit from the base layer, or are empty; a module whose bay is empty on the base layer runs its own
animation and answers no gesture <span class="tag measured">MEASURED</span> (2026-09-03, 2026-09-16). See [Keymap](../protocol/keymap.md).

Each bay has its own 24-entry LED block in the whole-board map (88-111 left, 112-135 right); the block
belongs to the bay, not to the module: swapping a Tune and a Track kept each side's color <span class="tag measured">MEASURED</span> (owner's
board, 3.41.0, 2026-09-08). See [Layout and positions](layout.md#the-led-map).

## Module firmware through the dock

<!-- dock facts 28-31 -->
Module firmware reaches a module through the dock. NayaCore carries a 1 MiB LittleFS bundle
(`FlashMemory.bin`) of encrypted module apps (`.sfb` files) inside its own executable, uploads it to the
LEFT half's module store over the bootloader's serial protocol (image slot 4), then tells the half to
program the docked module (`de/1005`) <span class="tag static">STATIC</span>[^nc]. We have run it on the owner's board (left half on
3.41.0, 2026-09-23): NayaFlow updated a Touch, and OpenFlow's own module update then flashed a Touch up,
down and up again and downgraded a Track, which read back as a correct Track; `de/1005` carries one byte for the
module type (`01` Touch, `02` Tune, `03` Track). One later Track update never finished and left that
Track silent <span class="tag measured">MEASURED</span>[^fp-modules]. See [Module firmware](../firmware/modules.md).

The UART and `BOOT1` nets fit a module update driven by the half over UART with a boot strap
(inferred, untested); nothing shows the STM32's USB bootloader reachable through the dock <span class="tag inferred">INFERRED</span>. Module
images are not MCUboot images; the module's own bootloader is unidentified (NayaCore does name an
`M_MCUBOOT_RESTART` module mode) <span class="tag static">STATIC</span>[^nc].

Vendor rules for a module update: only one up-to-date left half with the module docked may be
connected, the module must be on, and a Tune may take up to a minute to appear the first time; the
forced update ("Danger Zone") is for a module that does not respond after battery recovery and can take
up to 4 minutes <span class="tag doc">DOC</span>[^nc]. Detail on [Module firmware](../firmware/modules.md).

## Care and safety

<!-- dock fact 35 -->
!!! danger "Do not bridge the dock contacts"
    The `VBAT` contacts carry the module battery; a short across the dock can discharge or damage a
    pack. The manuals say: do not short or bridge the pogo pins, do not clean them with liquids,
    chemicals or abrasion, and when tenting avoid pressing on the connection pins
    <span class="tag doc">DOC</span>[^um106][^man-c]. Do not probe the dock with a bench supply or USB without knowing the pin order,
    which is not established.

!!! danger "Module updates can leave a module dark or hang the keyboard"
    We have run module updates, NayaFlow's forced update (a vendor "Danger Zone" operation) included,
    on the owner's board (left half, 3.41.0, from 2026-09-23). Two things went wrong on the way: the
    type byte in `de/1005` must match the docked module, and `03` (Track) sent to a Tune programmed it
    with the Track's app and left it dark until a forced update with `02` restored it; and one Track
    update never finished, hung the keyboard until a power cycle, and left that Track answering like an
    empty bay <span class="tag measured">MEASURED</span>[^fp-modules]. Pick the type that is physically docked. See
    [Module firmware](../firmware/modules.md).

## Open questions

- <span class="tag open">OPEN</span> Pin-to-signal map, voltages and UART settings of the dock; how the half puts a module into its bootloader ([details](../open-questions.md#oq-h09)).
- <span class="tag open">OPEN</span> Tune `J5`: 8 or 10 contacts ([details](../open-questions.md#oq-h10)).
- <span class="tag open">OPEN</span> Why the Touch base shows only 4 contacts ([details](../open-questions.md#oq-h11)).
- <span class="tag open">OPEN</span> Spring-pin block maker, pitch and stroke ([details](../open-questions.md#oq-h12)).
- <span class="tag open">OPEN</span> Module-base blocks: magnet or steel ([details](../open-questions.md#oq-h13)).
- <span class="tag open">OPEN</span> The module MCU's bootloader identity and whether module images are signed ([details](../open-questions.md#oq-f09)).
- <span class="tag open">OPEN</span> The Float's address (`0x80`/`0x81` inferred) ([details](../open-questions.md#oq-p23)).
- <span class="tag open">OPEN</span> The dock link's rate ([details](../open-questions.md#oq-c15)).

## Sources

[^fcc-crl]: FCC ID 2BQ4V0825CRL (left half; the module photos are in both filings): exhibits on the FCC record ([FCC EAS search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm), grantee 2BQ4V; mirror [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL)). Codes are explained on [Regulatory records](regulatory.md#how-to-cite-an-fcc-photo).
[^fcc-crr]: FCC ID 2BQ4V0825CRR (right half); mirror [fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR).
[^um106]: Naya Create User Manual Version 1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits ([fccid.io](https://fccid.io/2BQ4V0825CRR)); see [Manuals](../product/manuals.md).
[^man-c]: Naya Create User Manual Version 1.1.0 (vendor PDF, 2025-11-10); see [Manuals](../product/manuals.md).
[^man-to]: Naya Touch, Tune and Track User Manuals Version 1.1.0 (vendor PDFs), p3-p4.
[^nc]: NayaFlow 1.25.1: NayaCore 6.11.0 strings and embedded resources, and the user-interface strings (static reading).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py`).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) and its comments (maintainer's board on 3.30.1, modules on 2.2.2).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) (maintainer's comment with `de/1008` replies).
[^ks-04]: Kickstarter update 4, [2023-08-10](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3881566).
[^ks-08]: Kickstarter update 8, [2023-11-28](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3964585).
[^ks-10]: Kickstarter update 10, [2024-01-06](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4000229).
[^wo]: WO2025188184A1, "Manual user input device", Naya B.V., published 2025-09-12 ([Google Patents](https://patents.google.com/patent/WO2025188184A1/en)).
[^wb-naya]: The vendor's former website, archived by the Wayback Machine ([naya.tech captures](https://web.archive.org/web/2025*/naya.tech/*)); cited only, images not reproduced.
[^fp-modules]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Module firmware update, captured from NayaFlow (2026-09-23)"](https://github.com/create-collective/create-legacy-firmware/blob/db9a07c/FLASHING-PROCEDURE.md#module-firmware-update-captured-from-nayaflow-2026-09-23) (NayaFlow and OpenFlow module updates on the owner's board, and "A module that hangs the keyboard (Track, 2026-09-23)").

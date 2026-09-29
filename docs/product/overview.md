# The Naya Create

The Naya Create is a split, low-profile ergonomic keyboard made of two halves, each with a round dock
that holds one input module (Touch, Track or Tune), plus a Speedlink USB dongle in the box. This page
covers what the pieces are, how they connect, the models and identifiers, where the manual's
specifications and the filed hardware differ, which versions are in the field, and how the product
came to be. The one thing to know first: the left half is the central of the pair; it holds the
whole keymap and talks to the right half over a Bluetooth split link, so almost every tool talks to
the left half.

!!! note "At a glance"
    - Two halves, each a complete device with its own nRF52840 radio SoC, USB-C port, small cell, power switch and firmware image.
    - The halves are bonded to each other over Bluetooth LE; the left half is the central and holds the keymap, LED maps and module configurations for both.
    - Three modules shipped (Touch, Track, Tune); they have no radio and talk to the half through 8 dock contacts.
    - Output goes to one host at a time: USB or one of four Bluetooth host slots.
    - The Speedlink dongle ships in the box, but no shipped firmware gives it a working role.
    - Last vendor release: NayaFlow 1.25.1 (2026-07-21) with keyboard firmware 3.41.0 and module firmware 2.3.3.

Tags on this site say how each fact is known (MEASURED, STATIC, DOC, INFERRED, REPORTED, OPEN); see
the [home page](../index.md) for the legend. Firmware versions are written 3.41.0 and 2.3.3 here; the
wire form is explained on [Firmware versions](../firmware/versions.md).


!!! info "Manual"
    [Create](../assets/manuals/naya-create-user-manual-v1.1.0.pdf), [Touch](../assets/manuals/naya-touch-user-manual-v1.1.0.pdf), [Tune](../assets/manuals/naya-tune-user-manual-v1.1.0.pdf) and [Track](../assets/manuals/naya-track-user-manual-v1.1.0.pdf) user manuals v1.1.0 (PDF); every version is listed on [Manuals](../product/manuals.md).

## What the Create is

<!-- overview facts 1-3, 5-6, 50, 64-65 -->
The Create is a split, low-profile ergonomic keyboard: two separate halves, each with a round module
dock that holds one input module <span class="tag doc">DOC</span>[^um106][^man-c]. Each half is made of three hinged sections: the
main body, the outer "wing" (two key columns, the power switch and a light bar) and the "dock" (the
module ring with three thumb keys) <span class="tag doc">DOC</span>[^um106][^man-c]. There are 74 keys, 37 per half (24 on the
body, 10 on the wing, 3 on the dock), plus a 7-LED light bar on each wing; NayaFlow 1.25.1 draws the
same 74 keys and 14 side LEDs <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^um106][^fcc-crl][^nc]. Details are on
[The keyboard half](../hardware/half.md) and [Layout and positions](../hardware/layout.md).

The maker of record is Naya B.V. of Groningen, the Netherlands; the underside engraving reads
"Designed by Naya in the Netherlands" and "Made in China" <span class="tag doc">DOC</span>[^fcc-crr]. Manufacturing was done by an
ODM, Dongguan Boen Intelligent Technology Co., Ltd., named as manufacturer and factory on all three FCC
test reports; the same company made both PCB antennas <span class="tag doc">DOC</span>[^fcc-crl][^fcc-dg].

The firmware is a closed-source custom fork of ZMK by the vendor's own statements (2023), and the
vendor published no protocol documentation <span class="tag doc">DOC</span>[^ks-camp][^ks-09][^reddit-jklwnhz]; see
[ZMK](../firmware/zmk.md). The manual calls the backlight "Reprogrammable RGB", and marketing called
the module-bay ring light "A-RGB Status Lights" <span class="tag doc">DOC</span>[^um106][^wb-naya]. The product was marketed with Qi
wireless charging for modules, multi-device Bluetooth, tenting and sculpted keycaps
<span class="tag doc">DOC</span>[^um106][^wb-naya].

## The pieces

<!-- overview facts 4, 7, 8, 12, 13, 35 -->

| Piece | What it is | Radio | Microcontroller | Power | FCC ID | USB PID | Page |
|---|---|---|---|---|---|---|---|
| Left half | The central: holds the keymap for both halves | BLE (split link and host); its filing also certifies a 2 Mbps "2.4G SRD" mode | Nordic nRF52840 | USB, or a docked module; 50 mAh cell bridges module swaps | 2BQ4V0825CRL | `0x0064` | [Half](../hardware/half.md) |
| Right half | The peripheral: reports its keys to the left | BLE (split link); its filing also certifies a 2 Mbps "2.4G SRD" mode | Nordic nRF52840 | as the left | 2BQ4V0825CRR | `0x00C8` | [Half](../hardware/half.md) |
| Naya Touch | Glass touchpad module | none | ST STM32F411 | own pack, charged in the dock or on Qi | none | none | [Touch](../hardware/touch.md) |
| Naya Track | 40 mm trackball module with four buttons | none | ST STM32F411 | as the Touch | none | none | [Track](../hardware/track.md) |
| Naya Tune | Knurled dial with a touch surface and haptics | none | ST STM32F411 | as the Touch | none | none | [Tune](../hardware/tune.md) |
| Speedlink dongle | USB-A receiver, `NAYA-100-1` | 2.4 GHz: its filing certifies only a 2 Mbps "2.4G SRD" mode; the manual says Bluetooth 5.4 | Nordic nRF52840 | USB bus power | 2BQ4V0825DG | `0x012C` | [Dongle](../hardware/dongle.md) |

Each half is a complete device: its own USB-C port, its own Nordic nRF52840 radio SoC with native USB,
its own small internal cell, its own power switch and its own firmware image; the left and right
images differ in size in every release (for 3.41.0, 328 880 bytes left and 226 000 bytes right)
<span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^fcc-crl][^fcc-crr][^nh-fh]. The three modules that shipped are the Naya Touch (glass
touchpad), the Naya Track (40 mm trackball with four buttons) and the Naya Tune (knurled dial with a
touch surface and haptic feedback) <span class="tag doc">DOC</span>[^man-to][^man-tr][^man-tu][^ks-17].

Modules have no radio: each is an STM32F411 microcontroller with a Qi wireless-charging receiver and a
battery, and it talks to the half through the dock contacts. None has an FCC ID of its own; they are
photographed inside the two halves' filings, and the grantee has exactly three IDs <span class="tag doc">DOC</span>[^fcc-crl][^eas].

The Speedlink dongle (model `NAYA-100-1`) ships in the box; it is its own nRF52840 radio with its own
FCC ID (2BQ4V0825DG) and ISED number (34320-0825DG) <span class="tag doc">DOC</span>[^um106][^fcc-dg][^ised]. The radio the filings certify
differs from the manual's wording: both halves' FCC filings carry a separate "2.4G SRD" 2 Mbps test
report besides BLE, and the dongle's SAR report names only "2.4G SRD", while the manual says
"Speedlink Connection: Using Bluetooth v5.4" <span class="tag doc">DOC</span>[^fcc-crl][^fcc-dg][^um106]. Whether shipping firmware
ever uses the SRD mode, on the halves or the dongle, is <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-c14)). No working role for
it has been demonstrated with shipped firmware: it enumerates on USB but does not answer the halves'
protocol (measured on the owner's dongle, 2026-09-11) <span class="tag measured">MEASURED</span>, no NayaFlow release carries a firmware
image for it and no release note through 1.25.1 enables it <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nc][^nf-rel]. The vendor's
NayaFlow 0.1.0 note reserved a host slot "for future BLE dongle support" <span class="tag doc">DOC</span>[^nf-rel]. A third party
relays vendor statements that the dongle was "not yet active" and "coming soon"; those words are in no
primary source we hold <span class="tag reported">REPORTED</span>[^cfd]. See [Speedlink dongle](../hardware/dongle.md).

## How the pieces connect

### The split link between the halves

<!-- overview facts 16-21 -->
The two halves are bonded to each other over Bluetooth Low Energy (the "split link"): each half's
pair table holds the other half's address, and the left half's Bluetooth status reports a live link
to the right half at a 7.5 ms connection interval, latency 0 and a 4 s supervision timeout
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01 and 2026-09-08, cross-checked both ways). This contradicts
naya-create-kb's statement that there is no radio link between the halves and that the host merges
two streams[^kb-device][^kb-hardware].

Vendor text describes the same link: the BLE v2 firmware (3.35.4) promised "higher bandwidth between
halves", 3.39.4 onward (its beta note says 3.39.3) "reduced BLE traffic between halves", the v1.1.0
manual says to power the left half first "to ensure proper pairing between the keyboard halves", and a
2025 factory issue was "transmitting between the two halves"; the 2023 campaign page already said the
halves talk to each other over RF and that in wired USB mode only the left half sends data to the
computer <span class="tag doc">DOC</span>[^nf-rel][^nf-beta][^man-c][^ks-18][^ks-camp].

With both halves on USB, the right half exposes no keyboard HID interface of its own; its key presses
reach the host through the left half <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01). The left port also
answers some requests addressed to the right half (`dst 0x51`): the firmware-version read reaches the
right half, but the Bluetooth identity reads (`be/1008`, `be/1002`, `be/1005`) sent to `0x51` on the
left port answer for the left half, and requests for the left through the right port get no answer
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-22). This routing runs over the split link: every measurement
fits a radio link, and no wired traffic between the halves has been observed; each half has its own
USB-C port and the Y-cable joins them only at its splitter <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^um106]. It worked even with the
halves on different firmware: the left port read the right half's version (3.35.4) while the right
half's own port returned empty payloads <span class="tag measured">MEASURED</span> (owner's board, left 3.41.0, right 3.35.4, 2026-09-20).
Whether any shipped setup has a wired data path between the halves is open <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-c15)). See [Split link](../connectivity/split-link.md) and
[Transport](../protocol/transport.md).

Which sender byte a reply relayed from the right half carries is not established: naya-create-kb's
device overview says `0x50`, while its transport page implies `0x51`; this site does not state it
<span class="tag open">OPEN</span> ([details](../open-questions.md#oq-c12)). Direct replies carry the answering half's own address
in the sender position; NayaCore's port probe names `aa 50 00 00 fe ...` "ProtocolCDC Left detected"
and `aa 51 00 00 fe ...` Right <span class="tag static">STATIC</span>[^nc].

Toward a host the keyboard is one Bluetooth device, the left half: NayaFlow's BLE v2 warning asks
users to re-pair "NayaCreate Left" only, host device names are "NayaCreate BLE n" per slot, and on
the owner's board the right half answers the Bluetooth status read with nothing and a Windows host
paired one identity <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> <span class="tag doc">DOC</span> (3.41.0, 2026-09-08 and 2026-09-11)[^nc][^nf-rel]. A third-party BLE
central likewise used one connection for the whole keyboard (also reported by createflow-dongle) and
found one battery level only <span class="tag reported">REPORTED</span>[^cfd]. Whether the right half ever advertises to, or bonds with, a
host by itself is open <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-c07)).

### USB and Bluetooth to the host

<!-- overview facts 22-29 -->
Output goes to one host at a time; the user picks the output (USB or a Bluetooth slot) from the
System layer <span class="tag doc">DOC</span>[^man-c][^um106]. Bluetooth offers four user host slots; the firmware status reports
five profiles (0-4) and the stock keys select profiles 1-4 <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-10). The vendor's first notes reserved a fifth slot for a future dongle; the 2023 campaign
promised Bluetooth "to up to five devices", and its FAQ "multiple Bluetooth devices plus one RF device
via the included dongle" <span class="tag doc">DOC</span>[^nf-rel][^ks-camp].

In USB mode each half enumerates a CDC serial interface; on 3.41.0 the left half adds a HID interface,
while on 3.28.7 each half exposes two CDC interfaces of which only one answers <span class="tag measured">MEASURED</span> (owner's board,
3.41.0, 2026-09-01; a second board, 3.28.7, 2026-09-19). The configuration channel over USB stays
usable when output is switched to Bluetooth <span class="tag measured">MEASURED</span> (3.41.0, 2026-09-10). See
[USB](../connectivity/usb.md) and [Bluetooth](../connectivity/bluetooth.md).

Configuration and firmware updates are USB only on 3.41.0. The vendor tool has no Bluetooth path at
all: NayaCore links only Qt Core, SerialPort, Sql and ZeroMQ, and every device worker in it is a
serial one <span class="tag static">STATIC</span>[^nc] (also reported by createflow-dongle). Over Bluetooth, a third party found HID, one
battery level, device information and an idle vendor service that answers no configuration frame,
with no DFU, SMP or UART service <span class="tag reported">REPORTED</span>[^cfd]. The HID report map the naya-create-kb maintainer read over
Bluetooth is byte-identical to the left half's USB HID report descriptor in our own capture (keyboard
with LED output, consumer control, mouse) <span class="tag reported">REPORTED</span> (raw data checked; USB side measured on the owner's
board, 3.41.0, 2026-09-11).

The keyboard would not start Bluetooth pairing while powered over USB <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-11); a third-party guide likewise says to keep it unplugged while pairing[^cfd].

A half that is asleep does not answer on its USB serial port until it is woken by a key press, and
the first frame after waking is often lost <span class="tag reported">REPORTED</span>[^kb-device]. Tools retry their first request (nayactl's
connect handshake makes three attempts)[^nx], but no capture shows a sleeping half; see
[Transport](../protocol/transport.md).

Every power-on passes through the MCUboot bootloader: each half first appears at its bootloader USB
PID for about 1 to 1.7 s, then at its application PID; when one half comes up and re-links, the
central reboots through the bootloader too <span class="tag measured">MEASURED</span> (a second board, 3.28.7, 2026-09-19; owner's board,
3.41.0, 2026-09-22). See [Bootloader](../firmware/bootloader.md).

### The module dock

<!-- overview facts 9-11 -->
A module docks on either half; the same module reports a different dock address depending on the
side, for example a Tune is `0x40` on the left and `0x41` on the right <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-03; a second board, 3.28.7, 2026-09-19; also seen on the nayactl maintainer's board,
3.30.1[^nx-pr2]). The dock is magnetic: each half's module bay holds 6 magnets, one on either side of
the contact block and 4 more spaced around the circular bay <span class="tag measured">MEASURED</span> (owner's board, paper-clip test,
2026-09-23); the manual speaks of "magnets in the dock and on the bottom of the module"
<span class="tag doc">DOC</span>[^um106][^man-c]. The dock carries 8 contacts on both sides (spring pins on the half, flat pads on
the module) and no USB data lines; the net names are UART, boot select, battery, 5 V feed, enable and
ground <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl]. Details on [Module dock](../hardware/dock.md).

### Power in one paragraph

<!-- overview facts 30-31 -->
The half's internal cell only bridges module hot-swaps; normal operation is powered from USB or from a
charged docked module, so wireless use depends on the modules' batteries
<span class="tag doc">DOC</span>[^um106][^man-c][^reddit-jn3wrmk]. Modules charge in the dock when the keyboard has power, and on
any Qi charger whether docked or not <span class="tag doc">DOC</span>[^um106][^man-to]. Details on
[Power and batteries](../hardware/power.md).

## Roles of the two halves

<!-- overview facts 14-15 -->
The left half is the central of the pair: it holds the keymap for both halves, the LED maps for both
halves, the module configurations for both docks and the module firmware store. The right half holds
no keymap and reports no module-configuration slots; one layer-list write to the left restores
lighting on both halves <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01 to 2026-09-20). The right half answers
the status families on its own port (system, Bluetooth, module and dock reads), but NayaCore never
sends it a keymap-family frame, so the left half is the only way in for layout changes <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>
(3.41.0, 2026-09-11)[^nc] (also reported by naya-create-kb). That the right half would never answer
`30/1001` if asked is stated by naya-create-kb but untested <span class="tag reported">REPORTED</span>[^kb-device]. See
[Keymap](../protocol/keymap.md).

## Models and identifiers

<!-- overview facts 32-37 -->

| Item | Value | Evidence |
|---|---|---|
| Model, both halves | `NAYA-800-1(NAYA-CREATE)`; the registered HVINs add a side suffix, `NAYA-800-1(NAYA-CREATE) L` and `... R`, as printed on the two labels and listed by ISED; the halves are also told apart by FCC ID suffix (CRL left, CRR right) | <span class="tag doc">DOC</span> labels, BLE reports p10[^fcc-crl][^fcc-crr][^ised] |
| Model, dongle | `NAYA-100-1(Dongle)` | <span class="tag doc">DOC</span> DG RF report p10, UM1 p2[^fcc-dg][^um106] |
| Equipment name on the filings | "Ergonomic detachable wireless mechanical keyboard"; brand line "NAYA TECH, Naya Create" | <span class="tag doc">DOC</span> CRL and CRR reports p1, p10[^fcc-crl] |
| USB vendor ID | `0x37D1` for every Naya device | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> owner's boards (3.41.0) and dongle, 2026-09-11; nayactl constants[^nx] |
| USB application PIDs | `0x0064` left, `0x00C8` right, `0x012C` dongle | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> as above |
| USB product strings | "Naya Create Left", "Naya Create Right", "Dongle" | <span class="tag measured">MEASURED</span> owner's boards and dongle, 2026-09-11 |
| USB serial string | per unit; it is also the hardware ID that `fe/1004` returns and the key NayaCore uses for the device; values are not reproduced here | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> owner's board; NayaCore "HWID mismatch" string[^nc] |

More on [Regulatory records](../hardware/regulatory.md) and [USB](../connectivity/usb.md).

## Specifications: the manual versus the filings

<!-- overview facts 38-41 -->

| Specification | Manual v1.0.6 says | Filings or measurement show | Evidence |
|---|---|---|---|
| Size | 212 x 118 x 18 mm | most likely per half: the 1:1 label artwork of one half's underside is about 210 x 121 mm | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^um106][^fcc-crr] |
| Weight | 1.4 kg | per half or per pair not stated <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-h28)) | <span class="tag doc">DOC</span>[^um106] |
| Body, dock, wing | "Aerospace Grade Aluminum" | agrees; keycaps are polycarbonate | <span class="tag doc">DOC</span>[^um106] |
| Switches | Kailh CPG-1232, 0.45 x 0.42 mm pin variant | agrees | <span class="tag doc">DOC</span>[^um106] |
| Backlighting | RGB | 88 addressable LEDs on keys and light bars | <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span>; see [Layout](../hardware/layout.md) |
| Bluetooth | 5.4 | the SIG listing's core-spec field reads 5.1 | <span class="tag doc">DOC</span>[^um106][^sig] |
| USB | 2.0 or newer (v1.1.0: USB 3.0) | not tested | <span class="tag doc">DOC</span>[^um106][^man-c] |
| Internal battery | "45mA", Li-ion | a 50 mAh cell per half (3.7 V, 0.185 Wh) | <span class="tag doc">DOC</span>[^fcc-crl][^fcc-crr] |
| Input voltage | "4.2V" | each half's input is rated 5 V DC 1.5 A on its label; 4.2 V reads as the cell's full-charge voltage | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crr] |

The 2023 campaign spec sheet described the pre-production design as 205 x 120 mm, 17 mm total height
(11.2 mm typing height) and 225 g per half <span class="tag doc">DOC</span>[^ks-camp]. Module batteries in the filed samples are
Tune 1000 mAh, Touch 700 mAh and Track 600 mAh (two 300 mAh cells in parallel); the vendor's website
and the 2023 campaign spec sheet said 1500 / 800 / 800 mAh (1500 mAh for the Float), and the v1.1.0
module manuals 1500 / 1500 / 700 mAh; retail capacities are not confirmed <span class="tag doc">DOC</span> <span class="tag open">OPEN</span>
[^fcc-crl][^man-tu][^man-to][^man-tr][^ks-camp] ([details](../open-questions.md#oq-h21)). This
corrects naya-create-kb's attributions of the module packs[^kb-hardware]. The full reading of the
manual is on [Manuals](manuals.md).

## What is in the box

<!-- overview facts 42-44 -->
The v1.0.6 box list: a travel case, the keyboard, the Speedlink dongle, a 1 m USB Type-C Y-cable, one
keycap/switch puller, three spare switches and two module spacers <span class="tag doc">DOC</span>[^um106]. The vendor's later
help-center manual (v1.1.1, no public archive) describes item D as "Y-Cable/Two USB-C cables" <span class="tag doc">DOC</span>.
Modules ship in their own boxes: "1x Naya Touch"; "1x Naya Track" plus "1x 40mm Trackball"; "1x Naya
Tune" <span class="tag doc">DOC</span>[^man-to][^man-tr][^man-tu]. Supported host systems per the manual: Windows 10 and newer,
macOS Ventura and newer, tested on Ubuntu 24.04 LTS <span class="tag doc">DOC</span>[^um106].

## Versions in the field

<!-- overview facts 45-49 -->

| What | Versions | Evidence |
|---|---|---|
| Keyboard firmware seen on hardware | 3.28.7 (a second board), 3.30.1 (the nayactl maintainer's board), 3.35.4 and 3.41.0 (the owner's boards) | <span class="tag measured">MEASURED</span> owner's boards; nayactl pull request 5[^nx-pr5] |
| Module firmware seen | 2.1.2, 2.2.2 (nayactl maintainer) and 2.3.3 | <span class="tag measured">MEASURED</span>[^nx-pr5] |
| Last vendor release | NayaFlow 1.25.1 (2026-07-21), carrying keyboard 3.41.0 and module 2.3.3; engine NayaCore 6.11.0 | <span class="tag doc">DOC</span>[^nf-rel] |
| Beta-only keyboard firmware | 3.39.4, 3.40.0 and 3.40.4 shipped only on the public beta channel (beta 1.22.0's note says 3.39.3, but its app constant and NayaCore's version string say 3.39.4); 3.30.1 is in no public release on either channel; some boards may still run one of these | <span class="tag doc">DOC</span> <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>[^nf-beta][^nh-beta] |
| Bluetooth layer version | `be/100f` replies `00 02` on 3.41.0 on both halves (status, then `02`, which fits the vendor's "BLE v2"); not implemented on 3.28.7 (no frame at all) | <span class="tag measured">MEASURED</span> owner's board, 3.41.0, 2026-09-11; a second board, 3.28.7, 2026-09-19 |
| Dongle | the only version-like value is its USB `bcdDevice 0x0307`; the halves' bootloader identities report the same value, so it most likely reflects the USB stack's default (Zephyr 3.7) rather than a dongle firmware version | <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span> owner's dongle and boards, 2026-09-11 |

naya-create-kb's "BLE FW v0.2.29" read the frame checksum `1d` as a third version byte[^kb-device];
its own capture frames (`aa 50 00 00 be 04 10 0f 00 02 1d 04`) carry one data byte after the status.
Every release is listed on [Firmware versions](../firmware/versions.md) and
[History](../software/history.md).

## Build history

<!-- overview facts 58-62, 66-70 -->
- **Prototypes (2023-2024).** In January 2023 the keyboard had no battery of its own (all batteries in
  the modules; the May 2023 campaign still said so) and tenting was quoted "up to 60°"; the shipped
  manuals say 27° <span class="tag doc">DOC</span>[^reddit-j34wi1g][^reddit-1047jlm][^ks-camp][^um106]. The Reddit quotes on this
  site are archived text, not live-verified.
- **Switches.** The 2023 campaign specified Gateron KS-28 low-profile switches; Gateron's promised
  hot-swap socket never came and the KS-28 had quality problems, so Naya moved to Kailh's PG1232
  ("Choc Mini", already tried in prototype 5) in March 2024. The dock keys, first Kailh CPG1316 scissor
  switches, moved to the same PG1232 in September 2024 (about 3 mm taller). Batch 0 came with linear
  switches, Batch 1 with tactile, and linear became the default from 2025-06
  <span class="tag doc">DOC</span>[^ks-camp][^ks-04][^ks-12][^ks-15][^ks-17][^ks-21].
- **Manufacturer.** In spring 2024 Naya dropped the contract manufacturer that had built all
  prototypes, prototyped with two new ones and chose one in July 2024; the vendor later put the time
  lost at about a year <span class="tag doc">DOC</span>[^ks-12][^ks-13][^ks-14][^ks-25].
- **Module microcontroller.** The modules moved from a Holtek part to ST's STM32F411 in May 2024 (the
  Tune ran on an STM MCU in the July 2024 prototype) <span class="tag doc">DOC</span>[^ks-13][^ks-14].
- **Antenna window.** The all-metal body blocked the radio, so a plastic section was added over the
  antennas by the USB-C port (the black end cap), and the planned slim USB-C receiver dongle became a
  USB-A one <span class="tag doc">DOC</span>[^ks-14][^ks-15].
- **Batches.** EVT1 finished and EVT2 samples arrived in autumn 2024. Batch 0 was 100 test units
  shipped in January 2025 (Create with Touch and Tune; Track later) with mostly-wired tester firmware
  and no remapping or module support. Batch 1 (about 150, April 2025) fixed "a few electrical issues",
  tightened socket tolerance and thickened the power switches. Batch 2 (2 x 250, June 2025), Batch 3
  (2 x about 500, August 2025) and Batch 4 (about 1300, August to September 2025) followed; production
  validation (PVT) was complete by 2025-07-28 and all Kickstarter pledges had shipped by 2025-09-11;
  Batches 0-2 were built during production validation
  <span class="tag doc">DOC</span>[^ks-16][^ks-17][^ks-18][^ks-19][^ks-20][^ks-21][^ks-22][^ks-25].
- **Filed samples.** The FCC samples (received by the lab 2025-06-20, mainboards dated 2025-02-20/21)
  postdate Batch 0, so early retail boards may carry an older board revision than the one filed <span class="tag inferred">INFERRED</span>
  ([details](../open-questions.md#oq-h01)).
- **Vendor batch notes.** "Batch 1 / DVT#2" units could not charge modules over USB until the firmware
  in NayaFlow 0.1.0; a "custom build of NayaCore" was used for testing and validating "the last batch
  of hardware"; NayaFlow 1.15.1 changed readiness detection so "newly delivered" units flash correctly
  <span class="tag doc">DOC</span>[^nf-rel][^nf-beta].
- **A wired chain that did not ship.** In January 2024 the vendor described a wired full-duplex chain
  at "10 mb/s" from the right module through the right half, the left half and the left module to the
  computer <span class="tag doc">DOC</span>[^ks-10]. The 2023 campaign page said the opposite for USB mode (the halves stay on RF,
  only the left sends data over USB), and every measurement on shipped halves fits a radio link between
  them; whether any shipped unit has such a wired path, and what rate the dock link runs at, is not
  known <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-c15)).
- **LED count.** The 2023 campaign spec sheet promised "90 individually addressable RGB LEDs" (listed
  as 68 body, 6 dock edge and 10 wing indicator LEDs, which add up to 84) and two side-glow zones per
  half for status; the shipped keyboard has 88 key and light-bar LEDs (74 keys plus a 7-LED bar per
  half) <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^ks-camp].

## The wider family

<!-- overview facts 51-57, 63, 71 -->
- **Device types in NayaCore:** CreateLeft, CreateRight, Dongle, ModDock, TypeLeft, TypeRight,
  TypeOne; module types TOUCH, TRACK, TUNE, FLOAT <span class="tag static">STATIC</span>[^nc].
- **Five module apps.** Every module firmware bundle, inside NayaCore in every stable release from
  1.11.0 to 1.25.1, contains five encrypted apps: Touch, Track, Tune, Float and Query
  (`*_UserApp.sfb` with `_HASH` sidecars); only Touch, Track and Tune shipped <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nc]
  (also listed by naya-create-kb). See [Module firmware](../firmware/modules.md).
- **Float.** A six-axis ("3D") input puck with a dial ring: marketing showed X/Y/Z, pitch, roll and yaw
  and a dial, the v1.1.0 manual lists the same inputs, and a vendor update of 2025-12-23 described 6DOF
  plus a base dial and put shipping at "Q3" 2026; a Naya patent family (WO2025188184A1) covers it; no
  Float was seen by us <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^ks-24][^ks-26][^man-c][^wo]. By the other modules' address pattern it
  would dock at `0x80` (left) / `0x81` (right); nobody has one to confirm <span class="tag inferred">INFERRED</span>.
- **Query.** It has a firmware app (41 088 bytes in the 1.25.x bundle) but no entry in NayaCore's
  module-type list and no marketing trace <span class="tag static">STATIC</span>. What it is stays unknown; naya-create-kb suggests an
  output-only device such as a display <span class="tag reported">REPORTED</span>[^kb-hardware] ([details](../open-questions.md#oq-h30)).
- **Naya Connect.** Naya announced a second product family: a 75 % keyboard (Naya Type) with a Dock and
  magnetic attachments, crowdfunded in January and February 2026 with delivery estimated from February
  2027; press reports say its Touch, Track, Tune and Float modules also work on the Create. There is no
  FCC filing for it: grantee 2BQ4V has nothing after 2025-09-03 as of 2026-09-23
  <span class="tag doc">DOC</span>[^newatlas][^cnx][^ks-connect][^eas].
- **Other shop items.** The vendor's 2026 shop images also showed a "Type" keyboard, a 24-key
  "Multipad" and a standalone "Dock" with 8 pogo pins and 4 keys; whether any shipped is unknown
  <span class="tag doc">DOC</span>[^wb-naya] <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-h30)).
- **Bluetooth SIG listing.** A listing exists for the keyboard (listing 311198, design Q372162,
  qualified 2025-09-19, model `NAYA-800-1(NAYA-CREATE)`); it describes "USB, 2.4G, BLE three working
  modes". No separate dongle or Naya Connect listing was found <span class="tag doc">DOC</span>[^sig]. Details on
  [Regulatory records](../hardware/regulatory.md).
- **The module layer model.** A 2024 vendor answer already described it: every layer has 9 sublayers,
  1 for the keyboard and 4 for each dock (one per module type), which matches the 8 module-bay
  positions in the keymap <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span>[^ks-11]; see [Layout and positions](../hardware/layout.md).

## Safety

The dock contacts carry battery voltage (see [Module dock](../hardware/dock.md)): do not bridge or short
them, as the manual says <span class="tag doc">DOC</span>[^um106]. The general safety notes are on the [home page](../index.md).

## Open questions

- <span class="tag open">OPEN</span> Whether the right half ever advertises to or bonds with a host by itself ([details](../open-questions.md#oq-c07)).
- <span class="tag open">OPEN</span> Which sender byte a relayed reply carries ([details](../open-questions.md#oq-c12)).
- <span class="tag open">OPEN</span> Whether the Speedlink dongle does anything with shipped firmware ([details](../open-questions.md#oq-c04)).
- <span class="tag open">OPEN</span> Whether 1.4 kg is per half or per pair ([details](../open-questions.md#oq-h28)).
- <span class="tag open">OPEN</span> Retail module battery capacities ([details](../open-questions.md#oq-h21)).
- <span class="tag open">OPEN</span> What Query is; whether Float, Type, Multipad or the standalone Dock shipped ([details](../open-questions.md#oq-h30)).
- <span class="tag open">OPEN</span> Whether early retail boards (Batch 0/1) carry older board revisions than the filed ones ([details](../open-questions.md#oq-h01)).
- <span class="tag open">OPEN</span> What the SIG listing's "2.4G" mode refers to (the "2.4G SRD" mode certified in the halves' and the dongle's FCC filings is one candidate, INFERRED) ([details](../open-questions.md#oq-h37)).
- <span class="tag open">OPEN</span> Whether any shipped setup has a wired data path between the halves ([details](../open-questions.md#oq-c15)).

## Sources

[^fcc-crl]: FCC ID 2BQ4V0825CRL (left half): exhibits on the FCC record ([FCC EAS search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm), grantee code 2BQ4V; mirror [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL)). Short codes such as "CRL IP1 p10" (exhibit Internal Photos 1, lab attachment page 10) are explained on [Regulatory records](../hardware/regulatory.md#how-to-cite-an-fcc-photo).
[^fcc-crr]: FCC ID 2BQ4V0825CRR (right half), including its label artwork ("Create-R Engraving Reference Sheet"); mirror [fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR).
[^fcc-dg]: FCC ID 2BQ4V0825DG (Speedlink dongle); mirror [fccid.io/2BQ4V0825DG](https://fccid.io/2BQ4V0825DG).
[^eas]: FCC OET Equipment Authorization System, [grantee search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm) for grantee code 2BQ4V, read 2026-09-23.
[^ised]: ISED Canada Radio Equipment List, company number 34320 ([search](https://sms-sgs.ic.gc.ca/equipmentSearch/searchRadioEquipments?lang=en)), read 2026-09-23.
[^sig]: Bluetooth SIG qualification listing 311198 ([listing search](https://qualification.bluetooth.com/Listings/Search)), read 2026-09-23.
[^um106]: Naya Create User Manual Version 1.0.6, filed as five exhibits under FCC ID 2BQ4V0825CRR ([fccid.io](https://fccid.io/2BQ4V0825CRR)); "UM1 p3" means part 1, PDF page 3. See [Manuals](manuals.md).
[^man-c]: Naya Create User Manual Version 1.1.0 (27 pages, PDF dated 2025-11-10), the vendor's `Naya_Create_UserManual.pdf` on its shop CDN (read 2026-09-23; no archived copy yet). See [Manuals](manuals.md).
[^man-to]: Naya Touch User Manual Version 1.1.0 (vendor PDF, 9 pages). See [Manuals](manuals.md).
[^man-tr]: Naya Track User Manual Version 1.1.0 (vendor PDF, 8 pages). See [Manuals](manuals.md).
[^man-tu]: Naya Tune User Manual Version 1.1.0 (vendor PDF, 8 pages). See [Manuals](manuals.md).
[^nc]: NayaFlow 1.25.1 (Windows): NayaCore 6.11.0 strings, symbols, imports and embedded resources, and the renderer bundle (static reading).
[^nf-rel]: Vendor release notes, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases) (0.1.0 to 1.25.1).
[^nf-beta]: Vendor beta release notes, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).
[^nh-fh]: create-legacy-firmware, [`FIRMWARE-HISTORY.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FIRMWARE-HISTORY.md) (image catalog of the 25 stable releases).
[^nh-beta]: create-legacy-firmware, [`firmware-history-beta/MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/firmware-history-beta/MANIFEST.json) (beta images carved, commit 7b511ca).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (README and `constants.py`).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (module type detection; maintainer's board on 3.30.1).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) (maintainer's board on 3.30.1 with modules on 2.2.2).
[^cfd]: createflow-dongle, [github.com/mediaandmerch/createflow-dongle](https://github.com/mediaandmerch/createflow-dongle): `docs/findings.md`, `firmware/src/battery.c` and README (third party, keyboard 3.41.0; read at e95b679, 2026-09-23).
[^kb-device]: naya-create-kb, [device overview](https://nemezzizz.github.io/naya-create-kb/device/) (third party).
[^kb-hardware]: naya-create-kb, [hardware deep dive](https://nemezzizz.github.io/naya-create-kb/device/hardware/) (third party).
[^ks-camp]: Kickstarter campaign page with its Specs Sheet and FAQ, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023).
[^ks-04]: Kickstarter update 4, [2023-08-10](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3881566).
[^ks-09]: Kickstarter update 9, [2023-12-07](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3982337) ("based on a customized ZMK base").
[^ks-10]: Kickstarter update 10, [2024-01-06](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4000229).
[^ks-11]: Kickstarter update 11, [2024-02-15](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4029736).
[^ks-12]: Kickstarter update 12, [2024-03-01](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4041543).
[^ks-13]: Kickstarter update 13, [2024-05-08](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4061393).
[^ks-14]: Kickstarter update 14, [2024-07-24](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4157656).
[^ks-15]: Kickstarter update 15, [2024-09-03](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4095301).
[^ks-16]: Kickstarter update 16, [2024-10-06](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4216739).
[^ks-17]: Kickstarter update 17, [2024-11-04](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4243300).
[^ks-18]: Kickstarter update 18, [2025-01-02](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4283150).
[^ks-19]: Kickstarter update 19, [2025-02-11](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4312089).
[^ks-20]: Kickstarter update 20, [2025-03-19](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4341013).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^ks-22]: Kickstarter update 22, [2025-07-28](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4444562).
[^ks-24]: Kickstarter update 24, [2025-08-08](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4452615).
[^ks-25]: Kickstarter update 25, [2025-09-11](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4453988).
[^ks-26]: Kickstarter update 26, [2025-12-23](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4573206).
[^ks-connect]: Kickstarter Naya Connect FAQ, [archived 2026-03-14](https://web.archive.org/web/20260314000000*/kickstarter.com/projects/naya-create/naya-connect*).
[^newatlas]: New Atlas, [Naya Connect modular keyboard](https://newatlas.com/consumer-tech/naya-connect-modular-keyboard/), 2026-01-25.
[^cnx]: CNX Software, [2026-01-30](https://www.cnx-software.com/2026/01/30/) (Naya Connect).
[^wo]: WO2025188184A1, "Manual user input device", Naya B.V., published 2025-09-12 ([Google Patents](https://patents.google.com/patent/WO2025188184A1/en)).
[^wb-naya]: The vendor's former website, archived by the Wayback Machine ([naya.tech captures](https://web.archive.org/web/2025*/naya.tech/*)); cited only, images not reproduced.
[^reddit-jklwnhz]: Reddit, vendor comment [jklwnhz](https://www.reddit.com/r/ErgoMechKeyboards/comments/13jydnp/_/jklwnhz/) (2023-05-18); archived text, not live-verified.
[^reddit-jn3wrmk]: Reddit, vendor comment [jn3wrmk](https://www.reddit.com/r/ErgoMechKeyboards/comments/13jydnp/_/jn3wrmk/) (2023-06-06); archived text, not live-verified.
[^reddit-j34wi1g]: Reddit, vendor comment [j34wi1g](https://www.reddit.com/comments/101pr7o/_/j34wi1g/) (2023-01-06); archived text, not live-verified.
[^reddit-1047jlm]: Reddit, vendor post [1047jlm](https://www.reddit.com/comments/1047jlm/) and comment [j35hisb](https://www.reddit.com/comments/1047jlm/_/j35hisb/) (2023-01-05/06); archived text, not live-verified.

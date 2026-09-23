# Vendor manuals

Naya published a user manual for the Create and one for each module; this page lists every known
version, says where to find it, and records what each states about the hardware, where the manuals
disagree with each other, and where they disagree with the filed hardware. The manuals are cited
by version and page and never republished. The one thing to know: the FCC copy is version 1.0.6,
written for beta testers, and several of its defaults (pairing key, host slots, thumb keys) changed
in version 1.1.0.

!!! note "At a glance"
    - Create manual v1.0.6 is public on the FCC record (right-half filing, five parts, text layer).
    - Create v1.1.0 and the Touch, Tune and Track manuals v1.1.0 are vendor PDFs with a text layer.
    - A help-center Create manual v1.1.1 existed; the help center no longer resolves.
    - The spec sheet's "45mA" battery and "Input Voltage 4.2V" do not match the filed 50 mAh cell and the 5 V 1.5 A input rating.
    - v1.1.0 settles four Bluetooth host slots and moves pairing to the "5" key.

## Which manuals exist

<!-- manuals facts 1-5, 55-56 -->

| Manual | Pages | Date | Where | Text layer | Evidence |
|---|---|---|---|---|---|
| Create, "User Manual Version 1.0.6" | 5 PDF parts | PDFs created 2025-08-18 | FCC ID 2BQ4V0825CRR, user manual exhibits 1-5[^fcc-crr] | yes | <span class="tag doc">DOC</span> |
| Create v1.0.6, image-only copy | 3 PDF parts | exported about a week later | FCC ID 2BQ4V0825CRL, user manual exhibits 1-3[^fcc-crl] | no | <span class="tag doc">DOC</span> |
| Create v1.0.6, dongle filing | 5 PDF parts | same files | FCC ID 2BQ4V0825DG; byte-identical to the right-half copy, so the dongle has no manual of its own[^fcc-dg] | yes | <span class="tag doc">DOC</span> (hashes compared 2026-09-23) |
| Create, "User Manual Version 1.1.0" | 27 | PDF modified 2025-11-10 | vendor PDF `Naya_Create_UserManual.pdf` on its shop CDN[^man-c] | yes | <span class="tag doc">DOC</span> |
| Touch, Tune, Track, "User Manual Version 1.1.0" | 9, 8, 8 | 2025 | vendor PDFs `Naya_Touch_UserManual.pdf`, `Naya_Tune_UserManual.pdf`, `Track_UserManual_100_...pdf` on the same CDN[^man-to][^man-tu][^man-tr] | yes | <span class="tag doc">DOC</span> |
| Create, "Version 1.1.1" (`User_Manual-create-1.1.1.pdf`) | 27 | 2026 | the vendor's help center, which no longer resolves; no public archive found | n/a | <span class="tag doc">DOC</span> |

v1.0.6 is addressed to beta testers ("As a beta tester your unit might have outdated firmware, please
use Naya Flow to update it") <span class="tag doc">DOC</span>[^um106]. The left-half copy differs from the right-half copy only in
that its box list omits the dongle's model line <span class="tag doc">DOC</span>[^fcc-crl]. The four v1.1.0 PDFs answered HTTP 200 on
2026-09-23 at `https://cdn.shopify.com/s/files/1/0667/1663/1351/files/` plus the file names above;
no Wayback capture of them existed on that date, so this site gives the address as text rather than a
link <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span>. The vendor's help center no longer resolves and the naya.tech domain no longer serves
Naya's material (it returned HTTP 402 from at least 2026-09-17), so this site links archived copies
only <span class="tag measured">MEASURED</span> (access checks 2026-09-17 and 2026-09-23). Third-party copies of the v1.0.6 FCC manual parts
exist on aggregator sites such as manuals.plus; our copies match those files byte for byte by hash
<span class="tag doc">DOC</span>.

## Manual v1.0.6, the FCC copy

### The specification sheet as printed

<!-- manuals facts 6-11 -->
Page 3 of part 1 prints: Internal Battery Capacity "45mA", Type "Lithium Ion"; Dimensions "212 x 118
x 18mm"; Weight "1.4kg"; Body / Dock / Wing "Aerospace Grade Aluminum"; Keycaps "Polycarbonate";
Hot-Swappable Switches "Kailh CPG-1232 (0.45x0.42mm pin variant)"; Backlighting "Reprogrammable RGB";
Bluetooth Version "5.4"; Speedlink Connection "Using Bluetooth v5.4"; USB "2.0 or newer"; Input Voltage
"4.2V" <span class="tag doc">DOC</span>[^um106].

| Sheet entry | What the filings or other vendor text show | Evidence |
|---|---|---|
| Switch type | none given: the sheet names the Kailh CPG-1232 part and pin variant only. The word "clicky" in naya-create-kb's summary is not in it; the lab samples have red stems, and the 2023 campaign sold linear and clicky switches separately from the pre-installed tactile ones | <span class="tag doc">DOC</span> UM1 p3, CRL IP1 p5[^um106][^fcc-crl][^ks-camp][^ks-21] |
| Materials | aluminum on the body, dock and wing, polycarbonate on the keycaps; the sheet does not describe the body as "aluminum + polycarbonate" (naya-create-kb's wording) | <span class="tag doc">DOC</span>[^um106][^kb-manual] |
| Keycap legends | the sheet lists keycap material and RGB backlighting only, nothing about transparent or shine-through legends. The 2023 campaign spec sheet did describe "backlit ABS shine-through keycaps with shine-resistant coating" (ABS then; polycarbonate and PC-ABS were sampled in 2024), so naya-create-kb's "transparent characters" has a vendor source, just not the manual. Whether shipped keycaps have shine-through legends is not confirmed | <span class="tag doc">DOC</span> <span class="tag open">OPEN</span>[^um106][^ks-camp][^ks-13] ([details](../open-questions.md#oq-h29)) |
| "45mA" battery | best read as a typo or a minimum rating: the test reports declare a 3.7 V, 50 mAh, 0.185 Wh cell (model 301217) and the photographed cell reads 50 mAh | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> BLE reports p10, CRL IP2 p14[^fcc-crl][^fcc-crr] |
| "Input Voltage 4.2V" | best read as the Li-ion cell's full-charge voltage: the label rates each half's input at 5 V DC 1.5 A and the manual asks for a computer USB port | <span class="tag inferred">INFERRED</span>[^fcc-crr][^um106] |

### Features and host systems

<!-- manuals facts 12-13 -->
The features list: programmable key behavior; programmable RGB backlighting (printed "RBG"); in-built
tenting up to 27°; modular design for additional inputs; a foam-suspended PCB for sound dampening;
dedicated customization software <span class="tag doc">DOC</span>[^um106]. Host systems: Windows 10 and newer, macOS Ventura and
newer, "tested on Ubuntu 24.04 LTS" <span class="tag doc">DOC</span>[^um106].

### What is in the box

<!-- manuals facts 14-16 -->
The lettered box list: A Travel Case; B Naya Create; C Speedlink Dongle ("Wireless dongle ·
NAYA-100-1(Dongle)", in the right-half copy only); D 1m USB Type-C Y-Cable; E Keycap/Switch Puller (one
tool, a wire keycap end and a fork switch end); F Spare/Sample Switches (3x); G Module Spacers (2x)
<span class="tag doc">DOC</span>[^um106]. The Y-cable has two short USB-C ends for the halves and one long USB-C end for the
computer; v1.1.1 lists item D as "Y-Cable/Two USB-C cables" <span class="tag doc">DOC</span>[^um106]. The module spacers are rings
used "to pack empty space" in the travel case, and the manual allows storing the keyboard with modules
attached <span class="tag doc">DOC</span>[^um106].

### Power and charging

<!-- manuals facts 17-20, 22-25 -->
- **Power sources (v1.0.6).** A computer "USB 2.0 or higher port", or a docked module with enough
  charge. Each half's small internal battery keeps it on during a module hot swap but "is not intended
  to power normal operation", and it charges while the keyboard draws power. v1.1.0 asks for a USB 3.0
  port instead <span class="tag doc">DOC</span>[^um106][^man-c].
- **Best practice.** Do not connect the keyboard straight to a wall outlet; charge from a computer's
  USB port ("USB 2.0 5V-1A" in v1.0.6, "USB 3.0 5V-1A" in the v1.1.0 module manuals)
  <span class="tag doc">DOC</span>[^um106][^man-to]. The 5 V DC 1.5 A rating comes from the label artwork, not from the manual text
  <span class="tag doc">DOC</span>[^fcc-crr].
- **Charging modules.** Docked modules charge "if the keyboard is connected to a power source";
  modules charge on a Qi charger "both when docked and when not" <span class="tag doc">DOC</span>[^um106].
- **Sleep.** The keyboard sleeps after 1.5 minutes idle and enters deep sleep after 10 minutes, which
  "will disconnect bluetooth connections"; both are configurable. NayaFlow 1.25.1's own defaults are
  90 s idle and 300 s sleep <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^um106][^man-c][^nc]; see
  [Settings and timing](../protocol/settings.md).
- **Lights.** "When the keyboard is turned ON and has adequate power, the LEDs will light up"
  <span class="tag doc">DOC</span>[^um106].
- **Power switch.** Each half has its own switch "on the side of each keyboard wing" with independent
  power control. The v1.0.6 drawings disagree on which direction is ON (part 1 page 5 shows up = ON,
  part 2 page 3 shows the OFF icon with an upward arrow); v1.1.0 draws slide up = ON and slide down =
  OFF <span class="tag doc">DOC</span>[^um106][^man-c].
- **v1.1.0 additions.** "Create will respect the ON/OFF state even while connected over USB", and "to
  ensure proper pairing between the keyboard halves it is recommended to power ON the left half first"
  <span class="tag doc">DOC</span>[^man-c]. Measured: switching a half OFF while on USB does shut it off, and switching it back ON
  restarts it <span class="tag measured">MEASURED</span> (owner's board, 2026-09-23).

### The module indicator LED

<!-- manuals fact 21 -->

| Module LED | Meaning (v1.0.6 table) |
|---|---|
| blinking red | battery low |
| solid red | a problem with the charging device |
| blinking orange | charging |
| blinking green | charging, close to full |
| solid green | fully charged |
| blinking white | connecting to the keyboard |
| solid white for 2 s | connected and ready |

<span class="tag doc">DOC</span>[^um106] The v1.1.0 module manuals repeat the table and describe a full module as "periodically"
lighting solid green <span class="tag doc">DOC</span>[^man-to]. Module firmware 2.3.3 disabled the battery blink, so the "battery
low" pattern may not appear on current module firmware (see
[Power and batteries](../hardware/power.md#module-recovery-mode-and-the-indicator)).

### Output modes and host slots

<!-- manuals facts 26-32 -->
- **USB output.** Hold Layer 2 (`RA5`) and press Z (`LC4`); v1.1.0 names the Layer 2 keys as `A5`/`H1`
  <span class="tag doc">DOC</span>[^um106][^man-c].
- **Bluetooth output (v1.0.6 text).** Hold Layer 2 and press a number key to pick a device slot; hold
  Layer 2 and press Esc to enter pairing; if the connection attempt fails, the keyboard falls back to
  its previous connection state <span class="tag doc">DOC</span>[^um106].
- **v1.0.6 contradicts itself on the slot count.** Its text says keys 1-5 and one drawing labels a
  fifth device on `LG1`, while another drawing and the Layer 2 table give BT Device 1-4 on
  `LC1`-`LF1`, `LG1` Disabled and `LA1` (the Esc position) BT Clear <span class="tag doc">DOC</span>[^um106]. naya-create-kb's
  "Layer 2 + 1...5" and "Layer 2 + Esc" are the v1.0.6 text, not the later default[^kb-manual].
- **Other v1.0.6 Layer 2 keys.** `LA4` "Speedlink", `LB4` "Connect to Bluetooth", `LC4` "Connect to
  USB" <span class="tag doc">DOC</span>[^um106].
- **v1.1.0 settles the slots.** Layer 2 plus 1-4 selects a slot, and the "5" key (`LG1`) enters pairing
  mode; its Layer 2 table calls `LG1` "BT Clear". The current stock profile in NayaFlow 1.25.1 matches
  this <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^man-c][^nc].
- **v1.1.0 Layer 2 (System), Windows.** `LA5` "Module Force Charge", `LB4` "Output through Wireless",
  `LC4` "Output through USB", `LA1` "Power Button", LED effects on `RG1`-`RD1`, LED colors on
  `RG4`-`RD4`; on macOS `LA5` is "Module Recovery Mode" and `LA1` "Display Sleep" <span class="tag doc">DOC</span>[^man-c].
- **v1.0.6 module controls on Layer 2.** `LA3` "Toggle Scroll Direction" and `LB3` "Cycle Tune Mode";
  host-layout keys `LC5` "To Windows Layout" and `LD5` "To MacOS Layout" <span class="tag doc">DOC</span>[^um106].

### The default keymap

<!-- manuals facts 33-36, 51 -->
- **v1.0.6 base layer.** `LA5` and `RA5` hold Layer 2; `LH4` and `RH4` hold Layer 1; `LH1` Backspace,
  `LH2` Space, `LH3` Enter on the left and `RH1` Enter, `RH2` Space, `RH3` Backspace on the right; both
  wing columns duplicate Tab, Caps Lock and Shift <span class="tag doc">DOC</span>[^um106].
- **v1.1.0 base layer (Windows).** The inner and thumb keys change: `LH1` Enter and `RH1` Backspace,
  each with a Layer 2 hold; `LH3` Backspace and `RH3` Enter; `LA5`, `RA5`, `LH4` and `RH4` keep their
  holds <span class="tag doc">DOC</span>[^man-c].
- **Layer rules (v1.1.0).** Layers stack; a transparent key behaves as if its layer were off; a higher
  layer takes priority over a lower one; layers can be held, set absolutely or toggled; a power cycle
  resets active layers <span class="tag doc">DOC</span>[^man-c].
- **Keycap coordinates.** Every keycap is labeled on its underside with a coordinate: side (L/R),
  column A-H, row 1-5 (`LA1`...`RH4`); the key map lists 37 per half <span class="tag doc">DOC</span>[^um106][^man-c]. See
  [Layout and positions](../hardware/layout.md).
- **Hot swap.** Keycaps and switches are hot-swappable; third-party CPG-1232 switches must have
  0.45 x 0.42 mm pins, larger keycaps have stabilizers, and the PCB may need pushing so the sockets
  line up with the body cutouts <span class="tag doc">DOC</span>[^um106][^man-c].
- **An inconsistency.** The v1.0.6 Layer 1 drawing and table disagree on four right-half keys (`RG3`,
  `RA3`, `RB3`, `RC4`) <span class="tag doc">DOC</span>[^um106].

### Handling: tenting, magnets, docking

<!-- manuals facts 37-39 -->
Tenting goes up to 27° with two hinges per half (the wing hinge and the dock hinge); it is done
powered off with USB and module removed, bending the wing up and pressing the dock down without
pressing on the connection pins <span class="tag doc">DOC</span>[^um106][^man-c]. The two halves attach to each other magnetically
for storage in the travel case <span class="tag doc">DOC</span>[^um106][^man-c]. Docking: align the contacts, let the magnets in the
dock and on the module pull it in, and seat it completely flat for a proper connection "with the data
pins"; to remove, push the module up through the dock cutout with the keyboard held up or tented
<span class="tag doc">DOC</span>[^um106][^man-c][^man-to].

### Safety, storage and disposal

<!-- manuals facts 40-42 -->
The safety text: do not short-circuit the pogo pins, the battery or its cells; the operating range is
0-60 °C (both v1.0.6 and v1.1.0 print "140°C" where 140 °F is meant); small parts are a choking hazard;
do not clean pogo pins with liquids, chemicals or abrasion; use a dry cloth only <span class="tag doc">DOC</span>[^um106][^man-c].
Battery disposal (v1.0.6): remove the switches, screws and hinges, take the circuit board out of the
aluminum body, then detach the battery from the board <span class="tag doc">DOC</span>[^um106]. Storage (v1.1.0): modules left
docked cause a slight power draw that can trigger battery protection; undock them for long storage
<span class="tag doc">DOC</span>[^man-c].

### Regulatory pages

<!-- manuals fact 50 -->
The regulatory part of v1.0.6 carries the FCC Part 15 Class B and two-condition statements, an RF
exposure statement, "FCC SAR - Dongle" (highest reported SAR near the body at 5 mm: 0.08 W/kg), the
ISED license-exempt statements in English and French with an RSS-102 exemption and a 5 mm dongle
distance, a Taiwan RoHS table and a WEEE statement <span class="tag doc">DOC</span>[^um106]. The dongle's own SAR report confirms
the 0.080 W/kg figure; see [Regulatory records](../hardware/regulatory.md).

## What changed after v1.0.6

<!-- summary table built from manuals facts 17, 18, 24, 26-33 -->

| Topic | v1.0.6 | v1.1.0 (and v1.1.1) |
|---|---|---|
| USB port asked for | "USB 2.0 or higher" | USB 3.0 |
| Box item D | 1 m USB Type-C Y-cable | v1.1.0 the same; v1.1.1 "Y-Cable/Two USB-C cables" |
| Pairing key | Layer 2 + Esc (`LA1`) | Layer 2 + "5" (`LG1`) |
| Host slots | text says 1-5, table says 1-4 | 1-4 |
| `LA5` on Layer 2 | not a module key | "Module Force Charge" (Windows), "Module Recovery Mode" (macOS) |
| Inner and thumb keys | `LH1` Backspace, `LH3` Enter | `LH1` Enter with a Layer 2 hold, `LH3` Backspace |
| Power switch drawing | two drawings disagree | slide up = ON |
| Switch on USB | not stated | "Create will respect the ON/OFF state even while connected over USB" |

All rows <span class="tag doc">DOC</span>[^um106][^man-c].

## The module manuals

<!-- manuals facts 44-49 -->
- A module works only when docked, and its behavior depends on the layout stored on the keyboard
  <span class="tag doc">DOC</span>[^man-to][^man-tu][^man-tr].
- **Tune.** The outer ring is the "Crown" and the inner touch surface the "Gesturepad"; the defaults
  are Crown = volume, one finger = scroll, two fingers = brightness and tab, three fingers =
  play/pause, seek and track; some units may ship without the latest configuration <span class="tag doc">DOC</span>[^man-tu].
- **Track.** It ships with a 40 mm ball in ceramic bearings; the ball is loose and falls out if the
  module is held upside down; the defaults are vertical and horizontal = cursor, rotate clockwise =
  scroll down, counterclockwise = scroll up <span class="tag doc">DOC</span>[^man-tr].
- **Touch.** One-finger tap = left click, tap and drag = drag, drag = cursor, two-finger tap = right
  click <span class="tag doc">DOC</span>[^man-to].
- **Printed specifications (v1.1.0).** Tune 1500 mAh, 69 x 69 x 28 mm; Touch 1500 mAh, 75 x 69 x 12 mm;
  Track 700 mAh, 75 x 69 x 34 mm. The FCC samples carry 1000 / 700 / 600 mAh <span class="tag doc">DOC</span>[^man-tu][^man-to][^man-tr][^fcc-crl];
  see [Power and batteries](../hardware/power.md).
- **Haptics.** They are branded "Naya Pulse (Tune Haptic Feedback)" and reprogrammed in NayaFlow; the
  manual points to `naya.tech/getstarted` for the app (not linked: the domain no longer serves Naya's
  material). The same page lists the Float's planned inputs: X, Y and Z axes, pitch, roll, yaw and dial
  rotation <span class="tag doc">DOC</span>[^man-c].

## Troubleshooting and the help center

<!-- manuals facts 43, 54, 57 -->
The v1.1.0 troubleshooting section says to power the left half on before the right, to make sure
the two halves are paired together "using the device manager", that a module that will not charge may
need the Recovery Mode keybinding, and that long docking can drain a module until its battery
protection makes it unchargeable until recovered <span class="tag doc">DOC</span>[^man-c][^man-tu][^man-tr]. The manual gives the
dongle one troubleshooting line ("Create isn't connecting over speedlink": move closer, avoid
interference, "Ensure the speedlink dongle is properly seated") and no pairing procedure or LED
description; "Speedlink" appears five times in the whole v1.0.6 manual <span class="tag doc">DOC</span>[^um106].

The help center's page titles survive in the Wayback index, their bodies do not: among them "Force
Flashing Naya Modules", "Module no longer turns ON: Battery Recovery", "Naya Create not typing after
update", "Clearing Keymap Data" and "Language Settings" (English QWERTY and Japanese JIS only)
<span class="tag doc">DOC</span>[^wb-help] ([details](../open-questions.md)).

## Where the manuals disagree with other vendor text

<!-- manuals facts 52-53 -->
Every version asks users to keep the firmware up to date with NayaFlow <span class="tag doc">DOC</span>[^um106][^man-c]. NayaFlow
1.25.1's own update and pairing instructions, however, say Y-cables "are known to cause issues" and
ask for two direct USB-C to USB-C cables, which contradicts the Y-cable setup the manual describes
<span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^nc]; see [Power and batteries](../hardware/power.md#cables-and-hubs).

## Safety

The manuals' pogo-pin warning applies everywhere on this site: do not short or bridge the dock
contacts and do not clean them with liquids <span class="tag doc">DOC</span>[^um106]. Their wall-outlet rule stands: charge from a
computer's USB port <span class="tag doc">DOC</span>[^um106].

## Open questions

- <span class="tag open">OPEN</span> Whether 212 x 118 x 18 mm and 1.4 kg are per half or per pair; the size fits one half by the label outline <span class="tag inferred">INFERRED</span> ([details](../open-questions.md#oq-h28)).
- <span class="tag open">OPEN</span> Whether retail keycaps have shine-through legends, and which default keymap matches the factory state of boards shipped before v1.1.0 ([details](../open-questions.md#oq-h29)).
- <span class="tag open">OPEN</span> The four v1.1.0 PDFs and the v1.1.1 manual have no public archive yet.

## Sources

[^fcc-crl]: FCC ID 2BQ4V0825CRL (left half): exhibits on the FCC record ([FCC EAS search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm), grantee code 2BQ4V; mirror [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL)). Short codes are explained on [Regulatory records](../hardware/regulatory.md#how-to-cite-an-fcc-photo).
[^fcc-crr]: FCC ID 2BQ4V0825CRR (right half), including the label artwork; mirror [fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR).
[^fcc-dg]: FCC ID 2BQ4V0825DG (Speedlink dongle); mirror [fccid.io/2BQ4V0825DG](https://fccid.io/2BQ4V0825DG).
[^um106]: Naya Create User Manual Version 1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits 1-5 ([fccid.io](https://fccid.io/2BQ4V0825CRR)); "UM1 p3" means part 1, PDF page 3.
[^man-c]: Naya Create User Manual Version 1.1.0, vendor PDF `Naya_Create_UserManual.pdf` (27 pages, dated 2025-11-10), read 2026-09-23.
[^man-to]: Naya Touch User Manual Version 1.1.0, vendor PDF `Naya_Touch_UserManual.pdf`.
[^man-tu]: Naya Tune User Manual Version 1.1.0, vendor PDF `Naya_Tune_UserManual.pdf`.
[^man-tr]: Naya Track User Manual Version 1.1.0, vendor PDF `Track_UserManual_100_8c81323d-033e-4b06-a3c7-bdbfe61fab55.pdf`.
[^nc]: NayaFlow 1.25.1 (Windows): user-interface strings, stock profile and NayaCore 6.11.0 strings (static reading).
[^kb-manual]: naya-create-kb, [official manual claims](https://nemezzizz.github.io/naya-create-kb/device/manual/) (third party).
[^ks-camp]: Kickstarter campaign page with its Specs Sheet and FAQ, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023).
[^ks-13]: Kickstarter update 13, [2024-05-08](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4061393).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^wb-help]: Wayback Machine index of the vendor's help center ([captures](https://web.archive.org/web/*/help.naya.tech/*)), to 2026-09-08; titles only.

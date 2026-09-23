# Board inventory

This is the entry page of the hardware section: what the FCC filings show and do not show, how the
parts were read, a block diagram in words for each device, every board with its silkscreen, the
confirmed part numbers, and the earlier public readings that the photos correct. The one thing to
know: each half carries a single Nordic nRF52840 (not an nRF52811 with a separate USB chip), and the
full parts list with every reading is on [Parts list](parts.md).

!!! note "At a glance"
    - Source: 54 of the 71 public FCC exhibits under grantee 2BQ4V (every one with hardware content); schematics, block diagrams and operational descriptions are permanently confidential.
    - Every photographed unit is a pre-production sample received on 2025-06-20.
    - 20 boards appear in the filings; 17 show a legible name.
    - Halves and dongle: Nordic nRF52840 (CKAA, build D0); modules: ST STM32F411CEU6.
    - Mainboards are revision V13; V11 is the wing board's revision.

## What the filings show

<!-- index facts 1-5 -->
The hardware facts on these pages come from 54 FCC exhibit PDFs under grantee code 2BQ4V (19 for the
left half 2BQ4V0825CRL, 21 for the right half 2BQ4V0825CRR, 14 for the dongle 2BQ4V0825DG) out of 71
public exhibits: internal and external photos, BTL test and RF-exposure reports, Boen antenna
documents, both halves' and the dongle's label artwork, the confidentiality letters and the user
manuals <span class="tag doc">DOC</span>[^eas]. Every public exhibit with hardware content is now held; the 17 not fetched are
administrative (attestation, US-agent, authority and power-of-attorney letters) and the dongle SAR
report's appendices A to C (calibration data) <span class="tag doc">DOC</span>[^eas].

The block diagram, schematics and operational description are the only confidential exhibits, for all
three IDs. Naya's confidentiality letters (2025-08-06 for CRL, 2025-08-04 for CRR and DG) ask for
exactly these three with no short-term hold on anything else, so they are permanent and will not
become public; no schematic exists in public <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl][^fcc-crr][^fcc-dg] (also noted by
naya-create-kb[^kb-hardware]).

Every unit in the photos is a pre-production sample the lab received on 2025-06-20; no firmware
version is printed anywhere in the filings, and retail boards may carry later revisions
<span class="tag doc">DOC</span>[^fcc-crl]. The Tune, Touch, Track and cable photos are the same image files in both halves'
filings (left-filing attachment page N equals right-filing page N-3 for modules, N-1 for cables), so a
pair of left and right citations for a module part is one photograph of one sample; the half, dongle
and test-setup photos are unique to their filing <span class="tag doc">DOC</span>.

## How the parts were read

<!-- index facts 6-7, 42 -->
Twenty-five extraction passes read every exhibit page from the embedded JPEGs and the report text
layers; sixteen adversarial passes then re-read each cited crop blind and gave each row a verdict
(confirmed, corrected, unverifiable, refuted). The result was 215 main rows (199 confirmed, 16
corrected), 48 unverifiable readings, 50 rejected readings and 27 open questions. The 16 exhibits
obtained on 2026-09-23 add 7 rows (222 in all) and settle one unconfirmed reading and one open question
(47 and 26 left); those 7 rows had one extraction pass, not the blind re-read <span class="tag doc">DOC</span>. See
[Parts list](parts.md).

Legibility is marked after every marking as [clear], [partial] or [illegible]; a "candidate" part
number is reasoning and never appears in the Part column <span class="tag doc">DOC</span>.

**Citation codes.** `CRL IP3 p20` means FCC ID 2BQ4V0825CRL, exhibit "Internal Photos 3", lab
attachment page 20 ("Page 20 of 48"); report pages use the report's own numbering. Codes for the
exhibits obtained on 2026-09-23: `CRL LLOC` (left label location: p1 left sheet, p2 right sheet),
`CRL MPE`, `CRL SETUP`, `DG EP`, `DG LBL`, `DG SAR` (and its appendix D), `DG SETUP`, `CL`
(confidentiality letters). The key table that maps each code to its exhibit is on
[Regulatory records](regulatory.md#how-to-cite-an-fcc-photo) <span class="tag doc">DOC</span>. naya-create-kb's coordinates (such as
`fullres p6-Im1` or `CRL-view-4`) point into its author's research repository, not to the FCC record.

## Block diagram in words

<!-- index facts 8-10 -->
- **Half.** An nRF52840 SoC (radio, native USB, QSPI host) with a 32 MHz crystal; a Winbond serial NOR
  flash on the QSPI bus; a PCB antenna; a USB-C port; a 50 mAh cell with a charger-class part and two
  DC-DC converters (identities unread); 24 per-key RGB LEDs on the mainboard. Flex links run to the
  wing board (10 keys, 10 LEDs, the 7-LED light bar, the power switch) and to the dock board (3 thumb
  keys and their LEDs), which links to the pogo board carrying the 8 dock contacts <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl][^fcc-crr].
  The roles of the unmarked power parts are inferred. Details on [The keyboard half](half.md).
- **Module.** An STM32F411CEU6 MCU with a 16 MHz crystal; a Maxic MT5705 Qi receiver on a flat coil; an
  SG Micro SGM41523 single-cell charger fed through Schottky diodes from the dock 5 V or the Qi output;
  a battery pack; an 8-contact dock block wired to the MCU's UART and boot pin; plus per-module input
  hardware (Touch: a CST3640 touch controller; Tune: a touch/LED disc and a haptic dial actuator;
  Track: two optical sensors, four buttons and a vibration motor). Tune and Touch add an SGM62117
  buck-boost converter <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl]. The topology is inferred; see [Tune](tune.md),
  [Touch](touch.md), [Track](track.md) and [Module dock](dock.md).
- **Dongle.** One nRF52840 (the only IC-class part), a 32 MHz crystal, an RGB status LED, a 10 mm PCB
  antenna and a USB-A plug; no external flash, PA/LNA, battery or charger <span class="tag doc">DOC</span>[^fcc-dg]. See
  [Speedlink dongle](dongle.md).

## Boards

<!-- index facts 11-26 -->
Twenty boards appear in the filings; 17 show a legible name (two of them only in part) and 3 show none
<span class="tag doc">DOC</span>.

| Board | Silkscreen | Part number, revision, thickness | Exhibit | Evidence |
|---|---|---|---|---|
| Left half mainboard | `Create_L_KB_20250220_V13`, the same string on both faces, circled `L` | V13, 1.0 mm (`T=1.0MM`) | CRL IP1 p8, p9 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Right half mainboard | `Create_R_KB_20250221_V13`, circled `R` | V13, 1.0 mm | CRR IP1 p6 | <span class="tag doc">DOC</span>[^fcc-crr] |
| Left wing | `Create_L_Wing_20250206_V11`, fab stamp `25 15` | V11, 1.0 mm | CRL IP1 p11, p12 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Right wing | `Create_R_` ... `0250206_V11` (middle hidden under a QR label; full name inferred from the left twin) | V11 | CRR IP1 p9 | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crr] |
| Left and right dock (thumb-key) boards | `Create_L_Dock_20241120_V09`, `Create_R_Dock_20241120_V09` | V09, 1.0 mm | CRL IP2 p16; CRR IP1 p12 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Left pogo board | `Create_L_PogoPin_20250109_V10` | V10, 0.6 mm | CRL IP2 p15 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Right pogo board | name under a QR sticker | - | CRR IP2 p13 | <span class="tag doc">DOC</span>[^fcc-crr] |
| Dongle | `B0K17_Dongle_20241106_V01` (the second character is the digit zero in the report's text layer) | V01 | DG test report p10; DG IP p4, p5 | <span class="tag doc">DOC</span>[^fcc-dg] |
| Tune main board (the ring) | `Tune_MB_20250227_V09`, stamp `25 12` | `408-06032-000`, 0.8 mm | CRL IP3 p19, p21 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Tune touch/LED disc | `Tune_touch 20240926 V00`, about 45 mm, under the glass | V00 | CRL IP3 p22; CRL IP4 p23 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Tune T-shaped sub-board | no legible name (a micro slide switch is the leading reading; too small for USB-C) | - | CRL IP2 p18; CRL IP4 p24 | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl] |
| Touch main board | `Touch_MB_20250227_V10`, round, about 44 mm | `408-06025-000`, 1.0 mm | CRL IP5 p29-p31 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Touch sensor board | `Touch_touch_20250106_V02`, stamp `25 12` | V02 | CRL IP6 p35-p36 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Touch pogo board | name partly hidden (`Tou`...`in` / `20`...`V0?`), stamp `25 10` | - | CRL IP5 p32 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Track main board (the ring) | `Track_MB_20250305_V13`, stamp `25 15` | `408-06028-000`, 1.0 mm | CRL IP7 p44-p46 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Track sensor boards | `SensorL_20241125_V09` and `SensorR_20241125_V09` (each photographed front and back: two boards, not four) | V09 | CRL IP6 p38-p39 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Track pogo board | `Track_Pogo_Pin_20241122_V08` | V08 | CRL IP6 p38, p40 | <span class="tag doc">DOC</span>[^fcc-crl] |
| Track dock interposer | no name | - | CRL IP6 p40 | <span class="tag doc">DOC</span>[^fcc-crl] |

Every test report declares the two V13 mainboard strings as the hardware version (text layers
verified 2026-09-23), so the filed mainboard is V13; V11 is the wing's revision <span class="tag doc">DOC</span>[^fcc-crl]. This
corrects naya-create-kb's exhibit page, which calls the mainboard V11[^kb-exhibits]. The
`408-060xx-000` numbers of the three module main boards look like one series <span class="tag inferred">INFERRED</span>. The `25 NN` stamps
on several boards read as fabrication year and week <span class="tag inferred">INFERRED</span>; no board house is named.

## Confirmed part numbers

<!-- index facts 27-35 -->

| Part | Where | Evidence |
|---|---|---|
| Nordic nRF52840, package code CKAA (WLCSP), build code D0 | both halves (`U2`) and the dongle (`U1`); marking on the left half `N528…` / `CKAAD0` / `2301ME` (crop re-viewed 2026-09-23) | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl][^fcc-dg] |
| Winbond serial NOR flash, leadless USON/WSON class (part number and capacity unread) | both halves (`U1`) | <span class="tag doc">DOC</span> CRR IP1 p8; CRL IP1 p9[^fcc-crr] |
| Boen RF0400A PCB antenna | halves | <span class="tag doc">DOC</span> CRL ANT[^fcc-crl] |
| Boen RF0401A PCB antenna | dongle | <span class="tag doc">DOC</span> DG OTA report[^fcc-dg] |
| Kailh CPG-1232 (PG1232 "Choc Mini") low-profile switches, 0.45 x 0.42 mm pin variant | 37 per half plus 3 spares | <span class="tag doc">DOC</span> UM1 p3; UM3 p2[^um106] |
| ST STM32F411CEU6 (UFQFPN48), Maxic MT5705 Qi receiver, SG Micro SGM41523 charger | all three modules | <span class="tag doc">DOC</span>[^fcc-crl] |
| SG Micro SGM62117 buck-boost | Tune and Touch | <span class="tag doc">DOC</span>[^fcc-crl] |
| Hynitron CST3640 capacitive touch controller | Touch sensor board; the Tune disc's controller reads `CST3…` (CST3640 is a candidate only) | <span class="tag doc">DOC</span> CRL IP6 p35[^fcc-crl] |
| Commodity parts: MMBT3904-class NPN (`1AM`), B5819W-class Schottky (`SL`), 1N4148W-class diodes (`T4`), 100 uF 6.3 V tantalum (`J107`), `YC32.0` 32 MHz crystals (halves, dongle), `YC16.0` 16 MHz crystals (modules) | various | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> (code-to-part decodes inferred) |
| Cells: `FH301217` 3.7 V 50 mAh (each half), `FH 202030` 1000 mAh (Tune), `FH364046` and `FH364045` 700 mAh (Touch), `QS801630 1S2P` 600 mAh made of two `QS801630` 300 mAh cells (Track); the makers (prefixes FH, QS) are not identified | see [Power](power.md) | <span class="tag doc">DOC</span>[^fcc-crl] |
| Model numbers: `NAYA-800-1(NAYA-CREATE)` for both halves, `NAYA-100-1(Dongle)` for the dongle | labels, reports | <span class="tag doc">DOC</span>[^fcc-crr][^fcc-dg] |

The full index, with every row it points to, is on [Parts list](parts.md#part-number-index).

## Still unidentified

<!-- index facts 36-37 -->
The biggest identification gaps are the half's power-management ICs, every LED part (addressable
4-pad RGB, WS2812/SK6812 class inferred), every connector and the spring-pin block maker, the Track's
optical sensors, the Tune's haptic driver and actuator, the wing slide switch and the USB-C receptacle
class <span class="tag doc">DOC</span>. There is no second microcontroller in a half: no second MCU-class part appears on either
face of either mainboard; a few small power parts are unidentified, and the nRF52840's native USB makes
a separate USB chip unnecessary <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl][^fcc-crr]. This contradicts naya-create-kb's "unknown
USB MCU" and its note that the component side appears in no filing[^kb-hardware]. See
[Parts list](parts.md#unconfirmed-readings).

## Earlier public readings the photos correct

<!-- index facts 38-41; errata R-01..R-16 -->
naya-create-kb (commit 7668067) published several readings that the photos and report text layers
correct. They are listed neutrally here and on [Parts list](parts.md#earlier-public-readings-the-photos-correct).

| Earlier reading | What the filings show | Evidence |
|---|---|---|
| Half SoC is an nRF52811 (`N5281?`, `N52811`) | nRF52840, package CKAA; CKAA is not an nRF52811 code | <span class="tag doc">DOC</span> see [The keyboard half](half.md#the-soc-is-an-nrf52840) |
| A second, unknown USB chip; the nRF has no USB; images exceed its 192 KB flash | no second MCU-class IC on either face; the nRF52840 has native USB 2.0 full speed and 1 MB flash | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> |
| Half mainboard `Create_L_KB 20250220_V11` | V13 on both faces; V11 is the wing | <span class="tag doc">DOC</span> |
| Dongle `BOK17_Dongle` (letter O) | `B0K17`, digit zero in the text layer | <span class="tag doc">DOC</span> |
| Tune module ring `Tune_Touch_20240926_V00` | the ring is `Tune_MB_20250227_V09`; `Tune_touch` is the disc | <span class="tag doc">DOC</span> |
| Track module ring `Y08_06025_20250227_V00` | `Track_MB_20250305_V13`; `06025` is the Touch board's number with `408` misread | <span class="tag doc">DOC</span> |
| Touch front end "SGMicro 4T523DF" | `41523DF` is the SGM41523 charger on all three modules; the Touch's controller is a CST3640 | <span class="tag doc">DOC</span> |
| Dock "VBUS/USB on test pads" | UART, boot and power contacts; no `D+`/`D-` on any dock contact | <span class="tag doc">DOC</span> |
| Touch pack `FH202030` 1000 mAh | that pack is the Tune's | <span class="tag doc">DOC</span> |
| Track pack `FH364046` 700 mAh | that cell is the Touch's; the Track has a 600 mAh 1S2P pack | <span class="tag doc">DOC</span> |
| A separate cylindrical "ICR" 300 mAh cell | a pouch cell inside the Track pack; no fourth module battery | <span class="tag doc">DOC</span> |
| One grant date, 2025-08-29, for all filings | 2025-08-26 (CRL), 2025-08-29 (CRR), 2025-09-03 (DG) | <span class="tag doc">DOC</span> |
| The SRD report is a second grant | the same FCC ID: a second report inside the same grant | <span class="tag doc">DOC</span> |
| "nRF Connect SDK 5.1.0" | `nrfconnect-setup-5.1.0-x64`, the nRF Connect for Desktop installer | <span class="tag doc">DOC</span> |
| "Clicky" switches | the manual states no switch type | <span class="tag doc">DOC</span> |
| "Aluminum + polycarbonate" body | body, dock and wing aluminum; keycaps polycarbonate | <span class="tag doc">DOC</span> |

naya-create-kb's own photos agree with these readings once read closely:

- Its `mainboard-v13.jpg` is itself a V13 board, which agrees with the V13 reading, and its file name
  already says so <span class="tag doc">DOC</span>[^kb-hardware].
- Its `nrf52811.jpg` shows a package marking (not a die marking) beginning `N528`, with the rest of
  line 1 hidden by the foam edge, then `CKAAD0` and `2301ME`; CKAA is an nRF52840 package code
  <span class="tag doc">DOC</span>[^kb-hardware]. Reading `2301` as January 2023 assumes the year-week convention; that is plausible
  but not confirmed from Nordic's marking document <span class="tag inferred">INFERRED</span>.
- Its captions agree in outline: `half-matrix.jpg` shows the body switch plate with red low-profile
  switches plus the bay bracket and a ring frame with rectangular blocks; by the owner's paper-clip test
  the magnets are the 2 features beside the contacts and 4 blocks around the bay, while the 5 blocks on
  the metal bay bracket did not attract a clip <span class="tag measured">MEASURED</span> (2026-09-23). `module-ring-pcb.jpg` is most likely
  the Tune main board and its touch/LED disc; `module-teardown.jpg` shows the half's cell, the half's
  pogo board and dock (thumb-key) board, and an opened Tune with its blue `FH 202030` pack <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^kb-hardware][^kb-power].

## Safety

Opening a half or a module exposes Li-ion cells: do not puncture or short them, as the manual says
<span class="tag doc">DOC</span>[^um106]. The general safety notes are on the [home page](../index.md).

## Open questions

- <span class="tag open">OPEN</span> Whether retail boards match the filed revisions (V13 mainboard, V11 wing, V09 dock, V10 pogo) ([details](../open-questions.md#oq-h01)).
- <span class="tag open">OPEN</span> The right pogo board's name; the Tune T-shaped sub-board and the Track interposer have none ([details](../open-questions.md#oq-h35)).
- <span class="tag open">OPEN</span> The nRF52840 silicon revision behind build code D0 (Revision 2 by the pattern, inferred) ([details](../open-questions.md#oq-h05)).
- <span class="tag open">OPEN</span> Everything in the unconfirmed readings and open questions of the [Parts list](parts.md#open-hardware-questions).

## Sources

[^eas]: FCC OET Equipment Authorization System, [grantee search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm) for grantee code 2BQ4V: exhibit lists read 2026-09-23.
[^fcc-crl]: FCC ID 2BQ4V0825CRL (left half; the module photos are in both halves' filings): exhibits on the FCC record, mirror [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL).
[^fcc-crr]: FCC ID 2BQ4V0825CRR (right half): mirror [fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR).
[^fcc-dg]: FCC ID 2BQ4V0825DG (Speedlink dongle): mirror [fccid.io/2BQ4V0825DG](https://fccid.io/2BQ4V0825DG).
[^um106]: Naya Create User Manual Version 1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits ([fccid.io](https://fccid.io/2BQ4V0825CRR)).
[^kb-hardware]: naya-create-kb, [hardware deep dive](https://nemezzizz.github.io/naya-create-kb/device/hardware/) with its photo captions (third party).
[^kb-exhibits]: naya-create-kb, [exhibit inventory](https://nemezzizz.github.io/naya-create-kb/device/exhibits/) (third party).
[^kb-power]: naya-create-kb, [power architecture](https://nemezzizz.github.io/naya-create-kb/device/power/) (third party).

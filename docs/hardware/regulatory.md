# Regulatory records

This page lists every regulatory record for the Create and its dongle (FCC, ISED, Japan MIC, Korea KC,
Taiwan BSMI, the Bluetooth SIG), what each FCC exhibit contains, the marks on the labels, and the
citation codes this site uses so a reader can find any photo on the public record. The one thing to
know: there are exactly three FCC IDs, one per half and one for the dongle, granted on three different
days; the modules have no FCC ID of their own.

!!! note "At a glance"
    - Grantee code 2BQ4V (Naya B.V.): `2BQ4V0825CRL` (left half), `2BQ4V0825CRR` (right half), `2BQ4V0825DG` (dongle).
    - Grants: 2025-08-26 (CRL, two grant lines), 2025-08-29 (CRR), 2025-09-03 (DG); nothing filed since.
    - ISED: `34320-0825CRL`, `34320-0825CRR`, `34320-0825DG`; MIC `219-257017` / `219-257016`; KC `R-R-NBv-0825CRL` / `...CRR`.
    - 71 public exhibits, 54 held; only the block diagram, schematics and operational description are confidential, permanently.
    - One Bluetooth SIG listing (311198) for the keyboard.

## FCC grantee and IDs

<!-- regulatory facts 1-7 -->
The FCC grantee code for Naya B.V. is `2BQ4V`. The official record is the FCC OET Equipment
Authorization System (search for grantee code 2BQ4V; exhibits are served at
`apps.fcc.gov/eas/GetApplicationAttachment.html?id=<id>` to a browser session); fccid.io mirrors the
exhibits <span class="tag doc">DOC</span>[^eas][^fccid].

| FCC ID | Device | Grant lines | Final action date | ISED number | ISED approval |
|---|---|---|---|---|---|
| `2BQ4V0825CRL` | left half | two: 2402-2480 MHz and 2404-2480 MHz | 2025-08-26 | `34320-0825CRL` | 2025-09-11 |
| `2BQ4V0825CRR` | right half | 2402-2480 MHz | 2025-08-29 | `34320-0825CRR` | 2025-09-08 |
| `2BQ4V0825DG` | Speedlink dongle | 2402-2480 MHz | 2025-09-03 | `34320-0825DG` | 2025-09-08 |

All rows <span class="tag doc">DOC</span>[^eas][^ised]. There are exactly three FCC IDs, with four grant lines, all "Original
Equipment"; there is no ID for the Tune, Touch, Track, a dock or a charger <span class="tag doc">DOC</span>[^eas]. The three IDs were
granted on different days.
The second CRL line (2404-2480 MHz) fits the 2 Mbps "SRD" report, whose data channels start at 2404 MHz
<span class="tag inferred">INFERRED</span>. Each test report is marked "This report concerns: Original Grant" <span class="tag doc">DOC</span>.

The test lab is BTL Inc. (Dongguan): FCC registration `747969`, designation `CN1377`, A2LA certificate
7130.01 <span class="tag doc">DOC</span> CRR BLE p1, p8. The manufacturer and factory of record on all three reports is Dongguan Boen
Intelligent Technology Co., Ltd. (Dongguan, Guangdong); the applicant is Naya B.V., Groningen, the
Netherlands <span class="tag doc">DOC</span>[^fccid]. Samples were received on 2025-06-20; the halves were tested 2025-06-26 to
2025-07-22 and the dongle 2025-06-26 to 2025-07-16 <span class="tag doc">DOC</span> CRL SRD p1.

## Test reports

<!-- regulatory facts 8-19 -->

| FCC ID | Report | Issued | What it covers |
|---|---|---|---|
| CRL (project 2506C291) | BLE `BTL-FCCP-1-2506C291` R01 | 2025-08-27 | 1M, 2M, coded 125k |
| CRL | "SRD" `BTL-FCCP-2-2506C291` R01 | 2025-08-27 | 2 Mbps only |
| CRL | RF exposure `BTL-FCCP-3-2506C291` R00 | 2025-08-15, never revised | SAR-exclusion calculation |
| CRR (project 2506C430) | `BTL-FCCP-1-2506C430` R01 (BLE), `-2-` R01 (SRD), `-3-` R01 (RF exposure) | 2025-08-27; the R00 versions of 2025-08-15 were superseded to change the antenna gain | as CRL |
| DG (project 2506C290) | `BTL-FCCP-1-2506C290` R00 | 2025-08-12 | 2 Mbps only |
| DG | antenna report `BTL-OTA-1-2506C290` R00 | tested and issued 2025-07-14 | RF0401A gain and efficiency |
| DG | SAR report `BTL-FCC SAR-1-2506C290` R00 | issued 2025-08-12, tested 2025-07-12 to 07-22 | SAR at 5 mm |

All rows <span class="tag doc">DOC</span>[^fccid].

- **Rule part.** 47 CFR 15.247 (digital transmission system), 2402-2480 MHz, GFSK, for all three <span class="tag doc">DOC</span>.
- **The halves' BLE reports** test 1 Mbps, 2 Mbps and coded 125 kbps (S=8); maximum peak output 9.30 dBm
  (left, 2M) and 8.36 dBm (right, 2M); maximum average 7.14 / 7.25 dBm (1M) <span class="tag doc">DOC</span> (text layers verified
  2026-09-23).
- **The "SRD" report** in each half's filing carries the same FCC ID as the BLE report: it is a second
  15.247 report inside the same grant, not a second grant. It
  tests 2 Mbps only, on data channels 2404-2478 MHz plus the advertising channels 2402, 2426 and 2480 MHz;
  left peak 9.27 dBm, average 4.35 dBm; right peak 8.33 dBm, average 5.57 dBm <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>. Its channel table,
  test modes and bandwidths are the same as the dongle's report, and the halves' RF-exposure reports list
  this "2.4G SRD" mode as a separate row beside BLE <span class="tag doc">DOC</span>. So both halves' FCC filings carry a
  separate "2.4G SRD" 2 Mbps test report besides BLE, and the dongle's SAR report names only "2.4G SRD";
  the manual says "Speedlink Connection: Using Bluetooth v5.4" <span class="tag doc">DOC</span>[^um106]. Every mode tested
  uses the Bluetooth LE channel plan and GFSK, so the filings do not say whether "2.4G SRD" is BLE at
  2 Mbps or a vendor link on the same radio, for the halves or the dongle
  <span class="tag inferred">INFERRED</span>. Whether shipping firmware ever uses the SRD mode, on the halves or the dongle, is
  <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-c14); see also
  [Speedlink dongle](dongle.md#is-it-bluetooth)).
- **The dongle** is filed at 2 Mbps only, maximum output 8.97 dBm, with power setting 8 / 7 / 8 at 2402 /
  2442 / 2480 MHz <span class="tag doc">DOC</span> DG RF p10, p11 (verified 2026-09-23).
- **Software.** Every sample declares `Naya_Temp_Flash_Pair.exe` as its EUT software; the lab's channel
  and power tool is `nrfconnect-setup-5.1.0-x64`, the installer name of Nordic's nRF Connect for Desktop
  5.1.0 (not the nRF Connect SDK); power setting 8 on every channel and PHY for the halves. No firmware
  toolchain or firmware version is stated anywhere in the filings <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> (text layers). The dongle's SAR sample ran "2.4G SRD
  engineering testing software" for continuous transmission at 100 % duty <span class="tag doc">DOC</span> DG SAR p7, p23.
- **Hardware versions declared** on every report: `Create_L_KB_20250220_V13, Create_R_KB_20250221_V13` for
  the halves and `B0K17_Dongle_20241106_V01` for the dongle <span class="tag doc">DOC</span>. See [Board inventory](index.md#boards).
- **Antennas filed.** Halves: Boen RF0400A, PCB, no connector, 0.8 dBi. Dongle: Boen RF0401A, PCB, no
  connector, 3.11 dBi <span class="tag doc">DOC</span> CRL BLE p11; DG RF p10. See [Speedlink dongle](dongle.md#the-board).
- **RF exposure of the halves.** KDB 447498 SAR-exclusion calculations, "No SAR evaluation required".
  Right half (R01): 1.646 (BLE, 7.25 dBm) and 1.118 ("2.4G SRD", 5.57 dBm) against a limit of 3,
  reproduced with 5 mm at 2402 MHz. Left half (R00): 1.630 (BLE, 7.14 dBm) and 0.858 (2.4G SRD,
  4.35 dBm), reproduced with 5 mm at 2480 MHz and unrounded milliwatts; it files the antenna at 0.59 dBi,
  where the R01 reports use 0.8 dBi <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> CRR MPE p3-p4; CRL MPE p3-p4.
- **RF exposure of the dongle.** The SAR report finds a highest reported 1-g SAR of 0.080 W/kg at 5 mm
  (2402 MHz, horizontal-down, against 1.6 W/kg), across five USB orientations; the manual repeats
  0.08 W/kg and gives an ISED 5 mm minimum distance <span class="tag doc">DOC</span> DG SAR p7, p26[^um106].

## Exhibits and confidentiality

<!-- regulatory facts 20-22, 34-35 -->
Confidential are exactly the block diagram, schematics and operational description for each ID. Naya's
letters (CRL 2025-08-06; CRR and DG 2025-08-04) request confidentiality under 47 CFR 0.457 and 0.459 for
these three only, as trade secrets, with no short-term request for anything else, so they are permanent
and will not be released <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fccid].

The FCC lists 71 exhibits, all public: CRL 22, CRR 24, DG 25. We hold 54 (CRL 19, CRR 21, DG 14): every
photo, report, label, antenna document and manual, and the three confidentiality letters. The dongle's
five manual files are byte-identical to the right half's v1.0.6 manual, and the left half's and the
dongle's test-setup photos repeat photos inside the test reports <span class="tag doc">DOC</span>[^eas]. Not fetched, on purpose: 17
administrative or calibration exhibits (attestation, US-agent, authority and power-of-attorney letters
for the three IDs; the dongle SAR report's appendices A to C) <span class="tag doc">DOC</span>[^eas].

There is no FCC filing under 2BQ4V after 2025-09-03 (no Naya Connect filing and no permissive changes) as
of 2026-09-23 <span class="tag doc">DOC</span>[^eas]. Our copies of the exhibits match files served elsewhere: four manual parts match manuals.plus
document hashes <span class="tag doc">DOC</span>.

## Other regimes and marks

<!-- regulatory facts 23-27 -->

| Regime | Left half | Right half | Dongle | Evidence |
|---|---|---|---|---|
| ISED Canada (company 34320) | `34320-0825CRL`, HVIN `NAYA-800-1(NAYA-CREATE) L` | `34320-0825CRR`, HVIN `... R` | `34320-0825DG`, HVIN `NAYA-100-1(Dongle)` | <span class="tag doc">DOC</span>[^ised] |
| Japan MIC (boxed `R` mark) | `219-257017` | `219-257016` | `XXX-XXXXX` placeholder only | <span class="tag doc">DOC</span> |
| Korea KC | `R-R-NBv-0825CRL` | `R-R-NBv-0825CRR` | KC logo, no number | <span class="tag doc">DOC</span> |
| Taiwan BSMI | `R45625` over "RoHS" | same | none | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> |
| Taiwan NCC-style mark | 17-character `X` placeholder | same | same placeholder | <span class="tag doc">DOC</span> |
| CE, UKCA, WEEE | yes | yes | CE and WEEE, no UKCA | <span class="tag doc">DOC</span> |
| RCM, VCCI | yes | yes | no | <span class="tag doc">DOC</span> |
| c-UL "Energy Verified" | yes | yes | yes | <span class="tag doc">DOC</span> |
| "ENERGY VERIFIED" with an N in an ellipse | yes | yes | no | <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> |

The PMNs registered with ISED are "Ergonomic detachable wireless mechanical keyboard" and "Wireless
dongle", and each number is also on its label artwork <span class="tag doc">DOC</span>[^ised]. The certification body behind MIC code 219 is not
identified. The BSMI number most likely identifies the importer rather than the product <span class="tag inferred">INFERRED</span>. Both half
labels carry a CNS 15663-style restricted-substance table (cable, circuit assemblies, plastic, metal and
rubber parts; every cell compliant; no battery row) <span class="tag doc">DOC</span>[^um106]. The issuer of the N-in-ellipse mark is
not identified (Nemko's logo is a shape-only candidate) <span class="tag inferred">INFERRED</span> ([details](../open-questions.md#oq-h26)). CE
and UKCA are vector graphics, which is why a text search misses them; an earlier "CE / UKCA not found"
note was wrong <span class="tag doc">DOC</span>.

## The label

<!-- regulatory facts 28-30, 39 -->
Label text (both halves): the FCC ID and IC number on one line; the maker's name and city; the equipment
name in Traditional Chinese and English ("Ergonomic detachable wireless mechanical keyboard"); "Model
Name: NAYA-800-1(NAYA-CREATE)" and the HVIN with its side suffix (` L` on the left label, ` R` on the
right; ISED registers the HVINs with the suffix); a serial-number field (template not reproduced);
"Rating: 5V⎓1.5A"; and the six-line FCC Part 15 two-condition statement on the body plate <span class="tag doc">DOC</span>[^fccid][^ised].

The label artwork is a 1:1 laser-engraving sheet per half ("Create-L" and "Create-R Engraving Reference
Sheet", 2025-08-20): the regulatory block sits on the wing's underside plate rotated 90°, and the logo on
the body plate 47.97 mm from the wing seam. The left filing's "Label Location" exhibit holds both sheets;
the right filing's label exhibit is the same export cut to the right page (inferred from the PDF
metadata). The two sheets differ only in title, FCC ID, IC, KC and MIC numbers, HVIN suffix, the L/R
circle and mirroring <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> CRL LLOC p1-p2; CRR LBL. The photographed right-half sample does not show the
Part 15 statement engraved; it probably carried an earlier engraving <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span> CRR EP p3.

The dongle's label artwork ("Dongle" engraving sheet, 2025-07-25, 12.55 x 12.00 mm) carries
"Manufactured Date: Jun. 2025" and "Rating: 5V⎓30mA" besides its IDs <span class="tag doc">DOC</span> DG LBL; details on
[Speedlink dongle](dongle.md#power-label-and-rf-exposure).

## Modules and certification

<!-- regulatory fact 31 -->
Modules have no FCC ID: the Touch and Track base labels print empty `FCC ID:` and `IC:` fields and
placeholder certification numbers, the maker's name and `Input: 5V⎓500mA`; their bases carry CE, UKCA,
WEEE, KC, VCCI and other marks. The modules are photographed inside both halves' filings <span class="tag doc">DOC</span> CRL IP4 p27;
CRL IP6 p37. The modules have no radio of their own; see [Module dock](dock.md), [Touch](touch.md)
and [Track](track.md).

## Bluetooth SIG

<!-- regulatory facts 32-33 -->
There is one listing for Naya B.V.: listing 311198, "NAYA TECH/NAYA CREATE", declaration `R076016`,
design `Q372162`, qualified 2025-09-19, model `NAYA-800-1(NAYA-CREATE)`, description "Ergonomic
detachable wireless mechanical keyboard, USB, 2.4G, BLE three working modes ..."; its core-spec field
reads 5.1, and it references Zephyr's host subsystem and Zephyr's nRF52 controller designs. There is no
dongle or Naya Connect listing <span class="tag doc">DOC</span>[^sig]. The controller reference is Zephyr's own link layer for the
nRF52 family, not Nordic's SoftDevice; it does not separate nRF52811 from nRF52840 and, being a reused
design, does not date the shipped stack <span class="tag inferred">INFERRED</span>.

## Every FCC exhibit

The full exhibit lists of all three filings, as the FCC's Equipment Authorization System shows them
(checked 2026-09-27). Every exhibit is public; none is held back beyond the three permanently
confidential documents named above. Each link opens the FCC's own copy in a browser (the FCC refuses
scripted downloads, so open them by hand). Exhibit ids are the FCC's; the same ids appear in
fccid.io's page addresses. <span class="tag doc">DOC</span>

### 2BQ4V0825CRL (left half, 22 exhibits)

[Exhibit list on apps.fcc.gov](https://apps.fcc.gov/oetcf/eas/reports/ViewExhibitReport.cfm?mode=Exhibits&RequestTimeout=500&calledFromFrame=N&application_id=jIWCdeXJEqFicUI5GRjHhQ%3D%3D&fcc_id=2BQ4V0825CRL)

| Exhibit | Type | FCC attachment |
|---|---|---|
| [US AGENT Letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611340) | Attestation Statements | `8611340` |
| [Attestation Statements 2.911 d 5](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611341) | Attestation Statements | `8611341` |
| [Authority Letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611289) | Cover Letter(s) | `8611289` |
| [Confidentiality Letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611290) | Cover Letter(s) | `8611290` |
| [External Photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611334) | External Photos | `8611334` |
| [Label Location](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611291) | ID Label/Location Info | `8611291` |
| [Internal Photos_1](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611295) | Internal Photos | `8611295` |
| [Internal Photos_2](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611296) | Internal Photos | `8611296` |
| [Internal Photos_3](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611297) | Internal Photos | `8611297` |
| [Internal Photos_4](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611298) | Internal Photos | `8611298` |
| [Internal Photos_5](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611331) | Internal Photos | `8611331` |
| [Internal Photos_6](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611332) | Internal Photos | `8611332` |
| [Internal Photos_7](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611333) | Internal Photos | `8611333` |
| [MPE Report](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611339) | RF Exposure Info | `8611339` |
| [Antenna Specification](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611342) | Test Report | `8611342` |
| [BLE Test Report_1](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8620606) | Test Report | `8620606` |
| [BLE Test Report_2](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8620604) | Test Report | `8620604` |
| [SRD Test Report](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8620605) | Test Report | `8620605` |
| [Test Setup Photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611335) | Test Setup Photos | `8611335` |
| [User Manual_1](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611292) | Users Manual | `8611292` |
| [User Manual_2](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611293) | Users Manual | `8611293` |
| [User Manual_3](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8611294) | Users Manual | `8611294` |

### 2BQ4V0825CRR (right half, 24 exhibits)

[Exhibit list on apps.fcc.gov](https://apps.fcc.gov/oetcf/eas/reports/ViewExhibitReport.cfm?mode=Exhibits&RequestTimeout=500&calledFromFrame=N&application_id=cBLDdNl2gRWC4RpJ20egKA%3D%3D&fcc_id=2BQ4V0825CRR)

| Exhibit | Type | FCC attachment |
|---|---|---|
| [Attestation Section 2.911(d)(5)(i)&(ii)](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621869) | Attestation Statements | `8621869` |
| [US Agent letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621870) | Attestation Statements | `8621870` |
| [confidentiality letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621871) | Cover Letter(s) | `8621871` |
| [POA letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621872) | Cover Letter(s) | `8621872` |
| [external Photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621879) | External Photos | `8621879` |
| [label](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621878) | ID Label/Location Info | `8621878` |
| [Internal photos 01](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621887) | Internal Photos | `8621887` |
| [Internal photos 02](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621888) | Internal Photos | `8621888` |
| [Internal photos 03](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621889) | Internal Photos | `8621889` |
| [Internal photos 04](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621890) | Internal Photos | `8621890` |
| [Internal photos 05](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621891) | Internal Photos | `8621891` |
| [Internal photos 06](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621892) | Internal Photos | `8621892` |
| [Internal photos 07](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621893) | Internal Photos | `8621893` |
| [RF exposure report](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621877) | RF Exposure Info | `8621877` |
| [antenna specification](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621873) | Test Report | `8621873` |
| [BLE test report 01](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621874) | Test Report | `8621874` |
| [BLE test report 02](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621875) | Test Report | `8621875` |
| [SRD 2.4G test report](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621876) | Test Report | `8621876` |
| [test setup photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621880) | Test Setup Photos | `8621880` |
| [User manual 01](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621882) | Users Manual | `8621882` |
| [User manual 02](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621883) | Users Manual | `8621883` |
| [User manual 03](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621884) | Users Manual | `8621884` |
| [User manual 04](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621885) | Users Manual | `8621885` |
| [User manual 05](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8621886) | Users Manual | `8621886` |

### 2BQ4V0825DG (Speedlink dongle, 25 exhibits)

[Exhibit list on apps.fcc.gov](https://apps.fcc.gov/oetcf/eas/reports/ViewExhibitReport.cfm?mode=Exhibits&RequestTimeout=500&calledFromFrame=N&application_id=egYdoL8uID%2BougMlzBctwg%3D%3D&fcc_id=2BQ4V0825DG)

| Exhibit | Type | FCC attachment |
|---|---|---|
| [Attestation Section 2.911(d)(5)(i)&(ii)](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635702) | Attestation Statements | `8635702` |
| [US Agent letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635703) | Attestation Statements | `8635703` |
| [confidentiality letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635704) | Cover Letter(s) | `8635704` |
| [POA letter](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635705) | Cover Letter(s) | `8635705` |
| [External photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635708) | External Photos | `8635708` |
| [label](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635706) | ID Label/Location Info | `8635706` |
| [Internal photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635707) | Internal Photos | `8635707` |
| [SAR test report](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635758) | RF Exposure Info | `8635758` |
| [SAR Appendix A. SAR Plots of System Verification](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635759) | RF Exposure Info | `8635759` |
| [SAR Appendix B. SAR Plots of SAR Measurement](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635760) | RF Exposure Info | `8635760` |
| [SAR Appendix C. Calibration Certificate_1](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635761) | RF Exposure Info | `8635761` |
| [SAR Appendix C. Calibration Certificate_2](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635762) | RF Exposure Info | `8635762` |
| [SAR Appendix C. Calibration Certificate_3](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635763) | RF Exposure Info | `8635763` |
| [SAR Appendix C. Calibration Certificate_4](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635764) | RF Exposure Info | `8635764` |
| [SAR Appendix C. Calibration Certificate_5](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635765) | RF Exposure Info | `8635765` |
| [SAR Appendix C. Calibration Certificate_6](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635766) | RF Exposure Info | `8635766` |
| [antenna specification](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635756) | Test Report | `8635756` |
| [RF test report](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635757) | Test Report | `8635757` |
| [Test setup photos](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635709) | Test Setup Photos | `8635709` |
| [SAR Appendix D. Photographs of the Test Set-Up](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635767) | Test Setup Photos | `8635767` |
| [User manual part1](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635710) | Users Manual | `8635710` |
| [User manual part2](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635711) | Users Manual | `8635711` |
| [User manual part3](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635712) | Users Manual | `8635712` |
| [User manual part4](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635713) | Users Manual | `8635713` |
| [User manual part5](https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=8635714) | Users Manual | `8635714` |

## How to cite an FCC photo

<!-- regulatory facts 36-38 -->
`CRL IP3 p20` means FCC ID 2BQ4V0825CRL, exhibit "Internal Photos 3", lab attachment page 20 ("Page 20
of 48"). Module and cable photos are the same image files in both halves' filings (left attachment page N
= right page N-3 for modules, N-1 for cables): cite one, and do not count a left/right pair as two samples
<span class="tag doc">DOC</span>. FCC exhibits are public records: facts from them can be stated freely and photos reused after
scrubbing (blur QR and 2D codes, serial-number fields, lab sample tags and handwriting; cut fresh from the
embedded JPEGs) <span class="tag doc">DOC</span>.

| Code | FCC ID | Exhibit | Pages |
|---|---|---|---|
| `CRL IP1`-`IP7` | 2BQ4V0825CRL | Internal Photos 1-7 (48 pages, BTL project 2506C291) | IP1 p1, p5-p12; IP2 p13-p18; IP3 p19-p22; IP4 p23-p28; IP5 p29-p34; IP6 p35-p41; IP7 p42-p48 |
| `CRL EP` | 2BQ4V0825CRL | External Photos | p2-p4 |
| `CRL BLE`, `CRL SRD` | 2BQ4V0825CRL | test reports BTL-FCCP-1 and -2-2506C291 R01 | report page |
| `CRL MPE` | 2BQ4V0825CRL | RF exposure report BTL-FCCP-3-2506C291 R00 | report page |
| `CRL ANT` | 2BQ4V0825CRL | Antenna specification, Boen RF0400A ver1.1 | PDF page |
| `CRL LLOC` | 2BQ4V0825CRL | Label Location (p1 left sheet, p2 right sheet) | p1, p2 |
| `CRL SETUP` | 2BQ4V0825CRL | Test setup photos | page |
| `CRL UM1`-`UM3` | 2BQ4V0825CRL | User Manual parts 1-3 (image-only copy of v1.0.6) | PDF page |
| `CRR IP1`-`IP7` | 2BQ4V0825CRR | Internal photos 01-07 (47 pages, BTL project 2506C430; dongle on p44-p47) | IP1 p5-p12 ... IP7 p42-p47 |
| `CRR EP` | 2BQ4V0825CRR | External Photos | p1 cover, p2-p4 |
| `CRR BLE`, `CRR SRD`, `CRR MPE` | 2BQ4V0825CRR | test reports BTL-FCCP-1/-2/-3-2506C430 R01 | report page |
| `CRR ANT` | 2BQ4V0825CRR | Antenna specification RF0400A ver1.1 (same content as CRL ANT) | PDF page |
| `CRR LBL` | 2BQ4V0825CRR | "Create-R Engraving Reference Sheet" (label artwork) | p1 |
| `UM1`-`UM5` | 2BQ4V0825CRR | User manual v1.0.6, parts 1-5 (text layer) | PDF page |
| `DG IP` | 2BQ4V0825DG | Internal photos | p4, p5 |
| `DG EP` | 2BQ4V0825DG | External photos | p1-p3 |
| `DG RF` | 2BQ4V0825DG | Test report BTL-FCCP-1-2506C290 R00 | report page |
| `DG OTA` | 2BQ4V0825DG | Antenna test report BTL-OTA-1-2506C290 R00 (Boen RF0401A) | report page |
| `DG SAR`, `DG SAR-D` | 2BQ4V0825DG | SAR report BTL-FCC SAR-1-2506C290 R00 and its appendix D (set-up photographs) | report page |
| `DG LBL` | 2BQ4V0825DG | Label artwork | p1 |
| `DG SETUP` | 2BQ4V0825DG | Test setup photos | page |
| `CL` | all three | Confidentiality letters | p1 |

Every exhibit is listed under its FCC ID on the FCC record and on fccid.io[^eas][^fccid].

## Safety and privacy

None physical. Privacy rule for this page: no serial numbers, serial-number templates, lab sample numbers
or lab staff names from the reports or the labels are reproduced, although they exist in the exhibits.

## Open questions

- <span class="tag open">OPEN</span> The issuer of the N-in-ellipse energy mark; the MIC certification body 219 ([details](../open-questions.md#oq-h26)).
- <span class="tag open">OPEN</span> The SIG listing's "2.4G" mode, and why its core-spec field says 5.1 while the manual says 5.4 ([details](../open-questions.md#oq-h37)).
- <span class="tag open">OPEN</span> The Tune and Track base part-number digits ([details](../open-questions.md#oq-h19)).
- <span class="tag open">OPEN</span> Whether shipping firmware ever uses the "2.4G SRD" mode certified in the halves' and the dongle's filings, and whether that mode is BLE ([details](../open-questions.md#oq-c14)).

## Sources

[^eas]: FCC OET Equipment Authorization System, [grantee search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm) for grantee code 2BQ4V: grant lines, final action dates and exhibit lists, read in a browser 2026-09-23.
[^fccid]: fccid.io mirrors of the three IDs: [2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL), [2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR), [2BQ4V0825DG](https://fccid.io/2BQ4V0825DG).
[^ised]: ISED Canada Radio Equipment List, company number 34320 ([search](https://sms-sgs.ic.gc.ca/equipmentSearch/searchRadioEquipments?lang=en)), read 2026-09-23.
[^sig]: Bluetooth SIG qualification listing 311198 ([listing search](https://qualification.bluetooth.com/Listings/Search)), read 2026-09-23.
[^um106]: Naya Create User Manual Version 1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits, part 5 (regulatory statements) ([fccid.io](https://fccid.io/2BQ4V0825CRR)).

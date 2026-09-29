# About

How the material on this site was gathered and checked, what each evidence tag stands for, which
sources it rests on, what it deliberately does not publish, its license, who to credit, and how to
send a correction. The one thing to know: every fact carries a tag and a source, and where our
evidence and another site's differ, both are shown with their firmware, host and date.

## Who wrote this and how

The research was done with AI tooling that walked the repositories built over the last few weeks
while building OpenFlow (the OpenFlow code and its test and capture records, the create-legacy-firmware release
archive, Create Companion, and the public nayactl repository), with the hardware measurements made by
the owner on the owner's own boards <span class="tag doc">DOC</span>.

**The site.** It is Create-knowledge-base, built with MkDocs Material and published on GitHub Pages
from [its repository](https://github.com/create-collective/Create-knowledge-base).

**Boards and period.** A daily-use board (both halves on 3.41.0; a Tune on module firmware 2.3.3 and a
Touch on 2.1.2 by mid-September 2026), a donor board on 3.28.7 with modules on 2.1.2, and a board
flashed both ways between 3.35.4 and 3.41.0 on 2026-09-20. Pages say "measured on the owner's board,
<firmware>, <date>"; no serial numbers or addresses are given. Where a measurement is already public,
the page cites the public record instead: the flashes of 2026-09-20 are written up in create-legacy-firmware's
`FLASHING-PROCEDURE.md`, section "Measured on hardware, both halves (2026-09-20)"[^nh-hw]. The work ran
from 2026-08-31 to 2026-09-23 (first captures 2026-09-01; first firmware flash 2026-09-20)
<span class="tag measured">MEASURED</span>.

**Methods.** USB captures of NayaFlow talking to the keyboard (USBPcap on Windows); live reads and
writes through OpenFlow's backend and small probe scripts; static reading of the vendor installers
(strings with a 2-character minimum, data tables with file offsets, the JavaScript bundles, and the
symbols and code of the macOS NayaCore builds; no decompiled code is published); the FCC exhibits read
page by page, with the official registers (FCC EAS for grantee `2BQ4V`, ISED's Radio Equipment List
for company 34320) checked in a browser on 2026-09-23; the vendor's manuals, release notes (stable and
beta), the Kickstarter campaign page, FAQ and all 26 updates (read in full on 2026-09-23), vendor
answers on Reddit (as archived text: the permalinks could not be opened live), the Bluetooth SIG
listing and patents <span class="tag doc">DOC</span>.

**A verification pass** (2026-09-23) took every fact that another source reported and we had not yet
checked, and tried to confirm it from our own material: the public NayaFlow installers (including the
macOS arm64 and x86_64 NayaCore builds), the stock NayaFlow databases, our own USB captures, and the
published code and raw data of the community KB. Most such facts are now tagged with our own evidence;
the rest stay REPORTED with the check they need listed on [Open questions](open-questions.md).

## Evidence rules

Every fact carries a tag; every MEASURED fact names firmware and date; REPORTED marks a third-party
statement we have not checked, with its source; where two observations differ both are kept with their
firmware and setup; later evidence replaces earlier notes, and replaced claims are shown as corrections.

| Tag | Meaning |
|---|---|
| <span class="tag measured">MEASURED</span> | observed on a real board, with firmware and date |
| <span class="tag static">STATIC</span> | read from the vendor's released software (NayaFlow, NayaCore, firmware images) |
| <span class="tag doc">DOC</span> | vendor documents, manuals, FCC and ISED filings, Kickstarter, release notes |
| <span class="tag inferred">INFERRED</span> | our reasoning; the reason is given |
| <span class="tag reported">REPORTED</span> | a third party states it and we have not verified it; the source is named |
| <span class="tag open">OPEN</span> | unknown; linked to its row on [Open questions](open-questions.md) |

## Sources

| Source | What it gave us | How it is cited |
|---|---|---|
| `NayaTech/NayaFlow-releases` and `NayaTech/NayaFlow-beta-releases` | every installer and release note | release and file, for example "NayaFlow 1.25.1, NayaCore, strings" |
| FCC filings for `2BQ4V0825CRL`, `2BQ4V0825CRR`, `2BQ4V0825DG`; the FCC EAS grant records and the ISED Radio Equipment List entries for the same devices | hardware, radios, ratings | FCC ID, exhibit title and page |
| The vendor's v1.1.0 manuals (Create, Touch, Tune, Track) | stated behavior and specifications | by version, archived copies only ([Manuals](product/manuals.md)) |
| The Kickstarter campaign page (story, Specs Sheet, Risks and challenges, FAQ) and its 26 updates | the vendor's stated plans and the manufacturing history | update number and date |
| Vendor answers on Reddit | a few technical statements | comment permalink, as archived text, marked not live-verified |
| Bluetooth SIG listing 311198; patent WO2025188184A1; Canadian industrial designs 229065-229069 | identity and design records | by number |
| create-legacy-firmware (github.com/create-collective/create-legacy-firmware) | the release archive, firmware library and flashing procedure | file and commit |
| nayactl (github.com/Qonfused/nayactl) | the first public protocol decoding | file, pull request or issue number |
| naya-create-kb (nemezzizz.github.io/naya-create-kb) | live macOS findings and a NayaCore disassembly | page name, for REPORTED facts and credit |
| createflow-dongle (github.com/mediaandmerch/createflow-dongle) | third-party Bluetooth measurements | file |
| Create Companion (github.com/create-collective/create-companion) | measurements of what modules send | file |
| OpenFlow (github.com/create-collective/openflow) | the tool most measurements were made with | file and release |
| The Wayback Machine | the vendor's own website | archived URL |

**Links to the vendor's website.** The vendor's old domain now belongs to another company, so its old
URLs no longer lead to Naya's material. This site cites the vendor's web pages (shop, help center,
product pages) only through Wayback Machine copies and carries no live link to that domain; the vendor's
GitHub release repositories stay live sources.

## What we do not publish

- Decompiled function bodies or instruction listings (names, offsets and behavior only).
- Ways to extract keys from a keyboard, or any method to bypass its protections.
- Token literals found in vendor bundles.
- Serial numbers, Bluetooth addresses and UUIDs from anyone's board; private messages; marketing images.
- Vendor firmware images. create-legacy-firmware, public on purpose, is OpenFlow's firmware library.

## License

- Pages: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code snippets and the files under
  `assets/code/`: MIT.
- Vendor material stays the vendor's: manuals are linked and cited, UI and release-note text is quoted
  only in short snippets, and firmware and marketing images are not reproduced. FCC exhibits are public
  records and are cited by FCC ID, exhibit and page.
- create-legacy-firmware is licensed Apache-2.0, matching OpenFlow; that license covers the repository's own
  documents, manifests and tools, not the vendor firmware images or installers it archives.

## Credits

| Project | License | What this site owes it |
|---|---|---|
| nayactl, by Cory Bennett (Qonfused) | Apache-2.0 | the first public decoding of the frame, the XOR checksum, and the category and opcode map; the module address map (with pull request #2) and the module battery units (pull request #5); a pull request #6 contributor's measurements of the LED brightness ceiling |
| naya-create-kb, by Aleksei Ilin (NemeZZiZZ) | no license file | live macOS findings and an arm64 disassembly of NayaCore (the ZMQ event list, the clear-all-data chain, the host maps, the factory format, LED recovery sequences, never-send lists); credited wherever it states a fact first |
| createflow-dongle, by mediaandmerch | Apache-2.0 | third-party Bluetooth measurements on 3.41 (the GATT table, the `0x1234` pipe, the 212-byte HID report map, the security level) and the stock dongle's behavior |
| Create Companion | MIT | measurements of what modules send to the host, and the per-application host engine |

Also used: ShortcutMapper data (MIT, inside OpenFlow's reference data) and the Wayback Machine.

**Relationship to naya-create-kb.** This site is independent of naya-create-kb and copies none of its
text or code. Facts both sites state are credited to it where it stated them first, and where our
evidence differs both observations are shown with firmware, host and date.

**Dating a board.** Which firmware a board shipped with depends on its batch and on the last NayaFlow
that updated it; the release history and the beta-only firmware are on [History](software/history.md)
and [Firmware versions](firmware/versions.md).

## Corrections

Open an issue or a pull request on this site's repository. Give both halves' `fe/1002` versions, the
module firmware, the host OS, the date and the raw bytes; leave out serial numbers and Bluetooth
addresses. Safety corrections are handled first.

## Sources

[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).

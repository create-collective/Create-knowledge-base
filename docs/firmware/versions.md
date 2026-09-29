# Firmware versions

This page lists every published keyboard and module firmware, which NayaFlow release carried it on
the stable and the beta channel, how a half reports its version, what each version changed
according to the vendor, and which versions are in the field. The one thing to know: 3.41.0 is the
last keyboard firmware Naya published, but boards run older and beta-only versions too, and one half
can silently miss an update, so read the version of **both** halves before following any recipe.

!!! note "At a glance"
    - Last published firmware: keyboard 3.41.0 and module bundle 2.3.3 (NayaFlow 1.25.0, 2026-07-17).
    - 25 stable releases (2025-03-19 to 2026-07-21) and 16 beta releases; every image is archived in create-legacy-firmware.
    - Three keyboard firmwares shipped only on the beta channel: 3.39.4, 3.40.0 and 3.40.4.
    - Images carry no version of their own; versions come from the vendor's notes, app constants and the device.
    - Read `fe/1002` on each half (and the right half through the left) instead of assuming.

## How versions are written and read

The vendor writes the keyboard firmware series two ways: one release note says
`v3.28.7 -> v3.29.1`, another `v0.3.29.1 -> v0.3.31.1`. 3.41.0 and 0.3.41.0 are the same version
<span class="tag doc">DOC</span>[^cl-310]. This site writes three parts everywhere else; on the wire a half reports its firmware
in four parts with a leading zero, so 3.41.0 arrives as 0.3.41.0 (`fe/1002` reply `00 00 03 29 00`)
and the module bundle 2.3.3 as 0.2.3.3 (`de/100a` reply `00 00 02 03 03`; `de/1008` carries the same
four version bytes).

**Reading a half's firmware.** `fe/1002` GET_FW_VERSION with params `00` answers
`00 00 03 29 00` for 3.41.0: the status byte `00`, then the vendor's leading zero, major, minor and
patch. `00 00 03 23 04` is 3.35.4 <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20). The nayactl maintainer's board
answers `00 00 03 1e 01`, which is 3.30.1 <span class="tag reported">REPORTED</span>[^nx-pr5] (raw data checked: the bytes decode to 3.30.1
by the same encoding). nayactl prints the version without the
leading zero ("3.41.0"). A sixth byte `38` shown after the version on some pages is the frame's XOR
checksum (`10 ^ 02 ^ 00 ^ 00 ^ 03 ^ 29 ^ 00 = 38`), not data <span class="tag inferred">INFERRED</span>. The frame layout is on
[Transport](../protocol/transport.md) and the command on [Command map](../protocol/commands.md).

**Module firmware** is a 2.x.y series. `de/100a` MODULE_FILE_FW_VERSION, sent to the
**left** half, reads the version of the module bundle the keyboard stores: `00 00 02 03 03` is 2.3.3.
The right half never answers it, because it holds no module store. `de/1008` reads a docked module's
own running firmware on either half <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-16). Details on
[Module firmware](modules.md#where-the-keyboard-keeps-the-bundle).

The MCUboot header of every image carries the placeholder version `1.2.3+4`, so the
versions on this page come from the vendor's release notes and, from NayaFlow 1.25.0, from two app
constants: `NAYA_CREATE_FW_VERSION` "3.41.0" and `NAYA_MODULE_FW_VERSION` "2.3.3". NayaFlow's
`/api/info/system` field `createFWVersion` is this bundled value, not something the device reported
<span class="tag static">STATIC</span>[^fh][^nc].

NayaCore grades a device's firmware as NotReady, NotFound, Legacy, OutOfDate, UpToDate or
Future, and it parses four-part versions (`fw_version#N.N.N.N`) <span class="tag static">STATIC</span>[^nc].

## Where firmware was published

The stable channel is the vendor's GitHub repository `NayaTech/NayaFlow-releases`:
25 releases from v0.0.1 (2025-03-19) to v1.25.1 (2026-07-21) with 264 assets (about 21.5 GB). All of
them are mirrored in create-legacy-firmware with checksums: 264 of 264 downloaded, and on verification 208 were
digest-checked, 56 size-checked only (they carry no published digest), none missing and none bad.
14 of the 25 releases carry release notes <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span>[^mf][^cl].

Firmware only ever shipped inside NayaFlow. The vendor's component repositories
(NayaCore, Touch, Track, Tune, Float) answer 404 publicly, no Create firmware repository name was
ever found, and NayaFlow's own update check never resolved: it sent an unsubstituted build
placeholder as its GitHub token and got HTTP 401 <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nc].

create-legacy-firmware groups the releases into four eras by what they bundle <span class="tag static">STATIC</span>[^fh]:

| Era | Releases | Firmware resources |
|---|---|---|
| dvt | 0.0.1 to 0.0.2 | `fwl.bin`, `fwr.bin` |
| dial | 0.1.0 to 1.6.10 | `kb_fwl.bin`, `kb_fwr.bin`, `d_fw.bin` |
| modules | 1.11.0 to 1.21.0 | keyboard images plus the `FlashMemory.bin` module bundle |
| gen-split | 1.25.0 to 1.25.1 | generation A and B keyboard images plus the bundle |

## The stable releases

The table gives, for each of the 25 stable releases, the publication date, NayaCore
version, keyboard firmware, the first 8 hex digits of the plaintext SHA-256 of the left and right
images (generation A; generation B in brackets) and the module firmware <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^mf][^cl][^fh].
"INF" marks a value inferred from the neighboring notes; "same" means the same images as the row
above.

| Release | Published | NayaCore | Keyboard firmware | Images left / right | Module firmware |
|---|---|---|---|---|---|
| 0.0.1 | 2025-03-19 | `naya_core_fw_service` | unknown | `b942c177` / `47ab8461` | none |
| 0.0.2 | 2025-03-19 | `naya_core_fw_service` | unknown (= 0.0.1) | same | none |
| 0.1.0 | 2025-05-01 | `naya_core_fw_service` | unknown | `ce6d82b9` / `066ebb1c` | none (`d_fw.bin`) |
| 0.1.1 | 2025-05-02 | `naya_core_fw_service` | unknown (= 0.1.0) | same | none (`d_fw.bin`) |
| 1.3.8 | 2025-06-13 | `naya_core_fw_service` | unknown | `ce51a353` / `31ceec1a` | none (`d_fw.bin`) |
| 1.3.11 | 2025-06-15 | same | unknown | same | none (`d_fw.bin`) |
| 1.6.4 | 2025-07-13 | same | unknown | same | none (`d_fw.bin`) |
| 1.6.5 | 2025-07-14 | same | unknown | same | none (`d_fw.bin`) |
| 1.6.10 | 2025-07-24 | same | unknown | same | none (`d_fw.bin`) |
| 1.11.0 | 2025-09-07 | `naya_core_project` | unknown | `83100f7b` / `ec1bbca4` | bundle, version unknown |
| 1.11.8 | 2025-09-12 | same | unknown | `e3a7afc4` / `93b050dc` | same |
| 1.11.9 | 2025-09-12 | same | unknown (= 1.11.0 images) | `83100f7b` / `ec1bbca4` | same |
| 1.11.10 | 2025-09-15 | same | unknown (= 1.11.8 images) | `e3a7afc4` / `93b050dc` | same |
| 1.11.11 | 2025-09-19 | same | unknown | `73587852` / `e1577ee8` | same |
| 1.14.3 | 2025-10-02 | 5.5.1 (INF) | 3.28.6 (INF) | `8c926ca7` / `baa94b1d` | 2.1.1 |
| 1.14.5 | 2025-10-03 | 5.5.2 | 3.28.7 | `f52aec47` / `fee82f0e` | 2.1.2 |
| 1.15.0 | 2025-11-07 | 5.8.1 | 3.29.1 (Linux: 3.28.7) | `99e6f8b2` / `ce0f1317` | 2.2.0 |
| 1.15.1 | 2026-01-06 | 5.8.1 (INF) | 3.29.1 (Linux: 3.28.7) | same | 2.2.0 |
| 1.17.2 | 2026-02-18 | 6.1.5 | 3.31.1 (Linux: 3.28.7) | `1b259d25` / `90f98e4d` | 2.3.2 |
| 1.17.3 | 2026-02-18 | 6.1.5 | 3.31.1 (Linux: 3.28.7) | same | 2.3.2 |
| 1.19.1 | 2026-04-03 | 6.4.1 | 3.35.4 | `036059b2` / `959fbae1` | 2.3.2 |
| 1.20.0 | 2026-04-15 | 6.6.1 | 3.35.4 | same | 2.3.2 |
| 1.21.0 | 2026-04-21 | 6.6.1 (INF) | 3.35.4 | same | 2.3.2 |
| 1.25.0 | 2026-07-17 | 6.11.0 | 3.41.0 | `479e89ba` / `2abb2695` (B: `07dd2523` / `87f63fd3`) | 2.3.3 |
| 1.25.1 | 2026-07-21 | 6.11.0 (INF) | 3.41.0 | same | 2.3.3 |

Which keyboard firmware a release carried is unknown for 0.0.1 to 1.11.11: the notes are
silent and the header holds only the placeholder. From 1.14.3 on: 3.28.6 in 1.14.3 (inferred from the
next note's "from" version), 3.28.7 in 1.14.5, 3.29.1 in 1.15.0 and 1.15.1, 3.31.1 in 1.17.2 and
1.17.3, 3.35.4 in 1.19.1 to 1.21.0, and 3.41.0 in 1.25.0 and 1.25.1 <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^cl][^fh].

NayaCore versions come from the notes: 5.5.2 (1.14.5), 5.8.1 (1.15.0), 6.1.5 (1.17.2 and
1.17.3), 6.4.1 (1.19.1), 6.6.1 (1.20.0), 6.11.0 (1.25.0). The notes do not state them for 1.14.3,
1.15.1, 1.21.0 and 1.25.1; the neighbors suggest 5.5.1, 5.8.1, 6.6.1 and 6.11.0 <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^cl].

The 1.11.x line flip-flopped between two builds before 1.11.11: 1.11.9 re-shipped
1.11.0's keyboard images and 1.11.10 re-shipped 1.11.8's <span class="tag static">STATIC</span>[^fh].

The Linux NayaCore of 1.15.0, 1.15.1, 1.17.2 and 1.17.3 embedded the 1.14.5 images
(keyboard 3.28.7, module 2.1.2) while Windows and macOS shipped newer ones, so a Linux user of those
releases would have been offered 3.28.7 <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>[^fh].

NayaCore moved out of `app.asar` in 1.19.1 (on macOS to
`NayaFlow.app/Contents/core/NayaCore.app/`). It sat inside the asar from 1.14.3 to 1.17.3, and the
1.11.x service `naya_core_project` sat in `app.asar.unpacked` <span class="tag static">STATIC</span>[^fp-binary]. More on the host
side is on [History](../software/history.md).

## Distinct keyboard images

The stable channel carries 13 distinct left and right pairs of generation A plus one
generation-B pair, 26 keyboard images in all <span class="tag static">STATIC</span>[^fh]. Sizes are `img_size` (see
[Images](images.md#the-three-sizes)); hashes are the first 8 hex digits of the plaintext SHA-256.

| Releases | Keyboard firmware | `img_size` left / right | Plaintext hash left / right |
|---|---|---|---|
| 0.0.1 to 0.0.2 | unknown | 285 392 / 218 256 | `b942c177` / `47ab8461` |
| 0.1.0 to 0.1.1 | unknown | 313 392 / 235 296 | `ce6d82b9` / `066ebb1c` |
| 1.3.8 to 1.6.10 | unknown | 352 256 / 239 184 | `ce51a353` / `31ceec1a` |
| 1.11.0 and 1.11.9 | unknown | 356 848 / 242 704 | `83100f7b` / `ec1bbca4` |
| 1.11.8 and 1.11.10 | unknown | 358 016 / 243 312 | `e3a7afc4` / `93b050dc` |
| 1.11.11 | unknown | 358 496 / 243 840 | `73587852` / `e1577ee8` |
| 1.14.3 | 3.28.6 (inferred) | 359 200 / 244 224 | `8c926ca7` / `baa94b1d` |
| 1.14.5 | 3.28.7 | 359 312 / 244 224 | `f52aec47` / `fee82f0e` |
| 1.15.0 to 1.15.1 | 3.29.1 | 361 632 / 244 336 | `99e6f8b2` / `ce0f1317` |
| 1.17.2 to 1.17.3 | 3.31.1 | 304 448 / 218 064 | `1b259d25` / `90f98e4d` |
| 1.19.1 to 1.21.0 | 3.35.4 | 312 272 / 220 688 | `036059b2` / `959fbae1` |
| 1.25.0 to 1.25.1, generation A | 3.41.0 | 328 880 / 226 000 | `479e89ba` / `2abb2695` |
| 1.25.0 to 1.25.1, generation B | 3.41.0 | 328 880 / 226 000 | `07dd2523` / `87f63fd3` |

Full hashes are in create-legacy-firmware's per-release `manifest.json` files.

The oldest archived images are those of 0.0.1 and 0.0.2 (`fwl.bin` 285 392, `fwr.bin`
218 256), from the pre-production era, not those of 0.1.1 <span class="tag static">STATIC</span>[^fh].

naya-create-kb's six size rows are correct, and we confirmed them against the archive:
0.1.1 313 392 / 235 296; 1.3.11 352 256 / 239 184 (the same images ship from 1.3.8 to 1.6.10);
1.11.11 358 496 / 243 840; 1.15.1 361 632 / 244 336; 1.21.0 312 272 / 220 688; 1.25.1 328 880 /
226 000 <span class="tag static">STATIC</span>[^fh][^kb-versions]. Its table comes from its maintainer's own carve of six
releases (15 images). Those 15 images are byte-identical to the corresponding create-legacy-firmware images: the
MD5 prefixes in the maintainer's published file names match the MD5 of the MCUboot image part of ours
(checked 2026-09-23) <span class="tag static">STATIC</span>. Also reported by naya-create-kb.

The images shrank at 3.31.1 (NayaFlow 1.17.2): left 361 632 to 304 448, right 244 336 to
218 064. 3.35.4 (1.19.1 to 1.21.0) is larger again, 312 272 / 220 688 <span class="tag static">STATIC</span>[^fh]. 3.31.1 is also the
firmware that retired the engineering text channel (SystemCDC); a link between the two is a guess
<span class="tag inferred">INFERRED</span>[^cl-310].

Generation-B (`_64`) images ship only with 3.41.0, in 1.25.0 and 1.25.1 <span class="tag static">STATIC</span>[^fh]. What
generation B is: [Images](images.md#flash-generations-a-and-b).

## Module firmware versions

Module firmware ships in every stable release from 1.11.0 as `FlashMemory.bin`. By
release: 1.11.x unknown (the bundle has no VERSION file yet), 2.1.1 in 1.14.3, 2.1.2 in 1.14.5, 2.2.0
in 1.15.0 and 1.15.1, 2.3.2 in 1.17.2 to 1.21.0, and 2.3.3 in 1.25.0 and 1.25.1 <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^fh][^cl].

There are six distinct module bundles (resource hash prefixes `fc354e74`, `5d4b036f`,
`d893f6fd`, `51d9d08e`, `84deccbf`, `97d94e9e`); the 2.3.2 bundle did not change from 1.17.2 to
1.21.0 <span class="tag static">STATIC</span>[^fh].

The 175 136-byte image of 0.1.0 to 1.6.10 is `d_fw.bin`, an MCUboot image signed with the
same key: dial or dongle firmware (**open**), not Touch, Track or Tune firmware <span class="tag static">STATIC</span>[^fh]
([details](images.md#other-image-families)).

## The beta channel

The beta channel is the vendor's `NayaTech/NayaFlow-beta-releases`: 16 releases from
2025-09-01 to 2026-07-17. Five tags are shared with the stable channel (1.17.2, 1.19.1, 1.20.0, 1.21.0,
1.25.0) and eleven are beta-only (1.10.0, 1.16.0, 1.16.1, 1.17.0, 1.17.1, 1.18.0, 1.19.0, 1.22.0,
1.23.0, 1.23.1, 1.24.0), 36 distinct NayaFlow version numbers across both channels. A shared number
may still be a different build (the beta app is "NayaFlow-Beta"). Every beta release's images are
carved into create-legacy-firmware's `firmware-history-beta/` (commit 7b511ca), kept apart from the stable
`firmware-history/` that OpenFlow's firmware fetcher and catalog read <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^beta][^fhb][^fh-beta].

The table gives, for each beta release, the firmware its installer actually carries
(carved) beside what its note announces; where they differ, the carved image wins
<span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^beta][^fhb]. Bold marks firmware that shipped only on the beta channel.

| Beta release | Date | NayaCore (note) | Keyboard firmware carried | Module firmware carried | The note says |
|---|---|---|---|---|---|
| 1.10.0 | 2025-09-01 | (empty note) | none | none | nothing |
| 1.16.0 | 2026-02-03 | 5.8.1 to 6.1.2 | 3.29.1 (= stable 1.15.x) | 2.2.0 | keyboard 3.29.1 to 3.31.1, module 2.1.1 to 2.3.2 |
| 1.16.1 | 2026-02-03 | 6.1.3 | 3.29.1 | 2.2.0 | nothing on firmware |
| 1.17.0 | 2026-02-07 | 6.1.4 | 3.29.1 | 2.2.0 | nothing on firmware |
| 1.17.1 (pre-release) | 2026-02-11 | 6.1.5 | 3.31.1 | 2.3.2 | nothing on firmware |
| 1.17.2 | 2026-02-11 | not stated | 3.31.1 | 2.3.2 | nothing on firmware |
| 1.18.0 | 2026-03-12 | 6.4.0 | 3.35.4 | 2.3.2 | keyboard 3.31.1 to 3.35.4 |
| 1.19.0 | 2026-03-25 | 6.4.1 | 3.35.4 | 2.3.2 | nothing on firmware |
| 1.19.1 | 2026-04-03 | not stated | 3.35.4 | 2.3.2 | nothing on firmware |
| 1.20.0 | 2026-04-10 | 6.6.1 | 3.35.4 | 2.3.2 | nothing on firmware |
| 1.21.0 | 2026-04-21 | not stated | 3.35.4 | 2.3.2 | nothing on firmware |
| 1.22.0 | 2026-05-18 | 6.9.2 | **3.39.4** | 2.3.2 | keyboard 3.39.3 |
| 1.23.0 | 2026-05-21 | 6.10.1 | **3.40.0** | 2.3.3 | keyboard 3.40.0, module 2.3.3 |
| 1.23.1 | 2026-05-26 | 6.10.2 | **3.40.0** (repeat of 1.23.0) | 2.3.3 | nothing on firmware |
| 1.24.0 | 2026-06-09 | 6.10.3 | **3.40.4** | 2.3.3 | keyboard 3.40.4 |
| 1.25.0 | 2026-07-17 | 6.10.3 to 6.11.0 | 3.41.0 (generations A and B) | 2.3.3 | keyboard 3.40.4 to 3.41.0 |

The three beta-only keyboard firmwares are **3.39.4** (beta 1.22.0, 2026-05-18; its note
says 3.39.3, but the app constant `NAYA_CREATE_FW_VERSION` and NayaCore's version literal both say
3.39.4), **3.40.0** (beta 1.23.0, 2026-05-21, repeated in 1.23.1) and **3.40.4** (beta 1.24.0,
2026-06-09). None reached a stable release. They are stored as `kb_fwl.bin` and `kb_fwr.bin` in
`firmware-history-beta/v1.22.0/`, `v1.23.0/` and `v1.24.0/` <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^fhb][^fh-beta]:

| Firmware | Beta release | `img_size` left / right | Plaintext hash left / right | `fe/1002` reply (expected) |
|---|---|---|---|---|
| 3.39.4 | 1.22.0 | 327 008 / 224 464 | `d9f7f80a` / `d3d7bf81` | `00 00 03 27 04` |
| 3.40.0 | 1.23.0 | 327 264 / 224 800 | `01e3ddda` / `8b0a4e3d` | `00 00 03 28 00` |
| 3.40.4 | 1.24.0 | 327 808 / 225 024 | `3740d363` / `684f70f8` | `00 00 03 28 04` |

The `fe/1002` replies follow the encoding above; no board on these versions has been measured
<span class="tag inferred">INFERRED</span>.

The first release carrying each firmware image, across both channels: 3.31.1 in beta
1.17.1 (2026-02-11) and stable 1.17.2 (2026-02-18); 3.35.4 in beta 1.18.0 (2026-03-12) and stable
1.19.1 (2026-04-03); 3.41.0 in beta and stable 1.25.0 (2026-07-17); module 2.3.2 in beta 1.17.1 and
stable 1.17.2; module 2.3.3 in beta 1.23.0 (2026-05-21) and stable 1.25.0, 57 days later. Betas
1.16.0, 1.16.1 and 1.17.0 ship the stable 1.15.x images byte for byte (keyboard 3.29.1, module 2.2.0)
although the 1.16.0 note announces 3.31.1 and 2.3.2 <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^fhb][^fh-beta][^beta][^cl].

Beta 1.10.0 (2025-09-01, empty note) contains no firmware: its NayaCore embeds no
firmware resources and no MCUboot image, and carries only the version literals 0.2.0.0, 0.3.4.6 and
0.3.8.9 <span class="tag static">STATIC</span>[^fhb].

The 16 beta releases carried 47 images: 6 new (the three beta-only keyboard pairs), 39
byte-identical copies of stable images and 2 repeats of an earlier beta. Every beta keyboard image
uses the stable KEYHASH `de8b0718...5fd5b972`, MCUboot header version `1.2.3+4` and the same
pre-armed permanent-swap trailer as the stable images. The beta-only firmware is generation A only;
`_64` images first appear in 1.25.0, on both channels <span class="tag static">STATIC</span>[^fhb][^fh-beta].

Some NayaCore versions only ever shipped on the beta channel: 6.1.2, 6.1.3, 6.1.4, 6.4.0,
6.9.2, 6.10.1, 6.10.2 and 6.10.3 <span class="tag doc">DOC</span>[^beta][^cl].

## Firmware in the field

Boards in circulation run more than 3.41.0. We have measured 3.28.7 (with modules on
2.1.2), 3.35.4 and 3.41.0 on the owner's boards <span class="tag measured">MEASURED</span>; 3.30.1 is reported publicly <span class="tag reported">REPORTED</span>[^nx-pr5]; and a
board last updated from the beta channel before 2026-07-17 may run a beta-only version <span class="tag inferred">INFERRED</span>. One board
arrived with its left half on 3.41.0 and its right half on 3.35.4 in **both** slots: the vendor
update had never reached the right half (owner's board, slot hashes read 2026-09-20) <span class="tag measured">MEASURED</span>.

3.30.1 is in no public release on either channel: the beta carve confirms that no
installer carries it <span class="tag static">STATIC</span>[^fhb]. A factory build is the likelier explanation <span class="tag inferred">INFERRED</span>: the beta 1.16.0 note
says that "starting with the last batch of hardware, a custom build of NayaCore has been used for all
testing and validation" <span class="tag doc">DOC</span>[^cl-300][^beta]. The board it was read on belongs to the nayactl
maintainer <span class="tag reported">REPORTED</span>[^nx-pr5].

Module firmware seen on hardware: 2.1.2 (the modules of the 3.28.7 board, and a Touch on
the 3.41.0 board) and 2.3.3 (Tune and Track on the 3.41.0 board) <span class="tag measured">MEASURED</span> (owner's boards, 2026-09-16 and
2026-09-19); 2.2.2 on the nayactl maintainer's board <span class="tag reported">REPORTED</span>[^nx-pr5] (raw data checked: its module
version replies read `02 02 02` for a Track and a Touch). 2.2.2, like 3.30.1, is in no public release:
the bundles carry 2.1.1, 2.1.2, 2.2.0, 2.3.2 and 2.3.3 <span class="tag static">STATIC</span>[^fh].

The stock dongle reports USB `bcdDevice` `0x0307`, but so do the halves' bootloader identities
(their applications report `0x0300`), so the value most likely reflects the USB stack's default
(Zephyr 3.7) rather than a dongle firmware version <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span> (owner's board, 2026-09-11). No dongle image is embedded in NayaFlow 1.21.0 or 1.25.1:
their manifests list only keyboard images and `FlashMemory.bin`, and NayaCore 1.25.1's resource paths
name only `kb_fw/` and `m_fw/` <span class="tag static">STATIC</span>[^fh]. Also reported by the createflow-dongle author[^cfd].

Which firmware people likely run: Windows installer downloads, grouped by the keyboard
firmware each installer bundles (create-legacy-firmware's release metadata captured 2026-09-14), are about
3 570 for 3.29.1, 2 620 for 3.35.4, 1 720 for 3.41.0, 1 480 for 3.31.1 and 1 110 for 3.28.7. Downloads
are not installs (Windows installers also serve auto-updates), so this is weak evidence; read
`fe/1002` on both halves instead of assuming <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^mf].

## What changed, by version

The vendor's changes per keyboard firmware, dated to the first release that carried each
image <span class="tag doc">DOC</span>[^cl][^beta][^fhb]:

| Firmware | First carried by | Vendor-listed changes |
|---|---|---|
| 3.28.7 | 1.14.5 (2025-10-03) | hold-tap keys no longer stick when two activate together (a fix left out of 3.28.6) |
| 3.29.1 | 1.15.0 (2025-11-07) | module update method prevents installing the wrong firmware; Force Module Update |
| 3.31.1 | beta 1.17.1, stable 1.17.2 (announced in beta 1.16.0) | engineering text channel (SystemCDC) retired, about 5 % faster; LED PWM power control, about 50 % less power at maximum brightness; LED color desync between the halves fixed |
| 3.35.4 | beta 1.18.0, stable 1.19.1 | Bluetooth "BLE v2" (see below); module battery management, about 10 % better |
| 3.39.4 (beta only; announced as 3.39.3) | beta 1.22.0 | LED notifications; firmware-side LED remapping; power cycling on a low internal battery with a depleted module battery fixed; less Bluetooth traffic between the halves |
| 3.40.0 (beta only) | beta 1.23.0 | per-LED OFF state |
| 3.40.4 (beta only) | beta 1.24.0 | three activity-timeout fixes (the right half waking the left at idle, Track not keeping the Create awake, LEDs stuck half on and half off); lower low-battery LED threshold; LED effect and color actions take priority until restart; module update no longer fails unless the LED effect is Solid |
| 3.41.0 | 1.25.0 (2026-07-17) | LED action override setting; LED colors landing on the wrong keys during rapid updates fixed; Tune phantom ticks when switching layers fixed |

Per module firmware <span class="tag doc">DOC</span>[^cl][^beta]: 2.1.2 fixed Track scrolling (rotation around the Z axis)
triggering too easily; 2.2.0 added Force Module Update support and animation brightness sync; 2.3.2
added Tune LED PWM (about 20 % less at maximum) and exact instead of estimated Tune ticks; 2.3.3 fixed
Tune phantom ticks near detents and disabled the battery blink "as battery can now be fully read out
by NayaFlow".

Host changes that matter for firmware <span class="tag doc">DOC</span>[^cl][^beta]: NayaCore 5.8.1 (NayaFlow 1.15.0)
flashes up to 2.5 times faster and adds Force Module Update; 6.1.2 and 6.1.5 retire SystemCDC on the
host side and merge in the manufacturing tool; 6.1.3 handles a corrupted module firmware file; 6.1.4
fixes Interrupt Flavor and Tapping Term not being applied in some cases (the stable note lumps it
under 6.1.5); 6.4.0 adds the SPI flash test and format, Clear BLE Devices and per-half names; 6.9.2
fixes a silently failing pairing workflow; 6.10.2 handles a hold-tap action and flavor mismatch on
write; 6.11.0 adds generation-B ("64-bit") Create updates, consolidated firmware version checks
(Create, module and dongle minimums; see [above](#minimum-firmware-nayacore-expects)) and a Bluetooth version check after an update.

**The Bluetooth v1 to v2 boundary.** Updating from 3.31.1 or older to 3.35.4 or newer
removes every known Bluetooth host from the keyboard, so computers must be paired again. NayaFlow
1.25.1 warns that a "BLE v1" left half switches to BLE v2 during the update and that the link between
the halves fails until both are on BLE v2, in either order <span class="tag doc">DOC</span>[^cl-222][^nc]. See
[Recovery](../recovery.md#r15-bluetooth-hosts-forgotten-after-an-update).

Before any of this: the tester firmware of January 2025 was wired-first with "limited
wireless support", "no remapping support" and "no modules support"; the first NayaFlow release could
only flash the keyboard; "Naya Flow Version 1" with key remapping was live by 2025-06-16
<span class="tag doc">DOC</span>[^ks-19][^ks-21].

## Minimum firmware NayaCore expects

NayaCore 6.11.0 (NayaFlow 1.25.0 and 1.25.1) checks a board against minimum firmware versions, the
"consolidated firmware version checks" of its release note. The values are readable in the binary:
inline string variables set at start-up from literals in the four-part wire form
<span class="tag static">STATIC</span>[^nc-gates] <span class="tag doc">DOC</span>[^cl]:

| Gate | Minimum | What it covers |
|---|---|---|
| ProtocolCDC, and its copies Keymap, Pair, ClearAllData, TestSPIFlash, UpdateModule | keyboard 3.30.0 | REMAP (`30/*`, left half only) and most commands and operations |
| BLEStatus | keyboard 3.32.0 | `be/100c`-`be/100f` |
| ClearAllSplitLinks | keyboard 3.34.0 | `be/1010` |
| ActivityTimeouts | keyboard 3.36.0 | `fe/100a`, `fe/100b` |
| UpdateFW | none (0.0.0) | firmware updates |
| module ProtocolCDC | module 2.3.0 | module commands |
| dongle ProtocolCDC | dongle 0.1.0.2 (as written) | the dongle |

The full per-command table is on
[Differences by firmware](../protocol/firmware-differences.md#minimum-firmware-per-command), and how it
was read is on [Disassembly](../software/disassembly.md#version-gates). The gates explain the version
strings in beta NayaCore builds from 1.17.1 on that match no image (0.3.30.0, 0.3.32.0, 0.3.34.0 and,
from beta 1.22.0, 0.3.36.0): they are these thresholds, not firmware releases <span class="tag static">STATIC</span>[^fhb][^nc-gates].
One beta literal, 0.3.35.0, matches no 6.11.0 gate <span class="tag open">OPEN</span>. They are the
host's gates, not a list of what older firmware can do: 3.28.7 answers REMAP reads although its gate
is 3.30.0 <span class="tag measured">MEASURED</span> (donor board, 2026-09-19).

## Behavior that differs by firmware

A short summary; the canonical, detailed matrix is on
[Differences by firmware](../protocol/firmware-differences.md).

| Behavior | 3.28.7 | 3.35.4 | 3.41.0 | 3.39.4, 3.40.0, 3.40.4 |
|---|---|---|---|---|
| CDC serial interfaces per half | 2 | not recorded | 1 | unmeasured |
| Bluetooth status reads `be/100c` to `be/100f` | absent | not recorded | present | unmeasured |
| A configuration write of three CDC frames | wedges the half | not recorded | accepted | unmeasured |
| Second binding bank in layer reads | not recorded | not reported | reported | unmeasured |
| LED payload between the halves | differs from 3.41 | differs from 3.41 | changed in 3.41 | unmeasured |
| Engineering text channel | not yet retired | retired (from 3.31.1) | silent | unmeasured |
| Activity timeouts under 30 s | not recorded | not recorded | refused | unmeasured |

Measured on the owner's boards (3.28.7 on 2026-09-19; 3.35.4 and 3.41.0 between 2026-09-01 and
2026-09-22) <span class="tag measured">MEASURED</span>, except the text-channel retirement, which is the vendor's note <span class="tag doc">DOC</span>[^cl-310].

## The last release

3.41.0 (NayaFlow 1.25.0, 2026-07-17, re-shipped in 1.25.1 on 2026-07-21) is the last
published keyboard firmware, and 2.3.3 the last module firmware <span class="tag doc">DOC</span>[^cl][^beta][^fhb].
The vendor's
status is stated once, on the [home page](../index.md).

## Where this differs from naya-create-kb

| naya-create-kb says (versions page) | What the evidence shows |
|---|---|
| The halves are nRF52811 | nRF52840 ([ZMK](zmk.md#the-hardware-a-port-targets)) |
| 0.1.1 is the oldest archived firmware | 0.0.1 and 0.0.2 are older (285 392 / 218 256) |
| The desktop core moves out of the asar at 1.15.1 | It moves out at 1.19.1 |
| The images shrink at 1.21.0 | They shrink at 3.31.1 (1.17.2); 3.35.4 in 1.21.0 is larger again |
| 328 880 pairs with `fwr_64`, 226 000 with `fwl_64`; "dual-slot entries"; `_64` introduced in 1.25.1 as dual-bank slots | `kb_fwl_64.bin` is the left image (328 880), `kb_fwr_64.bin` the right (226 000); `_64` is flash generation B, first in 1.25.0 |
| Module firmware is present only up to 1.6.10; releases from 1.15 on carry none; 0.1.1 ships one 175 136-byte module blob | Module firmware ships in every stable release from 1.11.0 (`FlashMemory.bin`, 2.1.1 to 2.3.3); the 175 136-byte image is `d_fw.bin` |

## Open questions

- <span class="tag open">OPEN</span> The firmware versions of the images in 0.0.1 to 1.11.11, and the module version of the 1.11.x bundle ([details](../open-questions.md#oq-f12)).
- <span class="tag open">OPEN</span> How the beta-only firmware (3.39.4, 3.40.0, 3.40.4) behaves on the wire: carved, never measured.
- <span class="tag open">OPEN</span> How NayaCore acts on a board below a minimum-firmware gate, and why one beta literal (0.3.35.0) matches no 6.11.0 gate; the gates themselves are read ([above](#minimum-firmware-nayacore-expects); [details](../open-questions.md#oq-f17)).
- <span class="tag open">OPEN</span> Whether the 1.25.1 NayaCore still ships a Linux build, and whether 1.15.0's Linux NayaCore ran at all.
- <span class="tag open">OPEN</span> NayaCore versions of 1.14.3, 1.15.1, 1.21.0 and 1.25.1, which the vendor does not state ([details](../open-questions.md#oq-f12)).
- <span class="tag open">OPEN</span> Whether `d_fw.bin` is dial or dongle firmware ([details](../open-questions.md#oq-f08)).
- <span class="tag open">OPEN</span> Where 3.30.1 came from (a factory build?) ([details](../open-questions.md#oq-f12)).

## Sources

[^cl]: create-legacy-firmware, [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md): the vendor's release notes of `NayaTech/NayaFlow-releases`, captured 2026-09-14.
[^cl-310]: create-legacy-firmware, [`CHANGELOG.md` L310-L314 and L345](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L310-L314) (the two spellings; SystemCDC retirement).
[^cl-300]: create-legacy-firmware, [`CHANGELOG.md` L300](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L300) (manufacturing build of NayaCore).
[^cl-222]: create-legacy-firmware, [`CHANGELOG.md` L222](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L222) (BLE v1 to v2 removes known hosts).
[^mf]: create-legacy-firmware, [`MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/MANIFEST.json) (GitHub release metadata of all 25 stable releases, captured 2026-09-14), with `download.log` and `verify.py`.
[^fh]: create-legacy-firmware, [`FIRMWARE-HISTORY.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FIRMWARE-HISTORY.md) and the per-release `firmware-history/<version>/manifest.json` files.
[^fh-beta]: create-legacy-firmware, [`FIRMWARE-HISTORY.md`, "Beta channel"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FIRMWARE-HISTORY.md#L153-L218).
[^fhb]: create-legacy-firmware, [`firmware-history-beta/MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/firmware-history-beta/MANIFEST.json) (commit 7b511ca).
[^nc-gates]: NayaFlow 1.25.1, NayaCore 6.11.0 (macOS arm64, cross-checked on x86_64), our disassembly (2026-09-23): the guarded initializers of the `naya_fw::*_MinVersion` values, `operationMinFWVersion` and `commandMinFWVersion`; see [Disassembly](../software/disassembly.md#version-gates).
[^fp-binary]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Native service binary"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L107-L120).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (read 2026-09-23).
[^nc]: NayaFlow 1.25.1: main-process bundle constants and NayaCore 6.11.0 strings (version status names, the BLE v1/v2 warning, component repository names).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5), comment by the maintainer (a board on 3.30.1 with modules on 2.2.2, and their version replies).
[^cfd]: createflow-dongle, [`docs/findings.md`](https://github.com/mediaandmerch/createflow-dongle/blob/main/docs/findings.md).
[^kb-versions]: naya-create-kb, [firmware/versions](https://nemezzizz.github.io/naya-create-kb/firmware/versions/).
[^ks-19]: Kickstarter update 19, [2025-02-11](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4312089).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).

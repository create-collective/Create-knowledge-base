# History

How Naya's desktop software changed from NayaFlow 0.0.1 (March 2025) to 1.25.1 (July 2026), on the
stable and the beta channel, so that a reader holding an old installer or an old board knows which
pieces and which protocol they have. The one thing to know: the device service was rewritten twice
(a `newtmgr`-based service, then `naya_core_project`, then NayaCore), and a keyboard's firmware is
whatever the last NayaFlow that updated it carried, including three versions that only ever shipped
on the beta channel.

!!! note "At a glance"
    - 25 stable releases (2025-03-19 to 2026-07-21) and 16 beta releases (2025-09-01 to 2026-07-17);
      every installer is still public, and create-legacy-firmware mirrors the stable channel.
    - Keyboard firmware by stable release: 3.28.7 (1.14.5), 3.29.1 (1.15.x), 3.31.1 (1.17.x), 3.35.4
      (1.19.1-1.21.0), 3.41.0 (1.25.x).
    - Beta-only keyboard firmware: 3.39.4, 3.40.0, 3.40.4.
    - Old installers auto-update when run online; run them offline to keep an old version.

!!! warning "Old installers update themselves, and updating flashes both halves"
    electron-updater's auto-download and install-on-quit are on, so an old installer run online may
    replace itself <span class="tag inferred">INFERRED</span> (its `app-update.yml` and defaults).
    Installing NayaFlow and running "Update" flashes both halves; see [Flashing](../firmware/flashing.md).

## Where the releases are

- Naya published installers in two public GitHub repositories: `NayaTech/NayaFlow-releases` (25 stable
  releases, v0.0.1 2025-03-19 to v1.25.1 2026-07-21, 264 assets, about 21.5 GB) and
  `NayaTech/NayaFlow-beta-releases` (16 releases, 2025-09-01 to 2026-07-17; 5 tags shared with stable,
  11 beta-only). 36 distinct NayaFlow version numbers were published <span class="tag doc">DOC</span>[^rel][^beta][^nh-manifest].
- create-legacy-firmware mirrors every stable asset with GitHub sha256 digests (264 of 264 downloaded; 208
  digest-verified, 56 size-only because v0.x assets and `.yml` files carry no digest), the 14 release
  notes, and the firmware images carved from each release's NayaCore; it is OpenFlow's firmware
  library. It also records the beta channel: `firmware-history-beta/MANIFEST.json` lists all 16 beta
  releases and every image each carried, and stores only the six images found nowhere else. OpenFlow's
  catalog reads only the stable tree <span class="tag static">STATIC</span>[^nh].
- 14 of the 25 stable releases carry release notes: v0.1.0, v0.1.1, v1.3.8, v1.3.11, v1.14.5,
  v1.15.0, v1.15.1, v1.17.2, v1.17.3, v1.19.1, v1.20.0, v1.21.0, v1.25.0, v1.25.1
  <span class="tag doc">DOC</span>[^nh-changelog].

## Eras at a glance

| Releases | Device service | Where it sits | Firmware upload | UI to service |
|---|---|---|---|---|
| 0.0.1-1.6.10 | `naya_core_fw_service` | inside `app.asar` (Windows) | a bundled Apache mynewt `newtmgr` | text over a WebSocket and stdin/stdout; ZeroMQ markers from 1.6.10 |
| 1.11.0-1.11.11 | `naya_core_project` (about 3.3 MB) | `app.asar.unpacked` (Windows); `Contents/core/naya_core_project.app` (macOS) | Naya's own in-process SMP client | ZeroMQ (libzmq 4.3.6) |
| 1.14.3-1.17.3 | `NayaCore` | inside the asar (Windows); `Contents/core/NayaCore.app` (macOS) | in-process SMP | ZeroMQ |
| 1.19.1-1.25.1 | `NayaCore` | `core/NayaCore/` (Windows); `Contents/core/NayaCore.app` (macOS) | in-process SMP | ZeroMQ |

<span class="tag static">STATIC</span> (our scan of every stable installer; create-legacy-firmware[^nh-fp-binary];
the macOS release zips). naya-create-kb puts the move out of the asar at 1.15.1[^kb-versions]; on
Windows it came at 1.19.1, and on macOS the service has sat under `Contents/core` since at least
1.11.11. The macOS asars of 1.14.5 to 1.17.3 also carry a leftover copy of the Windows `NayaCore.exe`.

- **Service sizes** (Windows): 14.0 MB (0.0.x), 14.4 MB (0.1.x), 14.3 MB (1.3.8-1.6.10), 3.34 MB
  (1.11.0-1.15.1, newtmgr gone), 6.5 MB (1.17.x), 8.5 MB (1.25.x). macOS NayaCore: 10.1 MB (1.19.1),
  10.9 MB (1.20.0, 1.21.0), 12.6 MB (1.25.x, Intel; the arm64 build is 11.9 MB)
  <span class="tag static">STATIC</span>.
- **Messaging**: text commands over a WebSocket (`ws://localhost:<port>/ws`; the `:1024` string
  survives in late bundles) and stdin/stdout lines up to about 1.3.x; 1.6.4 and 1.6.5 transitional;
  ZeroMQ markers from 1.6.10; by 1.11.0 the service links libzmq 4.3.6 (`libzmq-v143-mt-4_3_6.dll` on
  Windows; `libzmq.5.dylib` on macOS from 1.19.1). Our two scans disagree on whether 1.6.10 already used
  ZeroMQ for its messaging <span class="tag static">STATIC</span> <span class="tag open">OPEN</span>
  ([details](../open-questions.md#oq-s13)).
- **Upload**: the bundled `newtmgr` (Go, a Codecoup build) run by the service in 0.0.1-1.6.10
  (`:/resources/includes/nmgr_win/newtmgr.exe`, `nmgr_mac/newtmgr`; about 3 900 newtmgr string
  references); from 1.11.0 Naya's own in-process SMP client (functions with an `ERK` suffix such as
  `sendFramedCommandERK`); un-suffixed names (`uploadImageToSlot`, `sendFramedCommand`,
  `parseSMPResponse`) appear beside them from 1.17.2 (Windows strips these names; macOS and Linux keep
  them). The serial rate is 1 000 000 in every era (`115200` also appears in the 0.x services)
  <span class="tag static">STATIC</span>[^nh-fp].
- **Background server**: a Node "background-server" (0.0.x) and "desktop-background-server" (0.1.0 to
  1.21.0 as a bundle; Hono/express-style HTTP, a WebSocket at `ws://localhost:<port>/ws`, drizzle ORM on
  better-sqlite3); the Go `flow-bg-server` is present by 1.17.3 (in-asar `@naya-suite/flow-bg-server`,
  spawned by `desktop-main` with `NAYA_CORE_EXE_DIR`); in 1.25.x it is installed outside the asar as
  `flow/flow-bg-server.exe`, with the Electron main moved to `dist/main/index.js`
  <span class="tag static">STATIC</span>.
- **Command vocabulary**: 0.0.1-1.3.11 UI commands (sent with `sendCommand`) `mcb_kbl_start`,
  `mcb_kbr_start`, `prog_kbb_verify`, `prog_quit`, and `ble_pair_auto_start` from 0.1.0; from 1.6.4 the
  JavaScript no longer calls `sendCommand`. The 0.0.x service understood `mcb_kb*`
  (start/success/fail/dep_fail), `mcb_usb_port`, `prog_alive`, `prog_command_queued`, `prog_dep_*`
  (paths for fwl, fwr, newtmgr; firmware version; verify), `prog_kbb_verify*`, `prog_log_*`,
  `prog_ready`, `prog_unknown_command`, `prog_version`; 0.1.0 added `ble_pair_*`, `dongle_fw_version`,
  `dongle_mode_release_toggle`, `dongle_upgrade_mcb_*`, `mcb_dongle_*` and progress events;
  `mcb_usb_port` is gone from 1.3.8. NayaCore's events: 1.11.x `fw_update`, `fw_update_init`,
  `fw_update_create_start`, `fw_update_create_pairing_start`, `fw_update_module_start`,
  `fw_update_end`, `fw_update_status`, `fw_version*`, `fw_process_status_*`; 1.17.x only `fw_files`,
  `fw_update_status`, `fw_version` (the 6.1.x messaging redesign); 1.19.1 on adds `fw_version_epoch`,
  `fw_version_legacy`, `fw_version_remapping`. 1.25.1's 16-event list is on
  [NayaFlow and NayaCore](nayaflow.md) <span class="tag static">STATIC</span>.
- **Embedded images**: Qt resource paths `:/resources/includes/kbfw/` (0.0.1-0.0.2), `includes/kb_fw/`
  and `d_fw/` (0.1.0-1.6.10), `includes/kb_fw/` and `m_fw/` (1.11.0-1.14.5), `Includes/kb_fw/` and
  `m_fw/` (capital I, 1.15.0-1.25.1); `kb_fw*_64.bin` (flash generation B) and PID-based generation selection
  first appear in 1.25.0 <span class="tag static">STATIC</span>[^nh-fp]. File names per release are on
  [Firmware versions](../firmware/versions.md).

## Stable releases

| Release | Date | Service (NayaCore) | Keyboard | Module | Notable host changes |
|---|---|---|---|---|---|
| 0.0.1, 0.0.2 | 2025-03-19 | fw_service | pre-production images | - | first public builds; flash-only |
| 0.1.0 | 2025-05-01 | fw_service | placeholder `1.2.3+4` | `d_fw` image | auto-updater fix, Track enabled, per-module scroll direction, Tune left/right configs, Bluetooth pairing fixes, slot 5 reserved for a future dongle |
| 0.1.1 | 2025-05-02 | fw_service | placeholder | `d_fw` image | installer 40 MB smaller |
| 1.3.8 | 2025-06-13 | fw_service | placeholder | `d_fw` image | custom key remapping (Press only); "completely redeveloped Naya Core" |
| 1.3.11 | 2025-06-15 | fw_service | placeholder | `d_fw` image | profile duplicate |
| 1.6.4, 1.6.5, 1.6.10 | 2025-07-13 to 07-24 | fw_service | placeholder | `d_fw` image | (no notes) |
| 1.11.0 to 1.11.11 | 2025-09-07 to 09-19 | naya_core_project | placeholder | module bundle | newtmgr dropped; the module bundle replaces the `d_fw` image |
| 1.14.3 | 2025-10-02 | NayaCore (5.5.1) | 3.28.6 (INFERRED) | - | binary renamed NayaCore |
| 1.14.5 | 2025-10-03 | NayaCore 5.5.2 | 3.28.7 | 2.1.2 | |
| 1.15.0 | 2025-11-07 | NayaCore 5.8.1 | 3.29.1 | 2.2.0 | JIS input source and templates, Force Module Update, flashing up to 2.5x faster |
| 1.15.1 | 2026-01-06 | (5.8.1) | 3.29.1 | 2.2.0 | readiness detection for newly delivered units |
| 1.17.2 | 2026-02-18 | NayaCore 6.1.5 | 3.31.1 | 2.3.2 | breaking IPC change, SystemCDC retired, manufacturing build merged, 30-minute backups, DeviceManager renamed Hardware Manager, Software Info, Intel Mac beta |
| 1.17.3 | 2026-02-18 | (6.1.5) | 3.31.1 | 2.3.2 | NayaCore log folder fix |
| 1.19.1 | 2026-04-03 | NayaCore 6.4.1 | 3.35.4 | 2.3.2 | BLE v2, Connection tab, SPI flash test and format, Clear BLE Devices |
| 1.20.0 | 2026-04-15 | NayaCore 6.6.1 | 3.35.4 | 2.3.2 | module battery on hover, help buttons, Intel Mac stable |
| 1.21.0 | 2026-04-21 | (6.6.1) | 3.35.4 | 2.3.2 | one-click diagnostics report |
| 1.25.0 | 2026-07-17 | NayaCore 6.11.0 | 3.41.0 | 2.3.3 | Double Tap and Tap and Hold, LED settings, manual backups, window scaling, Cmd/Ctrl+S and Cmd/Ctrl+D, Windows code signing, 64-bit (generation B) Create images |
| 1.25.1 | 2026-07-21 | (6.11.0) | 3.41.0 | 2.3.3 | auto-update fix (the last release) |

<span class="tag doc">DOC</span> <span class="tag static">STATIC</span> (release dates from GitHub;
notes[^rel]; create-legacy-firmware manifests[^nh]). NayaCore versions come from the notes ("5.5.1 -> 5.5.2" in
1.14.5, "5.5.2 -> 5.8.1" in 1.15.0, "5.8.1 -> 6.1.5" in 1.17.2, "6.1.5 -> 6.4.1" in 1.19.1,
"6.4.1 -> 6.6.1" in 1.20.0, "6.6.1 -> 6.11.0" in 1.25.0); 1.14.3, 1.15.1, 1.21.0 and 1.25.1 name none,
so they carry the previous one (in parentheses) <span class="tag inferred">INFERRED</span>. The
keyboard firmware of the 0.x-1.11.11 images is unknown: their MCUboot header carries the placeholder
version `1.2.3+4` <span class="tag open">OPEN</span>. naya-create-kb's version page covers six of these
releases[^kb-versions].

Release-note oddities <span class="tag doc">DOC</span>[^rel]: v1.19.1's note says "NayaFlow (v1.17.1
-> v1.19.0)" and v1.20.0's "v1.19.0 -> v1.20.0"; features shipped in 1.22.0 were announced only in
1.25.0 ("omitted from the release note"); modules "v2.1.1 -> v2.3.2" in 1.17.2 although 1.15.0 had
announced 2.2.0; the scaling shortcuts written as "CMD/Ctrl+plus and CMD/Ctrl+plus". SystemCDC, the text
"engineering communication channel", was retired on the host in NayaCore 6.1.2 (beta 1.16.0) / 6.1.5
(stable 1.17.2) and on the keyboard in firmware 3.31.1 ("improve performance by ~5%"); text commands
answer nothing on 3.41.0 <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span>
(nayactl pull request #2[^nx-pr2]). The Interrupt Flavor / Tapping Term "not applied in some cases" fix
is NayaCore 6.1.4 (beta 1.17.0), not 6.1.5 <span class="tag doc">DOC</span>[^beta].

## The beta channel

NayaFlow-Beta is a separate app published from `NayaTech/NayaFlow-beta-releases`
<span class="tag doc">DOC</span>[^beta]. What each beta release really carried, read from the
installers rather than the notes <span class="tag static">STATIC</span>
<span class="tag doc">DOC</span>[^nh-fhb]:

| Beta | Date | Keyboard / module carried | Note |
|---|---|---|---|
| 1.10.0 | 2025-09-01 | none: its NayaCore embeds no firmware resource | empty note; its NayaCore version is unknown |
| 1.16.0, 1.16.1 | 2026-02-03 | 3.29.1 / 2.2.0, the stable 1.15.x images byte for byte | the 1.16.0 note announces 3.31.1 and modules 2.3.2 |
| 1.17.0 | 2026-02-07 | 3.29.1 / 2.2.0 | |
| 1.17.1, 1.17.2 | 2026-02-11 | 3.31.1 / 2.3.2 | 3.31.1 first appears here, one week before stable 1.17.2 |
| 1.18.0 | 2026-03-12 | 3.35.4 / 2.3.2 | 3.35.4 first appears here, three weeks before stable 1.19.1 |
| 1.19.0, 1.19.1, 1.20.0, 1.21.0 | 2026-03-25 to 04-21 | 3.35.4 / 2.3.2 | |
| 1.22.0 | 2026-05-18 | **3.39.4** / 2.3.2 (beta only) | its note says 3.39.3; the app constant and NayaCore's version string both say 3.39.4 |
| 1.23.0, 1.23.1 | 2026-05-21, 05-26 | **3.40.0** / 2.3.3 (beta only) | module 2.3.3 arrives 57 days before stable 1.25.0 |
| 1.24.0 | 2026-06-09 | **3.40.4** / 2.3.3 (beta only) | |
| 1.25.0 | 2026-07-17 | 3.41.0 / 2.3.3, generations A and B | the same images as stable 1.25.0 |

- The three beta-only keyboard firmwares (3.39.4, 3.40.0, 3.40.4) are generation A only (no `_64`
  build); their left and right images are archived in create-legacy-firmware's beta tree, kept apart so no
  flasher offers them. A board last updated from beta before 2026-07-17 may still run one of them;
  nobody we know has measured them <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>
  <span class="tag inferred">INFERRED</span>[^nh-fhb].
- The beta images are packaged exactly like the stable ones: every beta keyboard image is encrypted and
  signed with the same key (KEYHASH `de8b0718...5fd5b972`), has MCUboot header version `1.2.3+4`, and is
  the whole 663 552-byte slot with the permanent-swap trailer already written. The 16 beta releases
  carried 47 images: 6 new, 39 byte-identical to stable images, 2 repeats of an earlier beta; `_64`
  (generation B) images first appear in 1.25.0 on both channels <span class="tag static">STATIC</span>[^nh-fhb].
- NayaCore versions that only appeared on beta: 6.1.2, 6.1.3, 6.1.4, 6.4.0, 6.9.2, 6.10.1, 6.10.2,
  6.10.3 <span class="tag doc">DOC</span>[^beta]. Beta NayaCore builds from 1.17.1 on also carry the
  literals `0.3.30.0`, `0.3.32.0`, `0.3.34.0` and (from 1.22.0) `0.3.36.0`, which match no image: they
  are NayaCore's minimum-firmware gates (see [Disassembly](disassembly.md#version-gates))
  <span class="tag static">STATIC</span>.
- Host-side changes by beta NayaCore <span class="tag doc">DOC</span>[^beta]: 6.1.3 corrupted module
  file handled and module battery reporting corrected; 6.4.0 BLE v2 support, SPI flash test/format,
  Clear BLE devices, per-half names from the hardware id; 6.6.1 module battery reading re-enabled;
  6.9.2 device detection redesigned and a silently failing pairing workflow fixed; 6.10.1 LED OFF
  state; 6.10.2 hold-tap action / flavor mismatch write handled; 6.10.3 modules not following the color
  map, and a communication breakdown on corrupted data, fixed; 6.11.0 Double Tap and Tap and Hold, LED
  setting commands, 64-bit Create images (the beta title misprints "4-bit"), consolidated firmware
  version checking, pairing error codes, a post-update Bluetooth version check, ProtocolCDC command
  timeouts, a dongle crash.
- Keyboard 3.30.1 (the nayactl maintainer's board) is in no public release on either channel (the beta
  carve confirms it: no beta image carries it); the beta 1.16.0 note says "a custom build of NayaCore
  has been used for all testing and validation" of the last hardware batch, so a factory build is the
  likelier source <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span> (third
  party: nayactl pull request #5, `fe/1002` reply `00 00 03 1e 01`[^nx-pr5])
  <span class="tag inferred">INFERRED</span>.
- The beta and stable 1.19.1 and 1.25.0 went out within seconds of each other; NayaFlow and
  NayaFlow-Beta cannot run at the same time <span class="tag doc">DOC</span>[^beta].

## Platforms and update channels

- **Linux**: only 0.0.1-0.1.1 shipped a Linux AppImage, and its JavaScript had no Linux service path
  (`_getNayaCoreLinuxExePath` returns ""), so it carried no firmware. Linux NayaCore builds exist in
  1.15.0, 1.15.1, 1.17.2 and 1.17.3 (1.17.3 README: Qt 6 libraries, `NayaCore.sh`, `run.sh`, "Ubuntu
  20.04+"), and they embed the 1.14.5 images (3.28.7 / module 2.1.2) while Windows and macOS shipped
  newer ones. Whether 1.19.1 and later had a Linux NayaCore is <span class="tag open">OPEN</span> (the
  1.25.1 main bundle still carries Linux tray icons) <span class="tag static">STATIC</span>[^nh-fp-binary]
  ([details](../open-questions.md#oq-s09)).
- **macOS**: x64 assets in 0.x, then arm64 only until the Intel build (beta from 1.17.1, stable in
  1.20.0). **Windows** builds are code-signed from 1.25.0. A portable Windows `.exe` shipped beside the
  installer in 1.3.8-1.15.0 <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^rel][^nh-manifest].
- **Update channel files**: `latest.yml` (all 25, Windows), `latest-mac.yml` (all 25),
  `latest-linux.yml` (0.0.1-0.1.1), `latest-mac-x64.yml` (1.17.3-1.21.0, which points at the Windows
  installer), `latest-mac-x64-mac.yml` (1.19.1-1.21.0), `latest-intel-mac.yml` (1.20.0-1.25.1). The
  vendor's own note says "the Windows auto-updater ended up tracking the wrong OS"
  <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^nh-manifest][^rel].
- **The update check that never worked**: it sends an unsubstituted build placeholder as its GitHub
  bearer token (not reproduced here), so GitHub answers 401 even for public repositories and every
  "latest tag" lookup is empty; 0.0.1-0.1.1 carry no such token. The component repositories the
  bg-server asks for besides `NayaFlow-releases` (`NayaCore-`, `NayaTouch-`, `NayaTrack-`, `NayaTune-`,
  `NayaFloat-releases`) return 404 to outsiders <span class="tag static">STATIC</span>
  <span class="tag measured">MEASURED</span> (access checks 2026-09-01 and 2026-09-22)
  ([details](../open-questions.md#oq-s12)).
- **Download counts** (Windows installer, snapshot 2026-09-14): 1.15.1 2040, 1.21.0 1592, 1.15.0 1531,
  1.17.3 1411, 1.25.1 1325, 1.14.5 1114; `latest.yml` of 1.15.1 was fetched 8631 times. Installers also
  serve auto-updates and our own mirror fetched every asset once, so these are not user counts
  <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^nh-manifest].
- **Early installers** are the largest (about 1.14-1.22 GB per release in 0.x; 128-200 MB `app.asar`)
  because of the SVG icon set and per-platform Qt runtimes, not debug material. No private keys, PEM
  blocks, crypto-library strings or source maps exist in any early installer
  <span class="tag static">STATIC</span> (our scan of the 0.0.1-0.1.1 installers).

## How the vendor named and staged it

- **Naming** (Kickstarter update 21, 2025-06-16): Naya Flow is the front end, Naya Core the bridge
  between Flow and the keyboard, Naya Firmware what runs on it; Core had been completely overhauled;
  "Naya Flow Version 1" was live with key remapping. In the release repository remapping first appears
  in 1.3.8 (2025-06-13: "custom key remapping", Press only, and a "completely redeveloped Naya Core"),
  three days before the update, so "Version 1" is the 1.3.x line <span class="tag doc">DOC</span>
  <span class="tag inferred">INFERRED</span> (the dates and the matching wording)[^ks-21].
- **Early stages**: Batch 0 testers (100 units, shipped mid-January 2025) got firmware with a default
  QWERTY layout, "No remapping support", "No modules support" and limited wireless, and the first Flow
  build could only flash the keyboard. The public builds agree: the UI vocabulary of 0.0.1-0.1.1
  (2025-03-19 to 2025-05-02) covers flashing, verifying and pairing only, and the 0.1.0 note
  (2025-05-01) still says only preloaded Tune configurations are supported; no note before 1.3.8
  mentions remapping <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^ks-19][^rel].
- **The stack as announced**: remapping "between our custom ZMK firmware and Naya Flow" (campaign page,
  2023-05); three layers, Naya Flow (the UI), the Core (drivers and plugins) and the Create firmware
  "based on a customized ZMK base" (update 9, 2023-12-07); every layer to hold 9 sublayers, 1 for the
  keyboard and 4 for each dock, stored on the board; profiles and layers exportable as JSON; no CLI at
  launch, an SDK and public API "eventually", license undecided (update 11, 2024-02-15). The FAQ
  answered that building and flashing custom ZMK layouts was not available "for now"
  <span class="tag doc">DOC</span>[^ks-page][^ks-9][^ks-11].
- **Why the schedule slipped** (the vendor's account): Naya left the contract manufacturer that had
  built every prototype in early 2024 (update 12, 2024-03-01), signed two new ones that prototyped in
  parallel, chose one in July 2024 (update 14, 2024-07-24), and later reckoned about a year was lost to
  the switch (update 25, 2025-09-11). Batch 0 (100 test units) shipped mid-January 2025; all Kickstarter
  pledges had shipped by 2025-09-11. NayaFlow's public releases (2025-03-19 on) all fall after the change
  <span class="tag doc">DOC</span>[^ks-12][^ks-14][^ks-19][^ks-25].
- The help-center pages the notes cite ("Input Source Selection JIS", "Force Flashing Naya Modules",
  "Default Templates v2 Update", "Module no longer turns ON: Battery Recovery", "Clearing Keymap Data",
  "Naya Create not typing after update") are gone: the host does not resolve and the Wayback Machine
  copies hold page shells only <span class="tag measured">MEASURED</span> (access checks, 2026-09-23).

## Open questions

- <span class="tag open">OPEN</span> Whether 1.19.1 or later shipped a Linux NayaCore ([details](../open-questions.md#oq-s09)).
- <span class="tag open">OPEN</span> Beta 1.10.0's NayaCore version; the keyboard firmware of the 0.0.x-1.11.11 images.
- <span class="tag open">OPEN</span> How the beta-only firmware (3.39.4, 3.40.0, 3.40.4) behaves on a board.
- <span class="tag open">OPEN</span> Whether the five component repositories other than NayaFlow-releases ever held anything ([details](../open-questions.md#oq-s12)).
- <span class="tag open">OPEN</span> Whether 1.6.10 already used ZeroMQ between UI and service ([details](../open-questions.md#oq-s13)).

## Sources

[^rel]: Vendor release notes, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases), mirrored in create-legacy-firmware [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases), read 2026-09-23.
[^nh]: create-legacy-firmware, [github.com/create-collective/create-legacy-firmware](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb) (`download.log`, `verify.py`, `firmware-history/`, `FIRMWARE-HISTORY.md`).
[^nh-manifest]: create-legacy-firmware, [`MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/MANIFEST.json) (GitHub release metadata of all 25 stable releases, captured 2026-09-14).
[^nh-changelog]: create-legacy-firmware, [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md).
[^nh-fhb]: create-legacy-firmware, [`firmware-history-beta/MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/firmware-history-beta/MANIFEST.json) and `FIRMWARE-HISTORY.md`, "Beta channel".
[^nh-fp]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md) ("Architecture and its evolution", "Firmware bundle layout").
[^nh-fp-binary]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Native service binary"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L107-L120).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) (text commands silent on 3.41.0).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5).
[^kb-versions]: naya-create-kb, [firmware/versions](https://nemezzizz.github.io/naya-create-kb/firmware/versions/).
[^ks-page]: Kickstarter campaign page, [description and FAQ](https://www.kickstarter.com/projects/naya-create/naya-create/description), read 2026-09-23.
[^ks-9]: Kickstarter update 9, [2023-12-07](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3982337).
[^ks-11]: Kickstarter update 11, [2024-02-15](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4029736).
[^ks-12]: Kickstarter update 12, [2024-03-01](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4041543).
[^ks-14]: Kickstarter update 14, [2024-07-24](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4157656).
[^ks-19]: Kickstarter update 19, [2025-02-11](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4312089).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^ks-25]: Kickstarter update 25, [2025-09-11](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4453988).

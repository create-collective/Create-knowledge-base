# Module firmware

The Touch, Track and Tune modules run their own firmware on their own microcontroller. This page
covers what runs in a module, how its firmware ships (the `FlashMemory.bin` bundle), where the
keyboard stores it, how NayaCore updates a module, the module recovery mode, the versions and what
they changed, and what is untested. The thing to know first: a module firmware update has never been
run outside the vendor as far as we know; the module recovery key, on the other hand, is measured and
revived two dead modules.

!!! note "At a glance"
    - Each module has an STM32F411 and no radio; its firmware is not an MCUboot image.
    - Module firmware ships as `FlashMemory.bin`: a 1 MiB LittleFS image of encrypted `.sfb` apps.
    - The keyboard stores the bundle on the **left** half and programs a docked module from it.
    - `de/100a` reads the stored bundle's version (left half only); `de/1008` reads a docked module's own version.
    - The System-layer recovery key force-charges a drained module and brought two back (3.28.7, module 2.1.2).

## What runs in a module

Each module (Touch, Track, Tune) has an ST STM32F411CEU6 microcontroller, a Maxic MT5705 Qi
receiver and a small LiPo cell; the boards expose SWD and boot-strap pads (`SWDIO`, `SWCLK`, `BOOT0`,
`BOOT1`, `RST`). Modules have no radio and no FCC ID of their own; they talk to the keyboard through
the dock contacts <span class="tag doc">DOC</span>[^parts]. The module microcontrollers moved from Holtek parts to the STM32F411
during development, for its resources, drivers, no license fees and machine-learning support
(Kickstarter update 13, 2024-05-08) <span class="tag doc">DOC</span>[^ks-13]. Hardware details: [Tune](../hardware/tune.md),
[Touch](../hardware/touch.md), [Track](../hardware/track.md), [Module dock](../hardware/dock.md).

Module firmware lives in the STM32's internal flash; no external memory was seen on the
module boards <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^parts].

The module's bootloader is unidentified. Module images are not MCUboot images, yet
NayaCore names module restart modes `M_NORMAL_RESTART`, `M_MCUBOOT_RESTART` and `M_CLEAR_REMAP_FLASH`
next to `MCUBootWorker_%1_PortTwo_Module`. Whether any key signs the module apps is **open**
<span class="tag static">STATIC</span> <span class="tag open">OPEN</span>[^nc] ([open question](../open-questions.md#oq-f09)).

## The bundle

From NayaFlow 1.11.0, every stable release ships module firmware as `FlashMemory.bin`
(Qt resource `m_fw/`): a 1 MiB (1 048 576-byte) LittleFS v2 image with 4 096-byte blocks (superblock
at offset `0x08`). It is not an MCUboot image: no MCUboot magic, no TLVs, no swap trailer
<span class="tag static">STATIC</span>[^fh].

It contains one encrypted app per module type (`Touch_UserApp.sfb`, `Track_UserApp.sfb`,
`Tune_UserApp.sfb`, `Float_UserApp.sfb`, `Query_UserApp.sfb`); from 1.15.0 a `<App>_HASH` file beside
each app (the SHA-256 of the `.sfb`, described as the value the Create reports for the app); and
from 1.14.3 a `VERSION` file of four bytes, `00 MM mm pp` <span class="tag static">STATIC</span>[^fh]. naya-create-kb also lists the
`.sfb` apps and their HASH files.

The `.sfb` payloads are encrypted (entropy about 7.98, no Cortex-M vector table): their
names and hashes are readable, their code is not <span class="tag static">STATIC</span>[^fh].

Float looks unreleased and Query deprecated or experimental, but both ship as apps in
every bundle; the Float app kept being rebuilt (157 184 bytes in 1.14.x, 85 440 in 1.17.2 to 1.21.0,
85 312 in 1.25.x) <span class="tag static">STATIC</span>[^fh].

`.sfb` sizes in bytes <span class="tag static">STATIC</span>[^fh]:

| Bundle | Touch | Track | Tune | Float | Query |
|---|---|---|---|---|---|
| 1.25.x (2.3.3) | 46 176 | 61 056 | 97 440 | 85 312 | 41 088 |
| 1.17.2 to 1.21.0 (2.3.2) | 46 304 | 61 184 | 97 728 | 85 440 | 41 216 |

## Versions

Module firmware by stable release: 1.11.x unknown (no `VERSION` file yet); 2.1.1 in 1.14.3;
2.1.2 in 1.14.5; 2.2.0 in 1.15.0 and 1.15.1; 2.3.2 in 1.17.2 to 1.21.0; 2.3.3 in 1.25.0 and 1.25.1.
On the beta channel 2.3.2 is first carried by beta 1.17.1 (2026-02-11; the 1.16.0 note announces it,
but betas 1.16.0 to 1.17.0 carry 2.2.0) and 2.3.3 by beta 1.23.0 (2026-05-21) <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^fh][^fhb][^cl][^beta].
What each version changed is on [Versions](versions.md#what-changed-by-version).

## Where the keyboard keeps the bundle

The keyboard keeps the bundle on the **left** half only, in a 1 MiB LittleFS partition
(candidate name `M_Firmware`), written by an SMP upload to direct id 4 (`slot3_partition`) while the
left half is in its bootloader. It is not an MCUboot slot and `image slot info` does not list it. The
right half has no module store: its flash self-test reports three partitions, the left's five
<span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-slots] (owner's board, 3.41.0, 2026-09-10 and 2026-09-16). See
[Flash layout](../storage/flash-layout.md).

`de/100a` MODULE_FILE_FW_VERSION reads the stored bundle's `VERSION` from the left half with
no module docked: `00 00 02 03 03` (2.3.3) on a board updated by NayaFlow 1.25.1. The right half never
answers it <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-16).

`de/1008` GET_MODULE_FW_VERSION reads a docked module's own running firmware on the half
it is docked on, either half. The reply is `00 <addr> <flag> 00 <major> <minor> <patch>`: status
`00`, the dock address, a flag byte, then the version with the vendor's leading zero. A right-docked
Touch at address `0x11` reported 2.1.2 on a 3.41.0 board <span class="tag measured">MEASURED</span> (owner's board, 2026-09). Third-party
captures show `00 11 00 00 02 03 03` (a Touch on the right, 2.3.3) and, while a module has not reported
yet, the flag `01` with an all-zero version (`00 11 01 00 00 00 00`) <span class="tag reported">REPORTED</span> (raw data checked: the
naya-create-kb maintainer's published captures; the nayactl maintainer reports the same layout[^nx-pr5]).
Details on [Modules](../protocol/modules.md).

## How NayaCore updates a module

!!! danger "Untested: never run outside the vendor as far as we know"
    Safety level HIGH (it rewrites the left half's module store and then reprograms a module).
    UNTESTED by us and, as far as we know, by anyone outside the vendor. First attempts belong on a
    donor board with the module docked on the left half. Do not send `de/1005`, `de/1006` or
    `fe/1003` by hand: their payloads are not known with certainty.

NayaCore's module update sequence, from the strings of `Naya_DeviceManager_ModuleFwUpdate.cpp`
<span class="tag static">STATIC</span>[^nc][^fp-slots]:

1. verify the file;
2. put the **left** half into its bootloader;
3. upload `FlashMemory.bin` to the modules target, id 4 (`uploadImageToModulesSlot` =
   `uploadImageToSlot(path, 4)`);
4. reset the half (no mark step and no swap: it is a filesystem);
5. send `de/1005` MODULE_FWUP with one byte naming the docked module type, so that the keyboard
   programs the module from its own store;
6. compare the module's reported version (`de/1008`) with the bundle's `VERSION`.

NayaCore's step names for it are ModuleFW_FileVerification, ModuleFW_FileVerificationPostUpload,
ModuleFW_Update, ModuleFW_VersionCheck, ModuleFW_Touch_Upload, ModuleFW_Track_Upload,
ModuleFW_Tune_Upload and ModuleFW_Read_Upload. It can force an update to Touch, Track or Tune, or read
the docked type ("Unknown, waiting for timeout" when none is docked); on a mismatch it logs "Module
firmware version image does not match stored module firmware version for device ..." <span class="tag static">STATIC</span>[^nc].

`de/1005` MODULE_FWUP takes one byte: NayaCore's validation requires a size of 1, and an
invalid type falls back to AUTO_DETECT <span class="tag static">STATIC</span>. The value table is uncertain: nayactl's module types give
1 Touch, 2 Track, 3 Tune, while the keyboard's module-configuration list uses 0 Touch, 1 Track,
2 Tune <span class="tag inferred">INFERRED</span>[^nx]. We have never sent it.

Host events: NayaFlow sends the ZMQ event `update_module_fw`, and NayaCore also accepts
`force_touch_start`, `force_track_start` and `force_tune_start` <span class="tag static">STATIC</span>[^nc]. The old text commands
`manual_fw_update_touch`, `_track` and `_tune` and `force_touch_start` belonged to the engineering
text channel, retired in 3.31.1; every text command returns nothing on 3.41.0 <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span>[^nx-pr2].
Whether a forced module update from NayaFlow works on 3.41.0 has not been tested
([open question](../open-questions.md#oq-f24)). naya-create-kb also lists `update_module_fw` among
NayaCore's ZMQ events.

An interrupted bundle upload would leave the modules partition partly erased and the
keyboard firmware untouched, because the keyboard's image slots are not involved <span class="tag inferred">INFERRED</span>.

The vendor's rules for module updates (NayaFlow text): only one up-to-date left half, with
the module docked; the module switched on; a module can take up to 7 s to appear, and a Tune up to a
minute the first time; a forced update can take up to 4 minutes. "Force update", in the Danger Zone,
is meant for a module that does not answer after Battery Recovery was tried: pick the module type that
is physically docked, and expect the keyboard and the module to restart several times <span class="tag doc">DOC</span>[^nc-flow].
More on the host side: [NayaFlow and NayaCore](../software/nayaflow.md).

## Force Module Update

Force Module Update arrived with NayaFlow 1.15.0, NayaCore 5.8.1, keyboard 3.29.1 and
modules 2.2.0. The vendor's help page "Force Flashing Naya Modules" is no longer reachable; only its
first line ("NayaFlow v1.16.x to 1.17.x and later") survives in the Wayback Machine <span class="tag doc">DOC</span>[^cl-331][^wb-help].

Vendor fixes to the update path: 3.29.1 "Module update method to prevent wrong firmware
from being installed"; NayaCore 6.1.3 handles a corrupted module firmware file on the Create; 3.40.4
module updates no longer fail unless the LED effect is Solid <span class="tag doc">DOC</span>[^cl][^beta].

## Module recovery mode

Module recovery mode is a System-layer key: `LA5` is labeled "Module Force Charge" in the
Windows default layout and "Module Recovery Mode" in the macOS default (manual v1.1.0, pp. 20 and 23)
<span class="tag doc">DOC</span>[^man-create]. On the wire it is a record of type `06` with parameter 401 (MODULE_FORCE_CHARGING);
the stock System layer holds `3e 06 04 91 01 00 00` at position 62 <span class="tag measured">MEASURED</span> (owner's board, 2026-09-08).

!!! note "Recovery key: Safety LOW, tested on 3.28.7 with modules on 2.1.2"
    It changes nothing stored. While it runs, that half's LEDs are out and the module does not work;
    it ends by itself. TESTED by us on 3.28.7 with modules on 2.1.2 (2026-09-19); untested on 3.41.0
    and module 2.3.3.

Behavior, measured on 3.28.7 with modules on 2.1.2: the key acts only on the half it is
pressed on (bind one per side); it puts that half's LEDs out and force-charges its bay; the module
does not work while the mode is active; the mode times out on its own, so it cannot run overnight (Qi
charging is the long-charge option); a restart clears it <span class="tag measured">MEASURED</span> (owner's board, 2026-09-19).

On 2026-09-19 recovery mode revived a Tune and a Touch that no longer answered: the Tune's
LED came back and the Touch moved the cursor. Hours on a Qi charger had not helped <span class="tag measured">MEASURED</span>.

The module manuals (v1.1.0): a module that will not charge may need to be "manually
recovered using the Recovery Mode" keybinding; modules left docked for a long time can drain until
the battery protection trips and leaves them unable to charge until recovered by hand; undock modules
for long storage; do not connect the Create directly to a wall outlet (charge from a computer, USB
3.0, 5 V 1 A) <span class="tag doc">DOC</span>[^man-modules][^man-create].

The vendor's history of the problem: "Battery Zero", a rare bug that can drain modules
beyond recovery. The vendor planned fixes in firmware plus minor hardware changes, and a recovery
mode for drained modules (Kickstarter update 21, 2025-06-16); NayaFlow 1.3.8 shipped "module recovery
support for battery Zero" <span class="tag doc">DOC</span>[^ks-21][^cl-421].

A dead-module rescue command exists in the configuration protocol: SYSTEM `fe/1003`
MODULE_BATTERY_RECOVERY (NayaCore's `MODULE_BAT_RECOVERY`). Its payload is unknown and we have never
sent it; the same holds for RESET_MODULE `de/1006` <span class="tag static">STATIC</span>[^nx][^nc].

## Known module-firmware problems

A module at about 0 to 1 % on dock power reports dock address `0xF0` or `0xF1`, firmware
0.0.0 and no battery until it charges past about 1 % <span class="tag reported">REPORTED</span>[^nx-pr2]. On the owner's boards `0xF0` means
that no module answered (3.41.0, 2026-09-03; 3.28.7, 2026-09-19), and OpenFlow treats it as "no
answer" <span class="tag measured">MEASURED</span>; the link to the battery level is the nayactl maintainer's.

Keyboard 3.28.7 with modules on 2.1.2: modules can end up with their LEDs off and not
working while still powering the keyboard, the Tune especially; charging does not fix it; the recovery
key did (above), and a later firmware plus Force Module Update is the vendor's cure <span class="tag measured">MEASURED</span> (owner's
board, 2026-09-19).

Module 2.1.2 does not implement GET_PRECISE_BATTERY (`de/100b`: about 1.09 s timeout per
request; `de/1009` works), and a Tune on 2.1.2 colors only 6 of its 24 bay LED indices (88 to 93; 94 to
111 stay white) <span class="tag measured">MEASURED</span> (owner's board, 2026-09-19).

The vendor's module battery history: 3.35.4 module battery management; NayaCore 6.1.3
corrected battery reporting; 6.6.1 re-enabled module battery reading; NayaFlow 1.20.0 shows module
battery percentages, with "fluctuations between 5 and 10 percent"; module 2.3.3 disabled the battery
blink <span class="tag doc">DOC</span>[^cl][^beta]. The percentage NayaFlow shows is
`(clamp(mV, 3300, 4200) - 3300) * 100 / 900`, truncated, then clamped to 1-100 %, from the `de/100b`
millivolts <span class="tag static">STATIC</span> (NayaCore 6.11.0, `Naya_Device::getModuleBatteryPercentage`)[^nc];
naya-create-kb's slope estimate of about 9.3 mV per percent is close, but the exact slope is 9 mV.
Readings and calibration points: [Power and batteries](../hardware/power.md#percentages).

## Before the bundle: `d_fw.bin`

Before the bundle (NayaFlow 0.1.0 to 1.6.10) the releases shipped `d_fw.bin`, an MCUboot
image signed with the keyboard key: dial or dongle firmware, **open**. From 1.11.0 create-legacy-firmware
describes the dial as folded into the modules bundle <span class="tag static">STATIC</span> <span class="tag open">OPEN</span>[^fh][^fp-bundle]
([Images](images.md#other-image-families)).

## The vendor's help pages

The vendor's help center had module troubleshooting pages whose bodies are lost: "Force
Flashing Naya Modules", "Module no longer turns ON: Battery Recovery", "Modules not outputting
anything after NayaCreate update" and "Naya Create not typing after update". Only their titles and
first lines survive in the Wayback Machine's index <span class="tag doc">DOC</span>[^wb-help].

## Tested and untested

A module firmware update has not been run on hardware by us; OpenFlow has it wired and
switched off (status 2026-09-23) <span class="tag measured">MEASURED</span>. naya-create-kb also reports that `update_module_fw` was never
exercised live <span class="tag reported">REPORTED</span>[^kb-versions] (raw data checked: its maintainer's published tools and captures
name the module-update commands but never send them). Tested: the recovery key (3.28.7 with modules on 2.1.2), the
version reads (`de/100a`, `de/1008`).

## Where this differs from naya-create-kb

| naya-create-kb says | What the evidence shows |
|---|---|
| Module firmware ships only up to NayaFlow 1.6.10, and releases from 1.15 on carry none (versions page) | `FlashMemory.bin` ships in every stable release from 1.11.0, with modules 2.1.1 to 2.3.3 |
| The 175 136-byte image is the module firmware (versions, signing) | That is `d_fw.bin`, dial or dongle firmware |
| One signing key covers the Track, Tune and Touch modules (signing) | Module apps are `.sfb` files, not MCUboot images; their signing is open |
| The module bundle and its HASH files sit on each half (littlefs) | Only the left half stores the bundle |

## Open questions

- <span class="tag open">OPEN</span> The `de/1005` module-type byte table, and the payloads of MODULE_BATTERY_RECOVERY (`fe/1003`) and RESET_MODULE (`de/1006`).
- <span class="tag open">OPEN</span> The module microcontroller's bootloader, and whether any key signs the `.sfb` apps ([details](../open-questions.md#oq-f09)).
- <span class="tag open">OPEN</span> Whether recovery mode behaves the same on 3.41.0 with modules on 2.3.3, and how long it runs before it ends ([details](../open-questions.md#oq-f22)).
- <span class="tag open">OPEN</span> Whether a Tune on 2.3.3 drives more than 6 of its 24 bay LED indices.
- <span class="tag open">OPEN</span> The module version of the 1.11.x bundle ([details](../open-questions.md#oq-f12)).
- <span class="tag open">OPEN</span> Whether `d_fw.bin` is dial or dongle firmware ([details](../open-questions.md#oq-f08)).
- <span class="tag open">OPEN</span> The module-bundle flash itself (`image: 4`, then `de/1005`) on a donor ([details](../open-questions.md#oq-f13)).

## Sources

[^parts]: [Parts list](../hardware/parts.md): FCC internal photos of the Tune, Touch and Track boards (exhibits of 2BQ4V0825CRL and 2BQ4V0825CRR).
[^ks-13]: Kickstarter update 13, [2024-05-08](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4061393).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (module restart modes, `Naya_DeviceManager_ModuleFwUpdate.cpp` step names and messages, `MODULE_BAT_RECOVERY`, ZMQ events) and macOS symbols and code (`Naya_Device::getModuleBatteryPercentage`, our disassembly, 2026-09-23).
[^nc-flow]: NayaFlow 1.25.1, renderer strings (Hardware Manager module-update texts).
[^fh]: create-legacy-firmware, [`FIRMWARE-HISTORY.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FIRMWARE-HISTORY.md) and the per-release `manifest.json` files (module bundle entries and `.sfb` apps).
[^fhb]: create-legacy-firmware, [`firmware-history-beta/MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/firmware-history-beta/MANIFEST.json) (the `VERSION` file of each beta bundle).
[^fp-slots]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Slot ids, vendor-exact"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L158-L195).
[^fp-bundle]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Firmware bundle layout"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L124-L138).
[^cl]: create-legacy-firmware, [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md) (vendor release notes).
[^cl-331]: create-legacy-firmware, [`CHANGELOG.md` L331-L351](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L331-L351) (Force Module Update in NayaFlow 1.15.0, NayaCore 5.8.1, keyboard 3.29.1, modules 2.2.0).
[^cl-421]: create-legacy-firmware, [`CHANGELOG.md` L421](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L421) (NayaFlow 1.3.8).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).
[^wb-help]: Wayback Machine index of the vendor's help center, [help.naya.tech captures](https://web.archive.org/web/2026*/help.naya.tech/*) (titles and first lines only).
[^man-create]: Naya Create User Manual v1.1.0, pp. 11, 20 and 23; see [Manuals](../product/manuals.md).
[^man-modules]: Naya Touch, Tune and Track User Manuals v1.1.0, pp. 5 and 7; see [Manuals](../product/manuals.md).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py`: module types, `fe/1003`, `de/1006`).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2), comments by the maintainer (text commands silent on 3.41.0; a module at 0 to 1 % reporting `0xF0`).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) (module version replies).
[^kb-versions]: naya-create-kb, [firmware/versions](https://nemezzizz.github.io/naya-create-kb/firmware/versions/).

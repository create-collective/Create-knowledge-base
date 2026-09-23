# Firmware images

This page describes what a stock Create keyboard firmware image is at the structural level: an
encrypted, signed MCUboot image, shipped inside the vendor's NayaCore service as a whole flash slot
with a swap trailer already written. It covers where the images ship, how they are signed and
encrypted, the two flash generations, and how to name the image a half is running, without ever
needing an image's bytes. The one thing to know before anything else: every stock upload is a
**permanent** swap. There is no trial boot and no automatic revert.

!!! warning "Correction: stock images do not boot on trial and do not revert automatically"
    naya-create-kb's signing page says that a newly uploaded image boots on trial, that the
    bootloader reverts to the old image automatically if the new one fails or crashes before
    confirming itself, and that firmware experiments are therefore safe on a daily driver. That
    does not hold on the Create. Every stock resource carries a pre-written MCUboot swap trailer, so
    the upload itself arms a **permanent** swap, and the bootloader refuses `image state` writes
    (rc 8, not supported), so a test swap cannot be requested at all
    <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-trailer][^fp-measured]. A signed image that boots badly stays in the primary slot;
    the way back is another serial-recovery upload, not a reboot. See
    [Flashing](flashing.md#there-is-no-test-mode) and [Bootloader](bootloader.md#what-the-bootloader-does-not-offer).

!!! note "At a glance"
    - Standard MCUboot images: 512-byte header, AES-128 encrypted payload, four TLVs.
    - One signing key for every MCUboot image Naya ever shipped, stable and beta channels alike.
    - Each resource is a whole 648 KiB slot (663 552 bytes) with a pre-armed permanent-swap trailer.
    - Two flash generations: plain file names are generation A, `_64` names are generation B; the
      USB product id decides which one a half takes.
    - The plaintext SHA-256 in each image is what the bootloader reports, so it names what a half runs.

## Where the images ship

The images are not files in the NayaFlow install tree and not in `app.asar`. They ship
inside the native service binary (NayaCore; earlier `naya_core_fw_service` and `naya_core_project`)
as Qt resources, each blob preceded by its length as a big-endian 32-bit integer. An early belief
that NayaFlow bundled no firmware came from scanning `app.asar` only <span class="tag static">STATIC</span>[^fp-bundle][^carve].

The Qt resource path changed over the product's life, and so did the uploader that went
with it <span class="tag static">STATIC</span>[^fp-bundle][^fp-transport]:

| NayaFlow releases | Resource path | Keyboard images | Other firmware | Uploader |
|---|---|---|---|---|
| 0.0.1 to 0.0.2 | `:/resources/includes/kbfw/` | `fwl.bin`, `fwr.bin` | none | bundled `newtmgr` |
| 0.1.0 to 1.6.10 | `:/resources/includes/kb_fw/` + `d_fw/` | `kb_fwl.bin`, `kb_fwr.bin` | `d_fw.bin` | bundled `newtmgr` (`nmgr_win/newtmgr.exe`, `nmgr_mac/newtmgr`) |
| 1.11.0 to 1.14.5 | `:/resources/includes/kb_fw/` + `m_fw/` | `kb_fwl.bin`, `kb_fwr.bin` | `FlashMemory.bin` (module bundle) | NayaCore's own SMP client |
| 1.15.0 to 1.25.1 | `:/resources/Includes/...` (capital I) | as above, plus `_64` from 1.25.0 | `FlashMemory.bin` | NayaCore's own SMP client |

NayaFlow 1.25.0 and 1.25.1 carry five firmware resources: `kb_fwl.bin`, `kb_fwr.bin`,
`kb_fwl_64.bin`, `kb_fwr_64.bin` and `m_fw/FlashMemory.bin` <span class="tag static">STATIC</span>[^fp-bundle][^fh].

The Windows and macOS builds of a release embed byte-identical images. The Linux NayaCore
shipped in 1.15.0, 1.15.1, 1.17.2 and 1.17.3 is the exception: it embedded the older 1.14.5 images
(keyboard 3.28.7, module 2.1.2) while Windows and macOS shipped newer ones <span class="tag static">STATIC</span>[^fh][^fp-binary].

No release contains a recovery, factory or bootloader image; only application images ship
<span class="tag static">STATIC</span>[^fh].

## Anatomy of a keyboard image

Every keyboard image is a standard MCUboot image: header magic `0x96f3b83d`, header size
512 bytes (`0x200`) <span class="tag static">STATIC</span>[^fh][^carve]. The header's flags word is `0x00000004`
(`IMAGE_F_ENCRYPTED_AES128`) on every keyboard image <span class="tag static">STATIC</span>[^fh][^secret].

The header's version field is the placeholder `1.2.3+4` in every image, beta images
included, so an image does not state its own firmware version. The version comes from the vendor's
release notes and, from NayaFlow 1.25.0 (beta 1.22.0), from the app constant
`NAYA_CREATE_FW_VERSION` ("3.41.0" in 1.25.1, beside `NAYA_MODULE_FW_VERSION` "2.3.3")
<span class="tag static">STATIC</span>[^fhb][^nc].

The payload is encrypted: AES-128 in counter mode, as MCUboot's image format specifies,
with a measured entropy of about 7.997 bits per byte. Even the first public images (NayaFlow 0.0.1)
are encrypted: their first payload bytes are not a Cortex-M vector table. No plaintext keyboard
firmware was ever shipped <span class="tag static">STATIC</span>[^secret].

After the payload comes the TLV area (info magic `0x6907`; tools also accept the
protected-TLV magic `0x6908`, which these images do not use). It holds four TLVs, in this order in
the file <span class="tag static">STATIC</span>[^carve]:

| Type | Name | Length | What it holds | Secret? |
|---|---|---|---|---|
| `0x10` | SHA256 | 32 bytes | SHA-256 of the **decrypted** image (header and plaintext payload) | no: it is what the bootloader reports for a slot |
| `0x01` | KEYHASH | 32 bytes | hash of the signing **public** key | no: a public identifier |
| `0x20` | RSA2048_PSS | 256 bytes | the RSA-2048-PSS signature | no |
| `0x30` | ENC_RSA2048 | 256 bytes | this image's AES key, wrapped with RSA-2048-OAEP | no: only the bootloader can unwrap it |

Header plus TLV overhead is exactly 1 108 bytes in every keyboard and `d_fw.bin` image:
512 (header) + 596 (TLV area: a 4-byte info header, 36 for KEYHASH, 36 for SHA256, 260 for the
signature, 260 for the wrapped key) <span class="tag static">STATIC</span>[^fh]. We re-parsed the headers, TLVs and trailers of the
stable, beta and `d_fw.bin` images on 2026-09-23 and found the same layout in each.

A resource (the file NayaCore uploads) is laid out like this <span class="tag static">STATIC</span>[^fp-trailer][^fh][^fhb]:

| Offset | Bytes | Content |
|---|---|---|
| 0 | 512 | MCUboot header (magic, sizes, flags `0x4`, version `1.2.3+4`) |
| 512 | `img_size` | encrypted payload |
| 512 + `img_size` | 596 | TLV area |
| after the TLVs | up to offset -24 | `0xff` fill |
| -24 | 1 | `image_ok` = `0x01` |
| -16 | 16 | BOOT_MAGIC `77 c2 95 f3 60 d2 ef 7f 35 52 50 0f 2c b6 79 80` |

`copy_done` and `swap_info` are left unset. The same trailer is in all 27 MCUboot images of the 25
stable releases and in the 6 beta-only keyboard images <span class="tag static">STATIC</span>[^fh][^fhb].

## The three sizes

Three sizes are easy to confuse <span class="tag static">STATIC</span>[^fh]:

| Size | Example (3.41.0 left, generation A) | Meaning |
|---|---|---|
| `img_size` | 328 880 | the payload length in the MCUboot header |
| MCUboot image length | 329 988 | `img_size` + 1 108 (header and TLVs) |
| resource | 663 552 | the whole slot, trailer included; what is uploaded |

Tables that list "image sizes", including ours on [Versions](versions.md), usually mean `img_size`.

Every keyboard resource in all 25 stable releases is 663 552 bytes (648 KiB, `0xA2000`),
exactly the size of the bootloader's primary and secondary slots; the `d_fw.bin` resource is
331 776 bytes (324 KiB, `0x51000`) <span class="tag static">STATIC</span>[^fh]. The slot size itself was read from a half in its
bootloader with `image slot info` (owner's board, 3.41.0, 2026-09-16) <span class="tag measured">MEASURED</span>[^fp-slots].

## The swap trailer: every stock upload is permanent

The consequence of that trailer: once the whole resource lands in the **secondary** slot,
MCUboot's swap table (secondary magic good and `image_ok` set) schedules a **permanent** swap on the
next boot. Nothing has to "mark" the image, and a later mark would be a no-op
<span class="tag static">STATIC</span>[^fp-trailer][^mcuboot]. Both halves of the owner's board showed it: after each upload the new
image was already in slot 0 and the replaced one in slot 1, on 3.35.4 to 3.41.0 on 2026-09-20, and
across six uploads in both directions between 2026-09-20 and 2026-09-22 <span class="tag measured">MEASURED</span>[^fp-measured]. There is
no trial boot and no automatic revert for a stock-style upload; the bootloader also refuses the
`image state` write that could request a test swap ([Bootloader](bootloader.md#what-the-bootloader-does-not-offer)).

What protects a half is MCUboot's own signature check: an image that fails it is never swapped in
([Flashing](flashing.md#the-two-risk-windows)).

## Signing

One signing key signs every MCUboot image of the 25 stable releases (the 26 keyboard
images of both flash generations and the `d_fw.bin` image) and the 6 beta-only keyboard images. Its
KEYHASH is `de8b07187913e6e788306618e4166e38a8c2eda99b68970d17fd00e75fd5b972`. The KEYHASH is the hash
of the signing **public** key: a public identifier, not a secret and not a decryption key
<span class="tag static">STATIC</span>[^fh][^fhb]. naya-create-kb reports the same value for the 15 images its maintainer carved.

The keys are Naya's own: we checked the images with imgtool against the published sample
keys of MCUboot, Nordic and Zephyr, and none matches <span class="tag static">STATIC</span>.

Because every stock image is signed by the key the bootloader already trusts, any stock
image can be flashed, older ones included: a downgrade is an ordinary flash <span class="tag static">STATIC</span>. It has been done:
the left half of the owner's board went from 3.41.0 to 3.35.4 (whole resource, 59.8 s upload,
2026-09-20), and both halves were then flashed in both directions <span class="tag measured">MEASURED</span>.

Scale: across the 25 stable releases there are 63 distinct firmware files: 26 keyboard
MCUboot images (both generations), 1 `d_fw.bin` MCUboot image, 6 distinct LittleFS module bundles
and 30 `.sfb` module apps. The beta channel adds 6 keyboard images (three beta-only left and right
pairs); its other 41 carried images are byte-identical copies of stable images (39) or repeats of an
earlier beta (2) <span class="tag static">STATIC</span>[^fh][^fhb]. naya-create-kb's "15 stock images" is one carve of six releases.

## Encryption

Each image has its own AES content key: the `ENC_RSA2048` TLVs of all images differ
<span class="tag static">STATIC</span>[^secret].

The host never holds a key. No installer of any release contains PEM blocks, private
keys or crypto-library strings; NayaCore uploads the encrypted resource as it is, and the bootloader
verifies the signature and decrypts the payload on the device, during the swap
<span class="tag static">STATIC</span>[^fp-bottom][^secret]. That is why stock firmware can be flashed without any key.

In MCUboot, encryption is a per-image header flag, so the format itself allows a signed
but unencrypted image <span class="tag doc">DOC</span>[^mcuboot]. Whether this bootloader would boot one is unknown and cannot
be tested without Naya's signing key <span class="tag inferred">INFERRED</span>. naya-create-kb states that such an image would boot;
that stays its report <span class="tag reported">REPORTED</span>[^kb-signing] ([open question](../open-questions.md#oq-f10)).

With MCUboot's RSA key wrapping, the **private** key that unwraps each image's AES key
lives inside the bootloader, and an image builder needs only the matching public key <span class="tag inferred">INFERRED</span>[^mcuboot].
naya-create-kb says the encryption public key would have to be recovered from a bootloader dump;
that wording mixes up which half of the pair is where. Recovery methods are out of scope for this site.

## Flash generations A and B

`_64` means flash **generation B**. It is not a word size and not a "dual-bank slot":
`kb_fwl_64.bin` is the **left** image (`img_size` 328 880) and `kb_fwr_64.bin` the **right** image
(226 000). Files without the suffix are generation A <span class="tag static">STATIC</span>[^fh].

NayaCore picks the image from the half's USB product id
(`Naya_Device::setCreateFlashGenerationFromPid`: bit `0x1000` of the PID set means generation B),
refuses to flash when the generation is unknown, and logs a mismatch when a stored generation
disagrees with the PID <span class="tag static">STATIC</span>[^fp-pid]. The PID table is on [Bootloader](bootloader.md#usb-identity).

Each physical half therefore matches exactly one of the four current images (left or
right, generation A or B); the four are not interchangeable <span class="tag static">STATIC</span>[^fh][^fp-pid].

Generation A and B images of one side have the same `img_size` but different plaintext
hashes. Generation B images first ship in NayaFlow 1.25.0 (2026-07-17), and only with keyboard
3.41.0. The vendor's note for NayaCore 6.11.0 calls them "64-bit Create Firmware Updates" (support
for updating 64-bit Create left and right firmware images); the beta release title misprints it as
"4-bit" <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^fh][^cl-113][^beta].

What physically distinguishes generation-B hardware is unknown. The nRF52840 is a 32-bit
part, so "64-bit" cannot be a word size; a larger QSPI flash part (for example 64 Mbit) is a guess.
No generation-B half has been measured by anyone we know of; all three of the owner's boards are
generation A <span class="tag inferred">INFERRED</span> ([open question](../open-questions.md#oq-f06)).

## Naming the image a half runs

TLV `0x10` (the plaintext SHA-256) is exactly what the bootloader's `image state` read
reports for each slot. Matching it against a table of stock images names the side, the generation
and the firmware version without trusting the USB product id <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>. Measured on the owner's board:
slot 0 matched `kb_fwl.bin` of 3.41.0 (2026-09-01), and both halves matched after the 2026-09-20
flashes[^fp-measured][^fh].

The four 3.41.0 images <span class="tag static">STATIC</span>[^fh]:

| File | Side | Generation | `img_size` | Plaintext SHA-256 | Matched on hardware |
|---|---|---|---|---|---|
| `kb_fwl.bin` | left | A | 328 880 | `479e89ba6c92ead9c46d1228d5033437caf63d72db89364081b9b0a321b31283` | yes <span class="tag measured">MEASURED</span> |
| `kb_fwr.bin` | right | A | 226 000 | `2abb2695b9b6e94883553e101ea5edb8e1934e3919d62b14e589331fe9f5bcfc` | yes <span class="tag measured">MEASURED</span> |
| `kb_fwl_64.bin` | left | B | 328 880 | `07dd2523bf87ee1385fdfb4dbaacd57c8f928e3751306a3e63eac748b2454297` | no |
| `kb_fwr_64.bin` | right | B | 226 000 | `87f63fd3be514538f099803c0912516a54bbb256facf2c50df6c0c85c16a6677` | no |

Every other release's hashes are on [Versions](versions.md#distinct-keyboard-images) and, in full,
in nayaHistory's per-release `manifest.json` files.

!!! note "How to name what a half runs"
    Put the half into its bootloader, read `image state` on the port that answers SMP, and look up
    the slot 0 hash in the table. Slot 1 holds the image the last update replaced. The procedure and
    the read-only probe are on [Bootloader](bootloader.md#naming-what-a-half-runs).

## Other image families

`d_fw.bin` (NayaFlow 0.1.0 to 1.6.10) is a separate MCUboot image family: encrypted,
`img_size` 175 136, MCUboot length 176 244, in a 331 776-byte resource, signed with the same KEYHASH
and carrying the same pre-armed trailer <span class="tag static">STATIC</span>[^fh]. nayaHistory calls it the "dial" image. It arrived
in 0.1.0 together with dongle upgrade commands (`mcb_dongle_*`, `dongle_upgrade_mcb_*`) and the
vendor's slot-5 reservation for the dongle, so it may be dongle firmware <span class="tag inferred">INFERRED</span>[^fp-bottom][^cl-453].
Which one it is stays **open** <span class="tag open">OPEN</span> ([open question](../open-questions.md#oq-f08)). It is not the
module firmware.

Module firmware is not an MCUboot image at all. From NayaFlow 1.11.0 it ships as
`FlashMemory.bin`, a 1 MiB LittleFS image with no MCUboot magic, no TLVs and no trailer, holding
encrypted `.sfb` module apps (see [Module firmware](modules.md)) <span class="tag static">STATIC</span>[^fh]. Whether any key signs
the `.sfb` files is **open** <span class="tag open">OPEN</span> ([open question](../open-questions.md#oq-f09)).

## Custom firmware: consequences only

This section states consequences. It does not describe, and this site does not publish, any method
to read, bypass or extract keys.

Self-built firmware cannot boot through the stock bootloader: MCUboot verifies the
RSA-2048-PSS signature against Naya's key before it swaps an image in. The two routes are Naya's
signing key or replacing the bootloader over SWD <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^fp-bottom][^fh].

What an SWD mass erase would cost: the carved stock images are encrypted, and the only key
that unwraps them is inside the stock bootloader. An erase (the only SWD action available if the
debug port is locked) removes that key, so the stock images could never be restored from the
archive afterwards <span class="tag inferred">INFERRED</span>. Whether shipped halves have the debug port locked (APPROTECT) is **open**
<span class="tag open">OPEN</span> ([details](zmk.md#the-gate-the-signed-bootloader)).

## Beta-channel images

The beta channel's images are carved into nayaHistory's `firmware-history-beta/` folder
(commit 7b511ca). The three keyboard firmwares that shipped only on the beta channel, 3.39.4, 3.40.0
and 3.40.4, are stored as `kb_fwl.bin` and `kb_fwr.bin` pairs: `img_size` 327 008 to 327 808 (left)
and 224 464 to 225 024 (right), generation A only, the same KEYHASH, the same header placeholder and
the same pre-armed permanent-swap trailer. Beta 1.10.0 carries no image. The beta tree is kept apart
from `firmware-history/`, which is the only tree OpenFlow's firmware fetcher and catalog read
<span class="tag static">STATIC</span>[^fhb][^fh-beta]. Per-version sizes and hashes are on [Versions](versions.md#the-beta-channel).
The beta carve found nothing that changes a statement on this page about the stable channel.

## How this was established

The archive was built from the public installers, and anyone can re-derive it: find the
MCUboot magic `0x96f3b83d` in the NayaCore binary (header size 32 or 512), walk the TLVs, and bind Qt
RCC resource names to blobs (a name entry is a 16-bit length, a 32-bit hash and a UTF-16BE name; a
file node holds the name offset as a big-endian 32-bit value at +0 and the data offset at +10; the
data is preceded by a big-endian 32-bit length). nayaHistory's `tools/carve_fw.py` and
`tools/extract_history.py` do this for every release <span class="tag static">STATIC</span>[^carve]. The images themselves are hosted in
nayaHistory, whose Apache-2.0 license covers its own documents, manifests and tools, not the vendor
firmware images or installers it archives. This page publishes structure, sizes and hashes only.

## Where this differs from naya-create-kb

| naya-create-kb says | What the evidence shows |
|---|---|
| New images boot on trial and revert automatically if they fail; experiments are safe on a daily driver; the worst case of a bad build is one extra reboot (signing page) | Stock uploads arm a permanent swap and a test swap cannot be requested; a bad signed image stays until another upload (warning above) |
| The 175 136-byte image is the module image, signed with the keyboard key (signing, versions) | It is `d_fw.bin`, dial or dongle firmware; module firmware ships as `.sfb` files in a LittleFS bundle, not as MCUboot images |
| One key signs the halves and the Track, Tune and Touch modules (signing) | True for every MCUboot image; whether any key signs the module `.sfb` files is open |
| `_64` images are dual-bank slots introduced in 1.25.1; 328 880 pairs with `fwr_64` (versions) | `_64` is flash generation B, first in 1.25.0; `kb_fwl_64.bin` (328 880) is the left image |
| The encryption public key must be recovered from a bootloader dump (signing) | The bootloader holds the private unwrap key; a builder needs the public half |
| All 15 stock images carry one KEYHASH (signing) | The same KEYHASH is in all 27 stable MCUboot images and all 6 beta-only images |

## Open questions

- <span class="tag open">OPEN</span> What physically distinguishes generation B, and how a generation-B half behaves ([details](../open-questions.md#oq-f06)).
- <span class="tag open">OPEN</span> Whether `d_fw.bin` is dial or dongle firmware ([details](../open-questions.md#oq-f08)).
- <span class="tag open">OPEN</span> The module MCU's bootloader, and whether any key signs the `.sfb` apps ([details](../open-questions.md#oq-f09)).
- <span class="tag open">OPEN</span> Whether this bootloader accepts a signed but unencrypted image; untestable without the key ([details](../open-questions.md#oq-f10)).
- <span class="tag open">OPEN</span> Whether shipped halves have the debug port locked (APPROTECT) ([details](../open-questions.md#oq-h05)).
- <span class="tag open">OPEN</span> The firmware versions of the images in NayaFlow 0.0.1 to 1.11.11, whose headers carry only the placeholder ([details](../open-questions.md#oq-f12)).

## Sources

[^fh]: nayaHistory, [`FIRMWARE-HISTORY.md`](https://github.com/traviswye/nayaHistory/blob/79eeefb/FIRMWARE-HISTORY.md) (catalog of every carved image with sizes, generations and plaintext hashes) and the per-release `firmware-history/<version>/manifest.json` files.
[^fh-beta]: nayaHistory, [`FIRMWARE-HISTORY.md`, "Beta channel"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FIRMWARE-HISTORY.md#L153-L218).
[^fhb]: nayaHistory, [`firmware-history-beta/MANIFEST.json`](https://github.com/traviswye/nayaHistory/blob/79eeefb/firmware-history-beta/MANIFEST.json) (commit 7b511ca): every beta release and every image it carried, with `img_size`, plaintext SHA-256, KEYHASH, header version and trailer.
[^carve]: nayaHistory, [`tools/carve_fw.py`](https://github.com/traviswye/nayaHistory/blob/79eeefb/tools/carve_fw.py) and [`tools/extract_history.py`](https://github.com/traviswye/nayaHistory/blob/79eeefb/tools/extract_history.py).
[^fp-bundle]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Firmware bundle layout"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L124-L138).
[^fp-transport]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Transport to the device"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L82-L95).
[^fp-binary]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Native service binary"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L107-L120).
[^fp-bottom]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Bottom line"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L16-L32) and "Command vocabulary by era" (L140-L154).
[^fp-slots]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Slot ids, vendor-exact"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L158-L195).
[^fp-trailer]: nayaHistory, [`FLASHING-PROCEDURE.md`, "The resource is a whole slot, trailer included"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L197-L226) (flow corrected in commit 6ef80e2).
[^fp-pid]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Product ids, vendor-exact"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L228-L248) (NayaCore 6.11.0, `Naya_Device::setCreateFlashGenerationFromPid`).
[^fp-measured]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384) (added in commit cdd897c).
[^secret]: nayaHistory, [`SECRET-HUNT.md`, "Findings" sections 1 to 3](https://github.com/traviswye/nayaHistory/blob/79eeefb/SECRET-HUNT.md#L80-L116) (encryption flag, entropy, per-image wrapped keys, no key material in any installer).
[^nc]: NayaFlow 1.25.1, main-process bundle: `NAYA_CREATE_FW_VERSION` "3.41.0" and `NAYA_MODULE_FW_VERSION` "2.3.3".
[^cl-113]: nayaHistory, [`CHANGELOG.md` L113](https://github.com/traviswye/nayaHistory/blob/79eeefb/CHANGELOG.md#L113) (vendor release notes, NayaFlow 1.25.0, NayaCore 6.11.0).
[^cl-453]: nayaHistory, [`CHANGELOG.md` L453-L455](https://github.com/traviswye/nayaHistory/blob/79eeefb/CHANGELOG.md#L453-L455) (vendor release notes: dongle support preparation, slot reservation).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases), v1.25.0.
[^mcuboot]: MCUboot source: image format and encryption design, [`bootutil_public.c`](https://github.com/mcu-tools/mcuboot/blob/main/boot/bootutil/src/bootutil_public.c) (swap table) and [`boot_serial.c`](https://github.com/mcu-tools/mcuboot/blob/main/boot/boot_serial/src/boot_serial.c).
[^kb-signing]: naya-create-kb, [firmware/signing](https://nemezzizz.github.io/naya-create-kb/firmware/signing/).

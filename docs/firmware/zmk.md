# ZMK and custom firmware

The Create's stock keyboard firmware is Naya's own fork of ZMK: the vendor said so from the campaign
on, and the host software, the keymap records and the Bluetooth descriptors all agree. This page
gathers that evidence, shows where the fork goes beyond upstream ZMK, lists the hardware facts a
porter would start from, and states the one hard gate: the signed bootloader. The thing to know
first: nobody has ported open firmware to the Create, and erasing a half over SWD to try would
destroy the only key that can decrypt the stock images, so there would be no way back to stock.

This page stays at the level of consequences. It does not describe, and this site does not publish,
any method to read, bypass or extract keys or to defeat a debug lock.

!!! note "At a glance"
    - The stock firmware is a ZMK derivative on Zephyr, according to the vendor and to host-side evidence.
    - The halves are nRF52840 (1 MB flash, 256 KB RAM, native USB, QSPI), not nRF52811.
    - The bootloader accepts only images signed with Naya's key; a USB update path exists for those.
    - An SWD mass erase removes the only key that unwraps the stock images: no way back to stock.
    - Known for a porter: the SoC, the split-link parameters, the key positions, the LED map. Unknown: the matrix pins, the LED driver, the dock protocol, the split-link payload.

## Status

As of 2026-09-23 nobody we know of has ported ZMK, or any other open firmware, to the
Create: a GitHub search that day found no keyboard firmware port (createflow-dongle replaces only the
dongle's firmware) <span class="tag inferred">INFERRED</span>. The firmware update path is SMP `image upload` over serial recovery, not the configuration
protocol <span class="tag measured">MEASURED</span> ([Flashing](flashing.md)). This differs from naya-create-kb, which places it on the
configuration protocol <span class="tag reported">REPORTED</span>[^kb-zmk]. For a porter, the rest of the stock firmware's behavior is on
our [wire protocol](../protocol/transport.md) pages.

## Evidence the stock firmware is a ZMK fork

**The vendor said so.** The Kickstarter campaign page says remapping is done "between our
custom ZMK firmware and Naya Flow"; update 9 (2023-12-07) describes the Create firmware as based on a
customized ZMK base that adds features ZMK lacks; the campaign FAQ says building and flashing your
own layout with ZMK is "not available for now" <span class="tag doc">DOC</span>[^ks-campaign][^ks-9][^ks-faq]. A staff comment on
Reddit (2023-05-18) adds that it is a custom fork of ZMK, made to allow external modules and other
custom features, and closed source <span class="tag doc">DOC</span>[^reddit-1]. Earlier and later vendor comments on
Reddit say the firmware is being heavily modified (2023-01-06, the same staff account) and that the
vendor builds on ZMK's MIT license and hoped to offer an open SDK later (2024-04-17, the brand account)
<span class="tag doc">DOC</span>[^reddit-2]. The Reddit comments are quoted from archived copies; we could not open them live.
The Kickstarter pages are the live sources.

**NayaCore logs ZMK behavior names**: "ZMK Behaviour: (0x%1) %2", "Unimplemented ZMK
behaviour: %1" and "Unknown ZMK behaviour: (%1) %2" <span class="tag static">STATIC</span>[^nc].

**The keymap record's type byte is a ZMK behavior index.** Types `00` to `0f` index
NayaCore's behavior table; `10` sits outside it <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc]:

| Type | Behavior | Type | Behavior |
|---|---|---|---|
| `00` | `&bt` (Bluetooth) | `09` | `&rgb_ug` |
| `01` | `&kp` (key press) | `0a` | sticky key |
| `02` | macro | `0b` | `&sl` (sticky layer) |
| `03` | `&mt` (mod-tap, the hold-tap form) | `0c` | `&to` |
| `04` | grave escape | `0d` | `&tog` |
| `05` | `&mo` | `0e` | `&trans` |
| `06` | Naya system action | `0f` | mouse |
| `07` | `&none` | `10` | hold-tap record (what OpenFlow calls OneKey) |
| `08` | `&out` | | |

The indices were matched against records captured from the owner's board between 2026-09-03 and
2026-09-22. The full record format is on [Keymap](../protocol/keymap.md).

**Hold-tap flavors are ZMK's four** (balanced, tap-preferred, hold-preferred,
tap-unless-interrupted), stored per record next to the tapping term (default 200 ms) <span class="tag static">STATIC</span>[^nc].
Valid values are 0 to 3. A value of 4 was accepted and stopped every key until the board was
unplugged (a power cycle); `02` was measured as tap-preferred; which of 0, 1 and 3 is which is
**open** <span class="tag measured">MEASURED</span> <span class="tag open">OPEN</span> (owner's board, 3.41.0, 2026-09-03 and 2026-09-17). See
[Settings and timing](../protocol/settings.md).

**Key names follow ZMK's `keys.h`**, aliases included (for example `K_LOCK`,
`K_SCREENSAVER` and `K_COFFEE` all map to usage `0xF9`, and the LANG and INT aliases), and the 4-byte
key-press parameter is ZMK's 32-bit keycode, little-endian: usage low, usage high, usage page,
modifiers <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>[^nc].

`&bt` (0 clear, 1 next, 2 previous, 3 select), `&out` (1 USB, 2 Bluetooth) and the LED
color packing (`RGB_COLOR_HSB`) match ZMK <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (checked against captures, owner's board,
2026-09-08 and 2026-09-10).

**The Bluetooth HID report map is ZMK's, with a vendor mouse.** The 212-byte report map,
read byte for byte identically by two independent third parties, contains ZMK's keyboard input items
and a consumer collection identical to ZMK's, and its HID service attribute list is ZMK's `hog.c`.
The mouse collection is vendor-modified: 8-bit X, Y, wheel and pan plus AC Zoom, where upstream ZMK
uses 16-bit fields and no zoom. There is no boot protocol over Bluetooth. The reads are the third
parties' <span class="tag reported">REPORTED</span>; the comparison with current ZMK is ours, made on their published bytes <span class="tag inferred">INFERRED</span>[^cfd-hid][^zmk-hid].

**The Bluetooth qualification points to Zephyr.** The Bluetooth SIG listing 311198
declares Zephyr's host subsystem (QDID 151074) and Zephyr's own nRF52 controller (QDID 150092), not
Nordic's SoftDevice. Those are reusable Zephyr 2.2-era designs, so they fit a ZMK-on-Zephyr stack
without dating it <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^sig].

**The bootloader was built from an upstream Zephyr tree.** The bootloader banner's Zephyr
build `v3.7.0-5411-g31fea97e05fd` is an upstream Zephyr `main` commit of 2024-10-25, after v3.7.0,
not an nRF Connect SDK tag, and the MCUboot build is vendor-local <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^zephyr]
([Bootloader](bootloader.md#what-it-is)).

## Where the fork goes beyond upstream ZMK

In ZMK the hold-tap flavor and tapping term are compile-time devicetree properties; this
firmware stores both in every hold-tap record and changes them at runtime. The whole keymap (156
records per layer, in two banks), per-layer LED maps, the layer list and the module configurations
are all writable at runtime over USB. There is no macro table: macro records are stubs
<span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>[^zmk-holdtap]. Details: [Keymap](../protocol/keymap.md), [Layers](../protocol/layers.md),
[LEDs](../protocol/led.md).

## The gate: the signed bootloader

The gate is the bootloader, not an "encrypted bootloader". MCUboot verifies each image's
RSA-2048-PSS signature against Naya's key and decrypts the AES-128 image body with a key it holds.
A firmware update path does exist, MCUboot serial recovery over USB, but it accepts only
Naya-signed images <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^fp-bottom] ([Images](images.md#signing), [Flashing](flashing.md)).

Custom firmware therefore needs either Naya's signing key or a replaced bootloader,
written over SWD, and the SWD route is only open if the debug port is not locked <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>.

!!! danger "What an SWD mass erase costs"
    The carved stock images are encrypted, and the key that unwraps them exists only
    inside the stock bootloader. A mass erase (the only SWD action available if the debug port is
    locked, APPROTECT) destroys that key. After it, no bootloader you build can decrypt the stock
    images, so there is **no way back to stock** from the archive. A real way back would need a
    complete dump of the internal flash (and ideally the QSPI) taken before any erase, which is only
    possible if the debug port is not locked. Whether shipped halves have it locked is **open**: the
    build code `D0` suggests revision 2 silicon, but the silicon revision and its APPROTECT default
    are unconfirmed <span class="tag inferred">INFERRED</span> <span class="tag open">OPEN</span>[^parts].

## The hardware a port targets

The halves are Nordic nRF52840 (package `CKAA`, WLCSP; marking `N528…` / `CKAAD0` /
`2301ME`, the end of the first line partly hidden by the potting edge; build code `D0`): 1 MB flash,
256 KB RAM, native USB and a QSPI host <span class="tag doc">DOC</span>[^fcc-crl][^nordic]. Photos and part details are on
[The keyboard half](../hardware/half.md).

No stock keyboard image would fit an nRF52811's 192 KB of flash: the 26 stock images of
the 25 stable releases run from 218 064 to 361 632 bytes, each in a 663 552-byte slot. Each half also
carries an external QSPI NOR flash (Winbond wordmark; part and capacity unreadable in the filed
photos) <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^fh][^parts].

There is no second MCU-class part on the half's mainboard; a few small power parts are
unidentified. The nRF52840's native USB makes a separate USB MCU unnecessary, and each half
enumerates directly as a USB device <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^parts] ([USB](../connectivity/usb.md)).

Debug pads are labeled: on the halves `SWDIO` and `SWDCLK` (plus test pads) at the USB-C
corner; on the dongle `SWDIO`, `TP1`, `TP2`, `5V` and `GND`; on the module boards `SWDIO`, `SWCLK`,
`BOOT0`, `BOOT1` and `RST` <span class="tag doc">DOC</span>[^parts]. Read the erase cost above before touching them.

**Split link.** The halves are Bluetooth-bonded to each other: each half's pair address
(`be/1002`) is the other's own address (`be/1008`). The left half is the central and holds the whole
keymap; the right half reports key positions over the link. The link parameters in the `be/100c`
status are a 7.5 ms interval, latency 0 and a 4 000 ms supervision timeout. The payload protocol on
the link is **open** <span class="tag measured">MEASURED</span> <span class="tag open">OPEN</span> (owner's boards, 2026-09-08 and 2026-09-20). See
[Split link](../connectivity/split-link.md).

**Wired mode, as the vendor described it.** Update 10 (2024-01-06) reports full-duplex
communication over the wired USB-C connection at "10 mb/s", chained right module, right half, left
half, left module, with the left half talking to the computer. The campaign page (2023) said the
opposite for USB mode: the halves stay on radio and only the left half sends data over USB
<span class="tag doc">DOC</span>[^ks-10][^ks-campaign]. Shipped halves fit the campaign page: on 3.41.0 with both halves on USB the
right half exposes no HID interface and its keys reach the host through the left, and every
measurement fits a radio link between the halves <span class="tag measured">MEASURED</span> ([USB](../connectivity/usb.md),
[Split link](../connectivity/split-link.md)). So update 10 most likely describes a prototype or a
design that changed <span class="tag inferred">INFERRED</span>. Whether any shipped unit has a wired path between the halves, and the rate
of the dock link to a module, are **open** <span class="tag open">OPEN</span>.

**Key matrix.** `fe/1008` TOGGLE_KEYSCAN_MODE makes a half stream raw key events
(`fe/1009` `[row][col][state]`) straight off its matrix, bypassing the split link: a right half that
could not type through the link sent 143 events this way (owner's board, 2026-09-20) <span class="tag measured">MEASURED</span>. A porter
can map positions to rows and columns without opening the case; the pin assignment stays **open**,
and the press polarity is inferred <span class="tag open">OPEN</span> <span class="tag inferred">INFERRED</span>.

**LEDs.** Each layer has a 136-entry LED map: 0 to 73 the keys, 74 to 87 the two side
bars, 88 to 111 the left module bay, 112 to 135 the right bay <span class="tag measured">MEASURED</span> (owner's board, 2026-09-08 and
2026-09-10). The LED driver chain and its pins are **open** <span class="tag open">OPEN</span>. See [LEDs](../protocol/led.md).

**Modules.** Each module has its own STM32F411CEU6 running its own firmware, which is not
an MCUboot image, so modules are not part of a keyboard port. They have no radio. The dock has 8
contacts carrying UART, boot and power, no USB data. The dock address encodes type and side (Touch
`0x10` and `0x11`, Track `0x20` and `0x21`, Tune `0x40` and `0x41`; `0xF0` and `0xF1` mean nothing has
booted). Power flows both ways: a charged docked module can power the keyboard, and the keyboard
charges a docked module. The data protocol on the dock is **open** <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span> <span class="tag open">OPEN</span>[^man-create][^parts]
([Module dock](../hardware/dock.md), [Module firmware](modules.md)).

**Battery gauge.** `fe/1006` returns the half's own cell voltage in millivolts (take the
median of five samples) and `de/100b` the module cell in millivolts; percentages are computed on the
host <span class="tag measured">MEASURED</span>. NayaFlow's module percentage is
`(clamp(mV, 3300, 4200) - 3300) * 100 / 900`, truncated, then clamped to 1-100 %, from the `de/100b`
millivolts <span class="tag static">STATIC</span> (NayaCore 6.11.0)[^nc]: 9 mV per point. nayactl and
OpenFlow use the same range[^nx-4], and NayaFlow showed a Tune at 4228 mV as 100 %
<span class="tag measured">MEASURED</span>. naya-create-kb published NayaFlow's calibration points
first; its slope estimate of about 9.3 mV per percent is close, but the exact slope is 9 mV
([Power and batteries](../hardware/power.md#percentages)).

## Known and unknown for a porter

| Subsystem | Known | Unknown |
|---|---|---|
| SoC | nRF52840, 1 MB / 256 KB, native USB, QSPI host | silicon revision |
| External flash | QSPI NOR (Winbond wordmark), holds the secondary slot and data | part number and capacity |
| USB | native, one CDC data port on 3.41.0 | |
| Split link | Bluetooth bond, central left, 7.5 ms interval, latency 0, 4 s timeout | payload protocol |
| Key matrix | positions mapped via keyscan events | pin assignment, polarity (inferred) |
| LEDs | 136-entry map per layer, index ranges | driver chain and pins |
| Modules | separate STM32F411, 8 dock contacts, address scheme | dock data protocol, module bootloader |
| Battery | millivolt reads, host-side curves | |
| Bootloader | MCUboot, Naya-signed images only, USB serial recovery | |
| Debug port | pads labeled | lock state (APPROTECT) |

## Verdict

The two biggest blockers naya-create-kb lists, the SoC's size and an unknown USB MCU, do
not apply. The signing gate and the erase cost do. A port means rebuilding a ZMK fork for the
nRF52840 with QSPI and a Bluetooth split, with the LED engine, the dock protocol and the module side
as the undocumented parts. Nobody has published one <span class="tag inferred">INFERRED</span>. naya-create-kb's own assessment, that a
minimal build (keys and a basic split, no modules, no per-key RGB) is conceivable with an SWD probe,
stays its report <span class="tag reported">REPORTED</span>[^kb-zmk]; it does not weigh the erase cost above.

## Where this differs from naya-create-kb

| naya-create-kb says (zmk and bootloader pages) | What the evidence shows |
|---|---|
| Both halves run the nRF52811, with 192 KB flash and 24 KB RAM; only a stripped-down ZMK build would fit; that is the biggest risk | nRF52840, 1 MB / 256 KB; every stock image is larger than 192 KB; the risk does not apply |
| An unknown USB MCU; the mainboard's component side is in no filing | Native USB on the nRF52840; the SoC close-ups are in the CRL and CRR internal photos; no second MCU-class part |
| A port is a board definition and driver exercise on the same nRF Connect SDK generation | The Zephyr build is an upstream `main` commit, not an NCS tag; the MCUboot build is vendor-local; the stock firmware is itself a ZMK fork |
| Stock images are carved, so there is a return path via SWD | The images are encrypted and the unwrap key is only in the stock bootloader, which an erase destroys |
| A "signed and encrypted bootloader"; no keys and no DFU path | The bootloader verifies and decrypts images; it is not shown to be encrypted itself; a USB update path exists for Naya-signed images |
| Module radios are unknown | Modules have no radio and no FCC ID |

## Open questions

- <span class="tag open">OPEN</span> The debug-lock (APPROTECT) state and silicon revision of shipped halves ([details](../open-questions.md#oq-h05)).
- <span class="tag open">OPEN</span> What a port would still need: the split-link payload protocol, the matrix pinout, the LED driver chain, the dock data protocol ([details](../open-questions.md#oq-f23)).
- <span class="tag open">OPEN</span> Which flavor values 0, 1 and 3 are ([details](../protocol/settings.md)).
- <span class="tag open">OPEN</span> Whether any shipped unit uses the wired link between the halves that update 10 describes.

## Sources

[^ks-campaign]: Kickstarter campaign page, [naya-create](https://www.kickstarter.com/projects/naya-create/naya-create/description) (story and Connectivity sections; read 2026-09-23).
[^ks-faq]: Kickstarter campaign FAQ, [faqs](https://www.kickstarter.com/projects/naya-create/naya-create/faqs).
[^ks-9]: Kickstarter update 9, [2023-12-07](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3982337).
[^ks-10]: Kickstarter update 10, [2024-01-06](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4000229).
[^reddit-1]: Reddit, r/ErgoMechKeyboards, comment `jklwnhz` in thread `13jydnp` (2023-05-18), vendor staff account; quoted from archived copies, not verified live.
[^reddit-2]: Reddit comments `j34yvw9` (thread `101pr7o`, 2023-01-06) and `l001rpv` (thread `1bqumqm`, 2024-04-17); quoted from archived copies, not verified live.
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (behavior names and table, key vocabulary, flavor names) and macOS symbols (`Naya_Device::getModuleBatteryPercentage`).
[^cfd-hid]: createflow-dongle, [`firmware/src/usb_hid.c`](https://github.com/mediaandmerch/createflow-dongle/blob/main/firmware/src/usb_hid.c) (the stock report map, read from a Create); a second, byte-identical read was published by the naya-create-kb maintainer.
[^zmk-hid]: ZMK, [`app/include/zmk/hid.h`](https://github.com/zmkfirmware/zmk/blob/main/app/include/zmk/hid.h) and [`app/src/hog.c`](https://github.com/zmkfirmware/zmk/blob/main/app/src/hog.c).
[^zmk-holdtap]: ZMK documentation, [hold-tap behavior](https://zmk.dev/docs/keymaps/behaviors/hold-tap).
[^sig]: Bluetooth SIG listing 311198 (Naya B.V., model `NAYA-800-1(NAYA-CREATE)`), read through the SIG's public listing search on 2026-09-23. Details on [Regulatory records](../hardware/regulatory.md).
[^zephyr]: Zephyr, [commit `31fea97e05fd`](https://github.com/zephyrproject-rtos/zephyr/commit/31fea97e05fd).
[^fp-bottom]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Bottom line"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L16-L32).
[^fh]: create-legacy-firmware, [`FIRMWARE-HISTORY.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FIRMWARE-HISTORY.md).
[^fcc-crl]: FCC ID 2BQ4V0825CRL and 2BQ4V0825CRR, internal photos exhibits; see [Regulatory records](../hardware/regulatory.md).
[^nordic]: Nordic Semiconductor, nRF52840 Product Specification.
[^parts]: [Parts list](../hardware/parts.md) (FCC internal photos of the halves, dongle and modules).
[^man-create]: Naya Create User Manual v1.1.0, p4; see [Manuals](../product/manuals.md).
[^nx-4]: nayactl, [issue #4](https://github.com/Qonfused/nayactl/issues/4).
[^kb-zmk]: naya-create-kb, [firmware/zmk](https://nemezzizz.github.io/naya-create-kb/firmware/zmk/).

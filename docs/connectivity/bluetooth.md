# Bluetooth

This page covers how the Create talks to Bluetooth hosts: the five host slots and the keys that pick
them, output selection and its hazards, pairing, the BLE v1 to v2 change, the security level, what the
keyboard exposes over GATT, link behavior, and what is known about the Speedlink dongle. The one thing
to know first: the two halves are bonded to each other and a host sees one keyboard; configuration and
firmware updates happen over USB only. The link between the halves is on [Split link](split-link.md).

Unless another source is named, <span class="tag measured">MEASURED</span> means measured on the
owner's board, with the keyboard firmware and date given beside the tag. Byte strings follow the
[byte convention](../protocol/transport.md#byte-convention). No Bluetooth address is reproduced.
Third-party Bluetooth measurements come from the public createflow-dongle project, which describes its
subject as "a Naya Create running firmware 0.3.41 in September 2026"[^cfd], and from naya-create-kb.

!!! note "At a glance"
    - One host-facing keyboard: the left half is the central of a bonded pair and the host gets one set of HID reports and one battery level.
    - Five host slots on the wire (0-4); NayaFlow's keys reach slots 1-4; the stock pairing combo is Layer 2 + 5 (Layer 2 + Esc in the v1.0.6 manual).
    - BLE v2 arrived with 3.35.4 and wiped every host bond on the way.
    - The vendor `0x1234` service answers reads with `65` and does nothing else that anyone has found.
    - Do not press BT_OUT on battery with no host in range: the keyboard froze until power cycled.

## One keyboard, two halves

<!--BT-01-->The two halves are bonded to each other over Bluetooth LE (the split link) and a host sees
one Bluetooth keyboard <span class="tag measured">MEASURED</span> pair tables, 2026-09-01. A third-party
central held a single connection and got the keys of the whole keyboard, the touchpad, the dials and
the media keys, with one battery level <span class="tag reported">REPORTED</span>[^cfd]. So "each half
is an independent peripheral and the host merges two streams, with no inter-half radio"[^kb-ble][^kb-device][^kb-hardware]
does not match what is measured <span class="tag inferred">INFERRED</span>. Whether the right half
advertises to hosts at all is not measured ([open questions](../open-questions.md#oq-c07)).

<!--BT-02-->The SoC and radio belong to [The keyboard half](../hardware/half.md): our reading of the FCC
exhibits is a Nordic nRF52840 (package code `CKAA`), not the nRF52811 naya-create-kb names[^kb-ble]
<span class="tag doc">DOC</span>. The Bluetooth SIG listing 311198 ("NAYA TECH/NAYA CREATE", Naya
B.V., qualified 2025-09-19) declares core specification 5.1, lists model NAYA-800-1 with "USB, 2.4G,
BLE three working modes", and references a Zephyr host (QDID 151074) and a Zephyr controller for nRF52
(QDID 150092) <span class="tag doc">DOC</span>[^sig], which points to a Zephyr link layer rather than
Nordic's SoftDevice <span class="tag inferred">INFERRED</span>. Marketing says Bluetooth 5.4. The
official registers, checked 2026-09-23, hold exactly three FCC IDs under grantee `2BQ4V` (left half,
right half, dongle; final actions 2025-08-26, 2025-08-29 and 2025-09-03, nothing filed since) and the
matching ISED certifications 34320-0825CRL, 34320-0825CRR and 34320-0825DG; each half's filing has a
BLE test report and a separate "2.4G SRD" report (2 Mbps only) under the same FCC ID
<span class="tag doc">DOC</span>[^fcc-eas][^fcc-crl]. Whether shipping firmware ever uses that SRD
mode, on the halves or the dongle, is <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-c14)). Details are on
[Regulatory records](../hardware/regulatory.md).

## Host slots

<!--BT-03-->Five host slots exist on the wire: `be/100c` reports a profile count of 5, and `be/1009` /
`be/100a` take one data byte below 5 <span class="tag measured">MEASURED</span> 2026-09-10
<span class="tag static">STATIC</span>[^nc]. NayaFlow's keys BT_DEVICE_1-4 select slots 1-4, with the
same numbering the status blob uses (the key records carry one-based arguments). Slot 0 is reachable
only by NayaCore's BT_SELECT_SL (wire record `(3, 0)`), which NayaFlow never offers; the dongle is the
usual guess for it <span class="tag static">STATIC</span>[^nc]. The vendor's v0.1.0 notes (one-based)
make slots 1-4 user-assignable and reserve "slot 5" for a future BLE dongle; how that maps onto wire
slots 0-4 is open <span class="tag doc">DOC</span>[^nh-cl]. The Kickstarter campaign (2023) promised
Bluetooth to "up to five devices", and its FAQ several Bluetooth devices plus one RF device through the
included dongle <span class="tag doc">DOC</span>[^ks-camp][^ks-faq].

| Wire slot | Selected by | Vendor naming | What is known | Evidence |
|---|---|---|---|---|
| 0 | BT_SELECT_SL `(3, 0)` only (NayaCore; NayaFlow never offers it) | "slot 5, reserved for a future dongle" is the likely match | never bonded by us; purpose open | <span class="tag static">STATIC</span> <span class="tag open">OPEN</span> |
| 1 | BT_DEVICE_1, record `(3, 1)` | "Dev. 1" | normal host slot | <span class="tag measured">MEASURED</span> 2026-09-10 |
| 2 | BT_DEVICE_2, `(3, 2)` | "Dev. 2" | normal host slot | <span class="tag measured">MEASURED</span> 2026-09-10 |
| 3 | BT_DEVICE_3, `(3, 3)` | "Dev. 3" | normal host slot | <span class="tag measured">MEASURED</span> 2026-09-10 |
| 4 | BT_DEVICE_4, `(3, 4)` | "Dev. 4" | normal host slot | <span class="tag measured">MEASURED</span> 2026-09-10 |

<!--BT-04-->The active slot persists across a power cycle: after a user pressed BT_DEVICE_1 and power
cycled the board, the status still showed slot 1 active
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10.

<!--BT-05-->BT_NEXT `(1, 0)` and BT_PREV `(2, 0)` exist only in NayaCore's table
<span class="tag static">STATIC</span>[^nc]. NayaFlow offers BT_DEVICE_1-4 and BT_CLEAR `(0, 0)`,
which NayaFlow's tooltip says clears the selected slot and starts pairing
<span class="tag doc">DOC</span>[^nf]; whether the bond is cleared on the press was not measured. The
select and clear commands `be/1009` / `be/100a` had not been exercised on hardware by us as of
2026-09-10 <span class="tag measured">MEASURED</span> (read side only). The key records are on
[Keymap](../protocol/keymap.md).

## Keys and key combos

<!--BT-06-->The current manual (v1.1.x, pages 7 and 20) gives these Layer 2 combos; NayaFlow 1.25.1's
stock profile agrees, with BT_CLEAR at positions 6 and 73 <span class="tag doc">DOC</span>[^man-c]
<span class="tag measured">MEASURED</span> stock positions, 2026-09-10. A failed pairing attempt falls
back to the previous connection <span class="tag doc">DOC</span>[^man-c].

<!--BT-07-->naya-create-kb's "Layer 2 + Esc = pairing"[^kb-manual] is the v1.0.6 manual (the FCC
exhibit): its Layer 2 table puts BT Clear on LA1 (the Esc position), "Speedlink" on LA4 and "Connect to
Bluetooth" on LB4, while its text says keys 1-5. The later manual and the stock profile moved Clear to
LG1. Both are right for their version; the stock default today is Layer 2 + 5
<span class="tag doc">DOC</span>[^um106][^man-c].

| Action | Manual v1.1.x and stock profile | Manual v1.0.6 (FCC exhibit) | Evidence |
|---|---|---|---|
| Select host 1-4 | hold Layer 2 (A5 or H1), press 1-4 (LC1-LF1, "Dev. 1-4") | Layer 2 + 1-5 (text) | <span class="tag doc">DOC</span> |
| Clear slot / enter pairing | Layer 2 + 5 (LG1; "BT Clear" in the table, "enter pairing mode" in the text) | Layer 2 + Esc (LA1, "BT Clear") | <span class="tag doc">DOC</span> |
| Output through USB | Layer 2 + Z (LC4) | Layer 2 + Z | <span class="tag doc">DOC</span> |
| Output through wireless | Layer 2 + Left Shift (LB4, "WL") | LB4 "Connect to Bluetooth" | <span class="tag doc">DOC</span> |
| Speedlink (dongle) | not listed | LA4 "Speedlink" | <span class="tag doc">DOC</span> |
| Power button (Windows) / display sleep (macOS) | Layer 2 + Esc (LA1) | not listed | <span class="tag doc">DOC</span> |

<!--BT-08-->NayaFlow's stock profile puts a full set of connection keys on EACH half's System layer
(left positions 2-6, 47 and 48; right 15, 29, 45, 61, 73, 71 and 72): BT_DEVICE_1-4, BT_CLEAR, BT_OUT
and USB_DEVICE <span class="tag measured">MEASURED</span> read from a NayaFlow-flashed board,
2026-09-10. Positions are explained on [Layout and positions](../hardware/layout.md).

## Output selection and its hazards

<!--BT-09-->Output selection is the `08` record (ZMK `&out`) with 1 = USB and 2 = wireless; the
keyboard sends to one output at a time. A Bluetooth device key also switches the output: pressing
BT_DEVICE_1 with no bonded host stopped typing over USB
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08 and 2026-09-10
<span class="tag doc">DOC</span>[^man-c].

<!--BT-10-->Output hazards seen on 3.41.0 <span class="tag measured">MEASURED</span> 2026-09-10,
2026-09-11:

- BT_OUT pressed on battery (USB unplugged, dongle on USB) with no reachable host froze the keyboard,
  layer switching included, until a power cycle.
- With a host bonded and the cable in, BT_DEVICE_1 then USB left typing stuck until USB was pressed a
  second time; the configuration ports stayed healthy.
- USB_DEVICE after BT_DEVICE_1 with no host looked like a shut-off (USB stayed enumerated) until both
  halves were power cycled ([open questions](../open-questions.md#oq-c11)).

## Pairing and identities

<!--BT-11-->The keyboard would not enter Bluetooth pairing while on USB power
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11. The createflow-dongle project says the
same in its own words: keep the keyboard off USB while pairing, because on a cable it sends keystrokes
over the cable; on a free slot it advertises openly (also reported by createflow-dongle[^cfd]).

<!--BT-12-->The address `be/1008` returns (the status blob's "local address") is the split-link
identity; a Windows host paired with a different, host-facing identity
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11.

<!--BT-13-->BLE v2 arrived with keyboard 3.35.4 (beta 1.18.0, stable 1.19.1): latency down to 7.5 ms
(Apple platforms enforce 15 ms), "stronger host connection security at Level 4", each slot advertising
its own name ("NayaCreate BLE 1", "NayaCreate BLE 2", ...), and every known host removed by the v1 to
v2 update (hosts must forget the old "NayaCreate Left" entry and pair again; some need a Bluetooth
restart). The split link fails until both halves run v2; the update order does not matter
<span class="tag doc">DOC</span>[^nh-cl][^beta]. NayaFlow 1.25.1 warns `CREATE_LEFT_BLE_V1_DETECTED` /
`CREATE_RIGHT_BLE_V1_DETECTED`, and NayaCore runs its ClearBLEDevices operation automatically after an
update that crosses the BLE version ("updated to %2 (above BLE version). Starting ClearBLEDevices
operation.") <span class="tag static">STATIC</span>[^nc][^nf].

<!--BT-14-->`be/100f` GET BLE FW VERSION answers `00 02` on 3.41.0 on both halves: one data byte, 2 =
BLE v2 <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-07 to 2026-09-17. The whole reply
frame is `aa 50 00 00 be 04 10 0f 00 02 1d 04`, so naya-create-kb's `00 02 1d` includes the frame
checksum `1d`, and its "BLE FW v0.2.29"[^kb-ble][^kb-commands] is a misreading. On 3.28.7 `be/100f`
returns no frame at all (the firmware predates it) <span class="tag measured">MEASURED</span> 3.28.7,
2026-09-19. See [Command map](../protocol/commands.md).

<!--BT-15-->Security level: the vendor's notes claim Level 4 for host connections
<span class="tag doc">DOC</span>[^nh-cl]. A third-party central with no display or keyboard (Just
Works) bonded at encryption level 2 (no MITM protection) on 3.41, so the keyboard does not refuse
unauthenticated pairing, and the level a host reaches depends on the host
<span class="tag reported">REPORTED</span>[^cfd]. On our board the bonded Windows slot's security byte
in the status blob read 2 <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11 (also reported
by createflow-dongle). The blob is decoded on [Split link](split-link.md).

## GATT: what the keyboard exposes

All of this section comes from third-party reads; no Bluetooth central of ours has read the table, and
NayaFlow has no Bluetooth transport. A read-only check from a host that is already bonded settles it
([open questions](../open-questions.md#oq-c08)).

<!--BT-16-->GATT services and handles, listed after encryption on 3.41 by createflow-dongle and without
handles by naya-create-kb (nRF Connect) <span class="tag reported">REPORTED</span>[^cfd][^kb-ble]:

| Service | Handles | Characteristics | Evidence |
|---|---|---|---|
| `0x1801` Generic Attribute | `0x0001`-`0x0008` | standard | <span class="tag reported">REPORTED</span> |
| `0x1800` Generic Access | `0x0009`-`0x000f` | standard | <span class="tag reported">REPORTED</span> |
| `0x180f` Battery | `0x0010`-`0x0013` | Battery Level `0x2a19`, value handle `0x0012`, notify | <span class="tag reported">REPORTED</span> |
| `0x180a` Device Information | `0x0014`-`0x001a` | three: Model, Manufacturer, PnP | <span class="tag reported">REPORTED</span> |
| `0x1812` HID over GATT | `0x001b`-`0x0030` | report map and reports (below) | <span class="tag reported">REPORTED</span> |
| `0x1234` vendor | `0x0031`-`0x0034` | one characteristic `0x5678` (read, write, notify) and its CCCD | <span class="tag reported">REPORTED</span> |

<!--BT-17-->There is one Battery Level characteristic for the whole keyboard, with no second one for the
other half <span class="tag reported">REPORTED</span>[^cfd]; per-half charge is available only over
USB (`fe/1006`, see [Command map](../protocol/commands.md)). naya-create-kb saw its notifications tick
between 89 and 92 % <span class="tag reported">REPORTED</span>[^kb-ble].

<!--BT-18-->The HID service carries report protocol only: 22 handles leave no room for a Protocol Mode
or boot-report characteristic <span class="tag inferred">INFERRED</span> (handle arithmetic), and the
third-party client finds no boot keyboard report <span class="tag reported">REPORTED</span>[^cfd]. The
212-byte report map is byte-identical in two independent third-party reads, createflow-dongle's and the
naya-create-kb maintainer's research files <span class="tag reported">REPORTED</span> (raw data checked:
we decoded the maintainer's published map)[^cfd][^kb-raw]. Trackball and touch input reach a host as
report 3.

| Report id | Kind | Contents | Evidence |
|---|---|---|---|
| 1 | keyboard (input) | 8 modifier bits, 1 reserved byte, 6-key array (0-255) | <span class="tag reported">REPORTED</span> (raw data checked) |
| 1 | keyboard (output) | 5 LED bits + 3 padding bits | <span class="tag reported">REPORTED</span> (raw data checked) |
| 2 | consumer control | six 16-bit usages, 0-4095 | <span class="tag reported">REPORTED</span> (raw data checked) |
| 3 | mouse | 5 buttons, 8-bit relative X and Y, wheel, AC Pan (`0x238`), AC Zoom (`0x22f`) | <span class="tag reported">REPORTED</span> (raw data checked) |

Whether the keyboard acts on the host's lock-key LED output report is not known.

<!--BT-19-->The `0x1234` / `0x5678` pipe: reads return one byte `65` ("e"), writes are accepted, and
nothing is ever notified, bonded or unbonded (naya-create-kb and createflow-dongle)
<span class="tag reported">REPORTED</span>[^kb-ble][^cfd]. Writing the keyboard's USB configuration
frames to it (GET FW VERSION, addressed to either half) gets no reply, and there is no DFU, SMP or UART
service <span class="tag reported">REPORTED</span>[^cfd]. So configuration and firmware updates are
USB-only on 3.41.0 <span class="tag inferred">INFERRED</span>; "no reply to a configuration frame, no
known use" is safer wording than "dead". NayaFlow 1.25.1 has no Bluetooth transport at all: NayaCore
links Qt SerialPort and no Bluetooth module <span class="tag static">STATIC</span>[^nc].
naya-create-kb's guess that the pipe is a host-initiated command channel for pairing, configuration or
module DFU[^kb-ble] is not supported by any of this.

<!--BT-22-->naya-create-kb saw notifications only for the battery during a 16 s window of trackball
use; a subscription to the pipe succeeded and stayed silent
<span class="tag reported">REPORTED</span>[^kb-ble] ([open questions](../open-questions.md#oq-p25)).

<!--BT-27-->Which half the naya-create-kb GATT map and the third-party central connected to is not
stated in either source <span class="tag reported">REPORTED</span>[^kb-ble][^cfd]; the maintainer's
report-map file is named after the left half, which is a hint only.

## Link behavior

<!--BT-20-->On 3.41 the keyboard drops the host link after its idle time (supervision timeout, HCI reason
`0x08`) and is back about 2 s after a key press; it reconnects by itself after sleep and after a
restart; heavy touchpad use peaked near 130 reports per second with none lost. A host whose bond the
keyboard no longer holds (slot cleared or re-paired) stays connected but gets no keystrokes, and the
keyboard answers "PIN or key missing" <span class="tag reported">REPORTED</span>[^cfd].

<!--BT-21-->Modules have no radio of their own: they link through the dock contacts, and their gestures
reach a Bluetooth host as ordinary HID reports through the keyboard. The vendor said on Reddit
(2023-06-06; archived text, the permalink could not be verified live) that a module hot-swap does not
drop host connections because the half's small cell carries it through; the current manual says the
same of the internal cell <span class="tag doc">DOC</span>[^man-c]. See
[Module fields](../protocol/module-fields.md) for what the host receives.

## The Speedlink dongle

<!--BT-23-->The vendor's v1.0.6 manual lists a "Speedlink Dongle (Wireless dongle, NAYA-100-1)" in the
box and "Speedlink Connection: Using Bluetooth v5.4" <span class="tag doc">DOC</span>[^um106]. The
dongle has no manual of its own: its FCC "user manual" exhibits are the right-half manual v1.0.6, which
adds "Ensure the speedlink dongle is properly seated" <span class="tag doc">DOC</span>[^fcc-dg]. Its
regulatory record describes the radio differently: the dongle's SAR report (R00, 2025-08-12, hardware
`B0K17_Dongle_20241106_V01`) names only a "2.4G SRD" radio at 2 Mbps, one antenna at the cap end and no
simultaneous transmission; FCC ID `2BQ4V0825DG` (granted 2025-09-03), ISED 34320-0825DG (2025-09-08)
<span class="tag doc">DOC</span>[^fcc-dg][^fcc-eas]. Which link protocol "2.4G SRD" is (BLE at 2 Mbps
or a vendor 2.4 GHz mode) is not stated in the filings, for the dongle or for the halves, which carry
the same mode beside BLE; whether shipping firmware ever uses it is
<span class="tag open">OPEN</span> ([open questions](../open-questions.md#oq-c14)); in 2023 the vendor said it was exploring Nordic's
low-latency packet mode (LLPM) <span class="tag doc">DOC</span>[^ks-7]. The Kickstarter campaign called
it an "RF dongle", and update 15 moved it from a planned USB-C receiver to USB-A
<span class="tag doc">DOC</span>[^ks-camp][^ks-15]. NayaFlow 0.1.0 named its action "Connect via
Speedlink" (`RF_DEVICE`) <span class="tag static">STATIC</span>[^nh-rel]. The left half answers
`be/100d` with a stored dongle address <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11.
No vendor text we have read says a dongle mode ever shipped, and a relayed vendor statement (early
2026, through the createflow-dongle project) called it "not yet active"
<span class="tag reported">REPORTED</span>[^cfd]; that statement cannot be checked. NayaFlow 1.21.0
and 1.25.1 carry dongle strings and a `Naya_DeviceDongle` class but no dongle firmware
<span class="tag static">STATIC</span>[^nc][^nh-fw]. NayaCore fixed a dongle-caused hang (5.8.1) and
crash (6.11.0) <span class="tag doc">DOC</span>[^nh-cl]. Whether the dongle bridges a battery-powered
keyboard is open: our test froze on BT_OUT (above)
<span class="tag measured">MEASURED</span> 2026-09-11 ([open questions](../open-questions.md#oq-c04)).
USB details are on [USB](usb.md) and hardware on [Speedlink dongle](../hardware/dongle.md).

<!--BT-24-->createflow-dongle (Apache-2.0, third party) turns an nRF52840 USB stick into a BLE-central,
HID-over-GATT-client bridge that presents the keyboard's own report map over USB; it pairs on an
ordinary user slot (1-4). It is the source of the third-party measurements on this page
<span class="tag doc">DOC</span>[^cfd].

## Host software and vendor claims

<!--BT-25-->Host software history around Bluetooth: NayaFlow 1.18.0 / 1.19.x added a Connection
Settings tab, a device status in the top bar, a split-connection warning and a "Clear BLE Devices"
button ("forces Create to forget all Bluetooth connections"; the host may need to forget the keyboard
too). NayaCore 6.4.0 added BLE v2 support and Clear BLE Devices; 6.9.2 fixed a pairing workflow that
could fail silently; 6.11.0 added pairing error codes, target selection and a post-update BLE version
check <span class="tag doc">DOC</span>[^beta][^nh-cl].

<!--BT-26-->Vendor host claims: BLE v2 is reliable across Debian Linux, Windows, macOS, iPadOS, iOS and
Android <span class="tag doc">DOC</span>[^nh-cl]; the Kickstarter FAQ (2023, live) lists device
support for macOS, Windows, Linux, iPadOS, iOS, Android and ChromeOS, and a 2024 vendor Reddit answer
repeats the list (archived text, not live-verified) <span class="tag doc">DOC</span>[^ks-faq].

## Bluetooth problems

| Symptom | Cause | Fix | Evidence |
|---|---|---|---|
| Keyboard frozen, layers too, after BT_OUT on battery | no reachable host in wireless output | power cycle; avoid BT_OUT on battery | <span class="tag measured">MEASURED</span> 2026-09-11 |
| Typing stuck after BT_DEVICE_1 then USB | output switching with a bonded host and the cable in | press USB (Layer 2 + Z) again | <span class="tag measured">MEASURED</span> 2026-09-10 |
| Keyboard looks off after USB_DEVICE, USB still enumerated | selected a Bluetooth slot with no host first | power cycle both halves | <span class="tag measured">MEASURED</span> 2026-09-10 |
| Will not enter pairing | on USB power | unplug and pair on battery, on a free slot | <span class="tag measured">MEASURED</span> 2026-09-11 |
| Old host cannot reconnect after an update to 3.35.4 or later | the v1 to v2 update removed every bond | forget "NayaCreate Left" on the host, pair again; restart Bluetooth if needed | <span class="tag doc">DOC</span> |
| Split link dead after updating one half across 3.35.4 | only one half on BLE v2 | update the other half | <span class="tag doc">DOC</span> |
| Host connected but no keys, "PIN or key missing" | the keyboard no longer holds that host's bond | forget and pair again | <span class="tag reported">REPORTED</span> |
| Host link drops when idle | supervision timeout after the idle time | press a key; back in about 2 s | <span class="tag reported">REPORTED</span> |

## Commands that touch Bluetooth

The `be` family (pair address, unpair, slots, dongle address, status, clear split links) is listed on
[Command map](../protocol/commands.md); the status blob and the pairing repair are on
[Split link](split-link.md).

## Safety notes

!!! danger "Commands and keys that drop bonds or freeze the keyboard"
    - Do not press BT_OUT (Layer 2 + Left Shift) on battery with no host in range: the keyboard froze
      until power cycled (measured 3.41.0, 2026-09-11).
    - The firmware step from BLE v1 to v2 (to 3.35.4 or later) wipes every host bond.
    - `be/1004` UNPAIR ALL and `be/100a` CLEAR BLE PROFILE drop bonds, and `be/1004` also drops the
      split link. Read [Split link](split-link.md) before using either; neither has been used by us
      outside the pairing repair.

## Open questions

- <span class="tag open">OPEN</span> What wire slot 0 is for, and how it relates to the vendor's "slot 5" ([details](../open-questions.md#oq-c06)).
- <span class="tag open">OPEN</span> Whether BT_CLEAR clears the bond on press; whether the right half advertises to hosts ([details](../open-questions.md#oq-c07)).
- <span class="tag open">OPEN</span> The Device Information strings, and whether the keyboard uses the host's lock-key LED report ([details](../open-questions.md#oq-c08)).
- <span class="tag open">OPEN</span> `be/1009` / `be/100a` on hardware ([details](../open-questions.md#oq-c10)).
- <span class="tag open">OPEN</span> What USB_DEVICE does after a Bluetooth slot was selected with no host ([details](../open-questions.md#oq-c11)).
- <span class="tag open">OPEN</span> Whether the stock dongle bridges anything, and its protocol address ([details](../open-questions.md#oq-c04)); whether shipping firmware ever uses the "2.4G SRD" mode, on the dongle or the halves ([details](../open-questions.md#oq-c14)); what the SIG listing's "2.4G" mode refers to ([details](../open-questions.md#oq-h37)).
- <span class="tag open">OPEN</span> USB-side HID boot protocol ([details](../open-questions.md#oq-c05)).
- <span class="tag open">OPEN</span> naya-create-kb observations nobody else has measured, including the 16 s notification window ([details](../open-questions.md#oq-p25)).

## Sources

[^cfd]: createflow-dongle, [`docs/findings.md`](https://github.com/mediaandmerch/createflow-dongle/blob/main/docs/findings.md) and its firmware sources (third party, Apache-2.0): GATT table, report map, pairing, security level, link behavior, the original dongle.
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (a BLE read of the left half's HID report map); raw data decoded by us, never copied.
[^sig]: Bluetooth SIG qualification listing 311198, "NAYA TECH/NAYA CREATE" (Naya B.V., 2025-09-19), with its referenced Zephyr host (QDID 151074) and controller (QDID 150092) listings.
[^fcc-eas]: FCC Equipment Authorization Search, [grantee 2BQ4V](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm), and the ISED Radio Equipment List, company 34320 (both checked 2026-09-23).
[^fcc-crl]: FCC ID 2BQ4V0825CRL (left half), BLE and "2.4G SRD" test reports, [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL).
[^fcc-dg]: FCC ID 2BQ4V0825DG (Speedlink dongle), SAR report R00 and user manual exhibits, [fccid.io/2BQ4V0825DG](https://fccid.io/2BQ4V0825DG).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): Bluetooth action tables, validation messages, ClearBLEDevices, linked Qt modules.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings (static reading): BT_CLEAR tooltip, BLE v1 warnings.
[^nh-cl]: create-legacy-firmware, vendor release notes, [`changelogs/`](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (v0.1.0, v1.19.1, v1.20.0, v1.25.0).
[^nh-fw]: create-legacy-firmware, [`firmware-history/`](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/firmware-history) (v1.21.0 and v1.25.1 image sets).
[^nh-rel]: NayaFlow 0.1.0, from the create-legacy-firmware release archive, [github.com/create-collective/create-legacy-firmware](https://github.com/create-collective/create-legacy-firmware) (static reading).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (1.18.0 and later).
[^ks-camp]: Kickstarter campaign page, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023), "Connectivity".
[^ks-faq]: Kickstarter FAQ, [naya-create/naya-create/faqs](https://www.kickstarter.com/projects/naya-create/naya-create/faqs) (read 2026-09-23).
[^ks-7]: Kickstarter update 7, [2023-11-07](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3957281).
[^ks-15]: Kickstarter update 15, [2024-09-03](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4095301).
[^man-c]: Naya Create User Manual v1.1.x (pages 7 and 20, key combos; internal cell); see [Manuals](../product/manuals.md).
[^um106]: Naya Create User Manual v1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits ([fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR)).
[^kb-ble]: naya-create-kb, [connectivity/ble](https://nemezzizz.github.io/naya-create-kb/connectivity/ble/) (commit 7668067).
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-device]: naya-create-kb, [device/index](https://nemezzizz.github.io/naya-create-kb/device/) (commit 7668067).
[^kb-hardware]: naya-create-kb, [device/hardware](https://nemezzizz.github.io/naya-create-kb/device/hardware/) (commit 7668067).
[^kb-manual]: naya-create-kb, [device/manual](https://nemezzizz.github.io/naya-create-kb/device/manual/) (commit 7668067).

# Split link

This page covers the Bluetooth bond and live link between the left and right halves: the left half is
the central, what travels over the link, the `be/100c` status blob that describes it, how to judge
whether a pair is healthy, the failures seen on real boards, NayaCore's pairing-repair sequence and its
runs on hardware, and what firmware updates and mismatches do to the link. The one thing to know first:
a firmware flash keeps the bond, and halves on different firmware still type; match the firmware before
you consider a pairing repair, which drops every host bond.

Unless another source is named, <span class="tag measured">MEASURED</span> means measured on the
owner's board, with the keyboard firmware and date given beside the tag. Byte strings follow the
[byte convention](../protocol/transport.md#byte-convention). Addresses are written `<addr6>` and never
reproduced.

!!! note "At a glance"
    - The halves are bonded to each other over BLE; each half's pair address is the other half's own address.
    - The left half is the central: it holds every store and receives the right half's keys over the link.
    - `be/100c` on the left returns a 239-byte status blob with a 39-byte split-link block (7.5 ms interval, 4 s supervision timeout).
    - A keyboard firmware flash leaves both bond tables byte-identical.
    - Halves on different firmware type, but the peripheral's LEDs go dark and its own port answers with empty payloads.

## The halves are bonded, and the left is the central

<!--SL-01-->The two halves are bonded to each other over Bluetooth LE. Each half's pair table (`be/1005`)
holds the other half's address (its only entry when no host is bonded), and `be/1002` on each half
returns the other half's own address. The left half's `be/100c` blob carries a split-link block naming
the right half <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 and 2026-09-08. The
naya-create-kb maintainer's own captures show the same swap (raw data checked: the left half's
`be/1008` equals the right half's `be/1002`)[^kb-raw]. This contradicts naya-create-kb's "no radio
link between halves"[^kb-ble][^kb-device] and fits the CLEAR ALL SPLIT LINKS command it lists itself
(`be/1010`)[^kb-commands].

<!--SL-02-->The left half is the central: it holds every store (keymaps, LED maps, layer list, module
configs) and receives the right half's key positions over the link. With both halves on USB the right
half exposes no HID interface; its keys reach the host through the left (see [USB](usb.md))
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. The right half's key matrix can still
be read directly over its own port with keyscan mode (`fe/1008`), which bypasses the link: 143 events
came from a right half that did not type <span class="tag measured">MEASURED</span> 2026-09-20. The
Kickstarter campaign described the same arrangement: in USB-C wired mode the halves still link over RF
and only the left half sends data over USB <span class="tag doc">DOC</span>[^ks-camp].

```text
host  <--- USB HID or Bluetooth HID (one keyboard) ---  LEFT half (central)
                                                           |  stores: keymaps, LED maps,
                                                           |  layer list, module configs
                                                           |
                                        BLE split link     |  right-half key positions -->
                                                           |  <-- LED state (INFERRED)
                                                           |
                                                        RIGHT half (peripheral)
host  <--- USB CDC only (system, BLE, module reads) ---  RIGHT half's own port
```

## Reading the link

<!--SL-03-->Only the left half answers `be/100c` GET BLE STATUS on 3.41.0; the right half answers
nothing <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08. On 3.28.7 the command does not
exist on either half <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19. The other reads
are `be/1002` GET PAIR ADDRESS (the partner), `be/1005` GET ALL PAIRS and `be/1008` GET BLE ADDRESS
(the half's own split-link identity); all four are on [Command map](../protocol/commands.md).

<!--SL-04-->The `be/100c` reply is `00` followed by exactly 239 bytes, with big-endian multi-byte
fields, in three blocks: a 15-byte header, five 37-byte host-profile blocks (offsets 15-199) and a
39-byte split-link block (offsets 200-238). The split is self-validating: each profile block starts
with its own index, 0 to 4 in order <span class="tag measured">MEASURED</span> 3.41.0, two captures
2026-09-08 and one with a bonded host 2026-09-11. naya-create-kb's "250 B live blob" is the whole
frame[^kb-commands].

| Offset (blob) | Field | Values seen | Confidence | Evidence |
|---|---|---|---|---|
| <!--SL-05-->0-3 | `revision`, u32 | behaves like a counter reset by a power cycle (78703, then 14) | measured, meaning inferred | <span class="tag measured">MEASURED</span> |
| 4 | profile count | 5 | measured | <span class="tag measured">MEASURED</span> |
| 5 | active profile | slot index | measured | <span class="tag measured">MEASURED</span> |
| 6 | bit field: `01` advertising (never seen set), `02` host connected, `04` local address valid | `04` with no host, `06` with a bonded, connected host | measured, names static | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> |
| 7-8 | "global connection mode" and "local address type" (nayactl's names; left raw) | always `02 01` | names static | <span class="tag static">STATIC</span> |
| 9-14 | the half's own address (the split-link identity) | `<addr6>` | measured | <span class="tag measured">MEASURED</span> |
| <!--SL-06-->15 + 37 x n | host-profile block n (n = 0-4) | see below | measured | <span class="tag measured">MEASURED</span> 2026-09-11 |
| <!--SL-07-->200-238 | split-link block | see below | measured | <span class="tag measured">MEASURED</span> 2026-09-08 |

Host-profile block (37 bytes), offsets relative to the block <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-11 <span class="tag static">STATIC</span> (bit names):

| Offset | Field | Values seen |
|---|---|---|
| +0 | index | 0-4 |
| +1 | flags: `01` configured, `02` bonded, `04` connected, `08` active, `10` has peer address, `20` encrypted, `40` authenticated | `08` on an active unbonded slot; `7f` on the bonded, connected, active slot |
| +2 | security level | 2 on the bonded slot (bytes 2-4 read `00 01 02` in every unbonded block) |
| +6..+11 | the host's address, when present | `<addr6>` |

Split-link block (39 bytes from offset 200) <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-08:

| Offset | Field | Value read |
|---|---|---|
| +0..+3 | unknown | |
| +4..+9 | the peer (other half) address | `<addr6>` |
| +10..+11 | connection interval, 1.25 ms units | 6 (7.5 ms) |
| +12..+13 | peripheral latency | 0 |
| +14..+15 | supervision timeout, 10 ms units | 400 (4 s) |
| +16..+38 | unknown | |

Read little-endian, the interval, latency and timeout would be 1536, 0 and 36865, which are not valid
BLE values; that is how the byte order was settled. The left half's own address equals the right
half's `be/1002` answer, and the block's peer equals the left half's `be/1002` answer, cross-checked
by independent commands.

<!--SL-08-->nayactl's status parser (derived from NayaCore's) reads per-profile connection metrics at
+12 and a "76-byte diagnostics block" at offset 200 (last disconnect reason at +`0x20`, packet error
count at +`0x22`) <span class="tag static">STATIC</span>[^nx]. The measured blob has only 39 bytes
there, and unbonded profiles are zero past the flags, so those fields are unreliable
<span class="tag inferred">INFERRED</span>. NayaCore's own display may index some profile fields at
absolute offsets (unverified), so "NayaCore shows the same number" is no proof of a decode.

<!--SL-09-->NayaCore's status JSON names, from its parser: profileCount, activeProfile,
advertisingStatus, hostConnected, localAddrValid, globalConnMode, localAddress (+Type),
advertisingCapability, connectionMode, linkPresent, connected, encrypted, authenticated, peerAddress
(+Type), connectionInterval / Latency / Timeout, metricsValid, estimatedLatency, packetLossCount,
lastDisconnectReason, splitLink, profileIndex, configured, bonded, active, hasPeerAddr, securityLevel,
phyTxEnabled, maxTxOctets and maxRxOctets, packetErrorCount. The list is longer than the header, so it
cannot be read as a byte sequence <span class="tag static">STATIC</span>[^nc].

## The pairing verdict

<!--SL-10-->A healthy pair is exactly `left.pair == right.own` and `right.pair == left.own`, where
`pair` is the `be/1002` answer and `own` the `be/1008` answer
<span class="tag measured">MEASURED</span> on a working pair, 2026-09-07. A one-way match is its own
state ("half-paired": one half re-paired, the other still points at an old partner)
<span class="tag inferred">INFERRED</span>. The bond (records) and the link (live connection) are
separate: correctly bonded halves can still have a dropping link, and during a firmware mismatch both
halves reported mutually correct pair addresses through a dead link
<span class="tag measured">MEASURED</span> 2026-09-20.

| State | `be/1002` / `be/1008` | Other signs | Evidence |
|---|---|---|---|
| Healthy | each half's pair = the other's own | both halves type; right-half LEDs lit | <span class="tag measured">MEASURED</span> |
| Half-paired | one direction matches, the other points elsewhere | right-half keys lost | <span class="tag inferred">INFERRED</span> |
| Bonded but not linked | both directions match | right half dark or silent; firmware mismatch is one cause | <span class="tag measured">MEASURED</span> 2026-09-20 |
| Not bonded | neither matches; the left's bond table lacks the right | right-half keys lost | <span class="tag measured">MEASURED</span> 2026-09-20 (one board) |

<!--SL-11-->A half that does not power or enumerate and a pair that is no longer bonded look the same to
a user ("my right half stopped working"). NayaFlow cannot tell them apart and ships no per-half
recovery: its "one half connected" warning strings exist in Japanese only and are not wired into the
UI. NayaFlow does show a "connection warning" (the halves "may not be communicating correctly"; fix:
restart, then Create Pairing) <span class="tag static">STATIC</span>
<span class="tag doc">DOC</span>[^nf].

## Failures seen on real boards

<!--SL-12-->On one board the right half was bonded to the left, but the LEFT half's bond table held a
host address twice and no bond to the right, so the right half's keys were lost. A firmware mismatch
present at the same time was not the cause; it only made NayaCore refuse its repair
<span class="tag measured">MEASURED</span> 3.35.4 / 3.41.0, 2026-09-20.

<!--SL-19-->**Halves on different keyboard firmware** (left 3.41.0, right 3.35.4): keys from both halves
still type, the peripheral's LEDs go dark, its own port answers every command with an empty payload,
and its version stays readable at `51` through the left half's port (the left port read the right
half's version, 3.35.4, while the right half's own port was hollow). OpenFlow has no automatic retry
through that route, but the route itself is measured; Bluetooth identity reads sent that way answer for
the left half (see below). NayaCore's "Devices have different firmware versions" is a policy of its
pairing flow, not a sign of a dead link. Matching the firmware restores everything; the central dropped
off USB for about 2 s as the halves re-linked. Only a newer central with an older peripheral has been
measured, so flash the central first. One half can miss a vendor update silently: a right half stayed
on 3.35.4 while its left half got 3.41.0
<span class="tag measured">MEASURED</span> 2026-09-20 and 2026-09-22[^fp-mismatch]. See
[Differences by firmware](../protocol/firmware-differences.md) and [Transport](../protocol/transport.md).

| Symptom during a mismatch | Left (central, newer) | Right (peripheral, older) |
|---|---|---|
| Typing | works | works (through the left) |
| LEDs | normal | dark |
| Own USB port | normal | handshakes, then empty payloads |
| Version read at `dst 51` through the left port | | answers (3.35.4) |
| Pair addresses | mutually correct | mutually correct |
| NayaCore pairing repair | refuses ("Devices have different firmware versions") | |

<!--SL-20-->Whenever the peer powers on or re-links, the central reboots through MCUboot (about 2 s off
USB, about 1.4 s at its bootloader product id), so tools should wait for both halves before a
whole-keyboard step <span class="tag measured">MEASURED</span> 2026-09-22 (see [USB](usb.md)).

## What crosses the link

<!--SL-21-->Seen from a host tool: the right half's keys cross the link; so does the right half's LED
state, which is driven from the left half's maps <span class="tag inferred">INFERRED</span> (see
[LEDs](../protocol/led.md)); and so does the firmware-version read sent to `51` through the left port
<span class="tag measured">MEASURED</span> 2026-09-20. The Bluetooth identity reads (`be/1008`,
`be/1002`, `be/1005`) sent to `51` through the left port answer for the LEFT half
<span class="tag measured">MEASURED</span> 2026-09-22. naya-create-kb describes the left port as
proxying the right half in general[^kb-transport][^kb-device]; the relay is partial. Which reply
address byte a relayed answer carries is not recorded ([open questions](../open-questions.md#oq-c12)).

<!--SL-25-->**No wired link between the halves.** Kickstarter update 10 (2024-01-06) says full-duplex
communication was implemented over the wired USB-C connection at "10 mb/s", with a data path right
module, right half, left half, left module, computer <span class="tag doc">DOC</span>[^ks-10]. Shipped
halves do not work that way: the campaign page (2023) already said that in USB mode the halves stay on
RF and only the left half sends over USB <span class="tag doc">DOC</span>[^ks-camp]; the manual's cable
drawing shows the Y-cable joining the halves only at the host <span class="tag doc">DOC</span>[^um106];
and every measurement here fits a radio link (bonded pair tables, the `be/100c` split-link block,
right-half keys arriving through the left when each half has its own cable)
<span class="tag measured">MEASURED</span> 3.41.0. So update 10 most likely describes a prototype or a
design that changed <span class="tag inferred">INFERRED</span>. No wired traffic between the halves has
been observed, and the rate of the dock (module) link today is not known
([open questions](../open-questions.md#oq-c15)). naya-create-kb says there is no link between the
halves at all[^kb-ble].

## Repairing the pair

<!--SL-13-->NayaCore's Pairing operation (6.11.0 strings), for each half in turn
<span class="tag static">STATIC</span>[^nc][^openflow]:

| Step | NayaCore step name | Command | Params (this site's convention) |
|---|---|---|---|
| 1 | `repair_ble_address` | `be/1001` SET PAIR ADDRESS, with the other half's own address | `00 <addr6>` |
| 2 | `wait_300ms` | host-side pause | |
| 3 | `clear_all_split_links` | `be/1010` CLEAR ALL SPLIT LINKS | `00` (empty data, INFERRED) |
| 4 | `unpair_all_pairs` | `be/1004` UNPAIR ALL | `00` (empty data, INFERRED) |
| 5 | `wait_1000ms` | host-side pause | |
| 6 | wait for the peer ("Waiting for peer %1 before normal_reset") | host-side | |
| 7 | `normal_reset` | `ee/10ce` NORMAL RESET | `00` |
| 8 | verify | each half's `be/1002` equals the other's `be/1008` | reads |

The phases are ExchangeBLEAddresses, WaitForPairingPeerBeforeNormalReset and VerifyBLEAddresses; the
waits are host-side pauses. NayaCore refuses with "Pairing failed: missing device(s) (left=%1,
right=%2)" and "Devices have different firmware versions".

<!--SL-15-->**The order is the safety property.** UNPAIR ALL drops every bond on the half, host bonds
included, so both halves' own and pair addresses must be stored BEFORE any clear; clearing first loses
the only copy of what to restore. NayaCore's sibling ClearBLEDevices operation has a
"StorePairedHalfAddressBeforeClear" phase for this reason <span class="tag static">STATIC</span>[^nc]
<span class="tag measured">MEASURED</span> (UNPAIR ALL dropped host bonds and the split bond,
2026-09-20).

<!--SL-16-->Vendor preconditions for pairing and updates: no modules docked on either half, and both
halves on direct USB-C cables (Y-cables are "known to cause issues")
<span class="tag doc">DOC</span>[^nf].

!!! danger "Pairing repair drops every host bond"
    Tested status: run by hand on one board on 3.35.4 (2026-09-20), and reported by the owner on 3.41.0;
    first attempts on a donor board. Before you start:

    1. Bring both halves to the same firmware (NayaCore refuses otherwise, and a mismatched peripheral
       answers with empty payloads).
    2. Undock every module and connect each half with its own direct USB-C cable.
    3. Read and write down `be/1008` and `be/1002` on BOTH halves.
    4. Run the steps in the table above in order, then verify the mutual addresses.

    Hosts must pair again afterwards. Do not chain a repair onto a firmware flash: the flash keeps the
    bond. On USB a half's own switch (OFF, then ON) resets it if needed (see [USB](usb.md)).

<!--SL-14-->**Runs on hardware.** On 2026-09-20, on one board, with both halves first brought to the
same firmware (3.35.4), the commands were sent by hand in NayaCore's order; the result was a clean
mutual bond and both halves typing <span class="tag measured">MEASURED</span> 3.35.4, 2026-09-20. The
address commands (`be/1001`, `be/1010`, `be/1004`) went to both halves, and `ee/10ce` to the left half
only. The repair sequence ends with a reset command (`ee/10ce` NORMAL_RESET); on 2026-09-20 a power
cycle was also done afterwards. Whether the reset alone is enough is untested; a test on the donor board settles
it ([open questions](../open-questions.md#oq-c17)). The owner reports a successful repair on 3.41.0 as
well (not separately recorded in our notes) <span class="tag measured">MEASURED</span> owner report,
3.41.0. OpenFlow's automated sequence ships disabled behind two gates
<span class="tag static">STATIC</span>[^openflow].

<!--SL-17-->ClearBLEDevices (NayaFlow's "Clear BLE Devices", event `clear_ble_devices`) runs the phases
CheckBLEFWVersion, WaitForPairAddress, StorePairedHalfAddressBeforeClear, ClearConnections,
VerifyConnectionsCleared, Respawn, RecheckBLEStatus, WaitForBLEStatus and VerifyBLEFWVersion
<span class="tag static">STATIC</span>[^nc]. It stores the partner, clears all connections and
re-pairs "to known pair address", so host bonds go and the split link stays
<span class="tag inferred">INFERRED</span> (purpose from the step names). NayaCore runs it
automatically after a firmware update that crosses the BLE v1/v2 line (see [Bluetooth](bluetooth.md)).

## Firmware updates, formats and the link

<!--SL-18-->A keyboard firmware flash leaves both halves' bond tables byte-identical (two erases, writes
and swaps each, 3.35.4 to 3.41.0 and back): pairing survives an update, so a repair is not a routine
post-update step <span class="tag measured">MEASURED</span> 2026-09-20[^fp-mismatch]. See
[Flashing](../firmware/flashing.md).

<!--SL-24-->Whether `30/10ca` (the factory format) touches the split link is not known to us.
naya-create-kb judges that it "most likely survives", because clearing the split link is a separate
command, advises re-pairing through NayaFlow if it does not, and its maintainer's post-format sessions
show the halves still linked <span class="tag reported">REPORTED</span>[^kb-fr]. Which partition
NayaCore's clear-all path formats is not recovered by us. See
[Factory reset](../storage/factory-reset.md) ([open questions](../open-questions.md#oq-f19)).

## Vendor notes about the link

<!--SL-22-->From the vendor release notes: v0.1.0 improved keyboard-to-keyboard communication; BLE v2
(3.35.4) raised the bandwidth between halves and requires both halves on v2; 3.31.1 fixed LED colors out
of sync between halves on boot and after sleep; 3.39.4 (its beta note says 3.39.3) reduced BLE traffic
between halves (battery, latency); 3.40.4 fixed the right half waking the left when entering idle
<span class="tag doc">DOC</span>[^nh-cl][^beta].

<!--SL-23-->The vendor manual says to power the left half on before the right, and that the halves are
"paired together using the device manager" (NayaFlow) <span class="tag doc">DOC</span>[^man-c]. A 2025
vendor update reported that with more than ten keyboards paired in one room, halves appeared connected
but did not exchange key presses <span class="tag doc">DOC</span> (archived vendor text).

## Safety notes

!!! danger "Before any clear or repair"
    - Pairing repair drops every host bond (UNPAIR ALL); hosts must pair again afterwards.
    - Store both halves' own and pair addresses before any clear, and verify the mutual addresses after.
    - Bring both halves to the same firmware first: NayaCore refuses otherwise, and a mismatched
      peripheral answers with empty payloads.
    - Undock modules and use two direct cables.
    - Do not chain a repair onto a firmware flash; the flash keeps the bond.
    - To reset a half during a repair or after a mismatch, its switch works even on USB.

## Open questions

- <span class="tag open">OPEN</span> Split-link block bytes 0-3 and 16-38; header bytes 7-8; profile flag bits other than active and the all-set bonded value; why the right half does not answer `be/100c` ([details](../open-questions.md#oq-c09)).
- <span class="tag open">OPEN</span> Whether the reset command alone completes the pairing repair (a power cycle was also done on 2026-09-20) ([details](../open-questions.md#oq-c17)).
- <span class="tag open">OPEN</span> Whether `30/10ca` affects the link ([details](../open-questions.md#oq-f19)).
- <span class="tag open">OPEN</span> Reaching a mismatched peripheral through `51` for writes or other reads (only the version read is measured) ([details](../open-questions.md#oq-c18)).
- <span class="tag open">OPEN</span> Which reply address byte a relayed `dst 51` answer carries ([details](../open-questions.md#oq-c12)).
- <span class="tag open">OPEN</span> The rate of the module (dock) link today; update 10's 10 Mb/s wired figure is a 2024 design ([details](../open-questions.md#oq-c15)).

## Sources

[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs, NayaFlow 1.25.1 on macOS, keyboard 3.41.0); raw data decoded by us, never copied.
[^fp-mismatch]: nayaHistory, [`FLASHING-PROCEDURE.md`, "Pairing and firmware mismatch"](https://github.com/traviswye/nayaHistory/blob/79eeefb/FLASHING-PROCEDURE.md#L369-L384) (commit cdd897c).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`bluetooth.py`, the status parser).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): Pairing and ClearBLEDevices step names, refusals, status JSON names.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings (static reading): connection warnings, pairing preconditions.
[^openflow]: OpenFlow (link at release): its pairing-repair module, which ships disabled.
[^nh-cl]: nayaHistory, vendor release notes, [`changelogs/`](https://github.com/traviswye/nayaHistory/tree/79eeefb/changelogs) (v0.1.0, v1.17.2, v1.19.1, v1.25.0).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (1.17.1, 1.18.0, 1.22.0, 1.24.0).
[^ks-camp]: Kickstarter campaign page, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023), "Connectivity".
[^ks-10]: Kickstarter update 10, [2024-01-06](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4000229).
[^man-c]: Naya Create User Manual v1.1.x ("Turning Create ON/OFF", pairing); see [Manuals](../product/manuals.md).
[^um106]: Naya Create User Manual v1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits ([fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR)), cable drawing.
[^kb-ble]: naya-create-kb, [connectivity/ble](https://nemezzizz.github.io/naya-create-kb/connectivity/ble/) (commit 7668067).
[^kb-device]: naya-create-kb, [device/index](https://nemezzizz.github.io/naya-create-kb/device/) (commit 7668067).
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-transport]: naya-create-kb, [protocol/transport](https://nemezzizz.github.io/naya-create-kb/protocol/transport/) (commit 7668067).
[^kb-fr]: naya-create-kb, [storage/factory-reset](https://nemezzizz.github.io/naya-create-kb/storage/factory-reset/) (commit 7668067).

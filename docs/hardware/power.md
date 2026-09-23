# Power and batteries

This page explains who powers whom (USB, the half's small cell, the module packs, Qi), lists every
battery as filed and as marketed, gives the ratings, shows how software reads battery voltages and turns
them into percentages, and collects the power behavior users and tool authors run into: sleep, resets,
flat modules, recovery mode and cables. The one thing to know: a half runs from USB or from its docked
module; its own 50 mAh cell only bridges a module swap, so wireless use depends on the modules'
batteries.

!!! note "At a glance"
    - Power flows both ways through the dock: USB charges the module through the half; off USB the module powers the half.
    - Cells as filed: half 50 mAh; Tune 1000 mAh; Touch 700 mAh; Track 600 mAh (2 x 300 mAh). Retail capacities are not confirmed.
    - Ratings: each half 5 V DC 1.5 A; module bases 5 V 500 mA; dongle 5 V 30 mA.
    - `fe/1006` reads the half's cell in mV; `de/100b` reads the module's cell in mV; `de/1009` reads the module cell and its charging rail in 0.1 mV.
    - NayaFlow's module percentage is `(clamp(mV, 3300, 4200) - 3300) * 100 / 900`, truncated, then clamped to 1-100 %: 9 mV per point.

## The power model

<!-- power facts 1-4, 51-52 -->
A half runs from one of two sources: a computer USB port, or a docked module with enough charge. Its own
small cell only keeps it on while a module is swapped and "is not intended to power normal operation";
it charges while the half draws power <span class="tag doc">DOC</span>[^um106][^man-c] (also reported by naya-create-kb as
user-confirmed[^kb-power]). Power therefore flows both ways through the dock: on USB the half feeds and
charges the docked module; off USB the module's pack powers the half <span class="tag doc">DOC</span>[^um106][^man-c] (dock nets
`MZ_VBAT`/`VBAT` and `USB_5V`/`POGOPIN_5V`; see [Module dock](dock.md)).

Wireless use depends on the modules' batteries, since the half's cell is too small; the manual's
wireless troubleshooting asks to check that modules are docked and charged, and the Naya Connect FAQ
states the same model ("modules contain the batteries that power the ecosystem") <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^man-c][^ks-connect].
Pass-through charging is a core design element: every module has a Qi coil at its base and charges
while docked, mainly when the keyboard is wired; module batteries are not designed to be swapped easily
<span class="tag doc">DOC</span>[^ks-11]. In 2024 the vendor reported lower runtime consumption, "nearly eliminated" quiescent draw,
better module charging efficiency and a larger Tune battery <span class="tag doc">DOC</span>[^ks-15].

History: in January 2023 the design had no battery in the keyboard at all; the May 2023 campaign still
placed all batteries in the modules while its Risks section mentioned the prototype's "backup battery,
BMS"; by June 2023 each half had "a hot-swap battery inside" so modules can be swapped without dropping
host connections <span class="tag doc">DOC</span>[^reddit-j34wi1g][^reddit-jn3wrmk][^ks-camp] (Reddit quotes: archived text, not
live-verified).

## Batteries as filed and as marketed

<!-- power facts 5-7, 11-13 -->

| Device | Cell label | Filed | v1.1.0 manual | Website and 2023 campaign | Evidence |
|---|---|---|---|---|---|
| Each half | `FH301217`, 3.7 V, 50 mAh, 0.185 Wh Li-ion polymer pouch | 50 mAh | "45mA" (v1.0.6 spec sheet) | none in the keyboard (early design) | <span class="tag doc">DOC</span> CRL IP2 p13-p14; CRR IP1 p10-p11[^fcc-crl][^fcc-crr] |
| Tune | `FH 202030`, 3.7 V 1000 mAh 3.7 Wh | 1000 mAh | 1500 mAh | 1500 mAh | <span class="tag doc">DOC</span>[^fcc-crl][^man-tu][^ks-camp] |
| Touch | `FH364046`, 3.7 V 700 mAh 2.59 Wh (a second `FH364045` 700 mAh cell appears in a teardown photo) | 700 mAh (one or two cells, open) | 1500 mAh | 800 mAh | <span class="tag doc">DOC</span>[^fcc-crl][^man-to][^ks-camp] |
| Track | `QS801630 1S2P`, 3.7 V 600 mAh 2.22 Wh, two `QS801630` 300 mAh cells in parallel | 600 mAh | 700 mAh | 800 mAh | <span class="tag doc">DOC</span>[^fcc-crl][^man-tr][^ks-camp] |
| Float (never shipped) | - | - | - | 1500 mAh | <span class="tag doc">DOC</span>[^ks-camp] |

The half's cell is about 3 x 12 x 17 mm by its size code (inferred), taped with its protection board, on
a three-wire lead (red, white, black) to a receptacle at `VBAT2` beside an `NTC` pad <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>. The test
reports declare the half's two power sources as "1# Supplied from battery. Model: 301217, DC 3.7V 50mAh
0.185Wh" and "2# Supplied from PC USB port, DC 5V" <span class="tag doc">DOC</span> BLE reports p10 (text layer verified
2026-09-23)[^fcc-crl][^fcc-crr]. The manual's "45mA" is a typo or a minimum rating; the cell and the
reports say 50 mAh <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^um106].

The filed units are pre-production, so retail capacities are not confirmed
([details](../open-questions.md#oq-h21)); naya-create-kb's module-pack attributions differ from these
(its "Touch FH202030 1000 mAh" is the Tune's pack, its "Track FH364046 700 mAh" the Touch's cell, and its
separate cylindrical "ICR" 300 mAh cell is one of the Track's two pouch cells)[^kb-hardware][^kb-exhibits].
Cell makers are not identified (label prefixes `FH` and `QS` only); module retail boxes carry a UN 3480
lithium-ion battery label <span class="tag doc">DOC</span>[^wb-naya].

## Ratings and supply rules

<!-- power facts 8-10, 16 -->
- Each half's input is rated 5 V DC 1.5 A on its label; the manual's "Input Voltage 4.2V" reads as the
  cell's full-charge voltage <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crr][^um106].
- Module bases are rated `Input: 5V⎓500mA` (read on the Touch and Track) <span class="tag doc">DOC</span> CRL IP4 p27; CRL IP6
  p37[^fcc-crl].
- The dongle is bus-powered at DC 5 V (rated 5 V DC 30 mA on its label) and has no cell <span class="tag doc">DOC</span> DG RF report
  p10; DG LBL[^fcc-dg].
- The manuals' rule: do not plug the keyboard into a wall outlet; charge from a computer USB port ("USB
  2.0 5V-1A" in v1.0.6, "USB 3.0 5V-1A" in the v1.1.0 module manuals) <span class="tag doc">DOC</span>[^um106][^man-to].

## Charging a module

<!-- power facts 14-15 -->
A module charges in the dock when the keyboard has power, and on a Qi charger whether docked or not;
halves charge from USB, and docked modules charge from the half <span class="tag doc">DOC</span>[^um106]. Inside each module the dock
5 V and the Qi receiver's output pass through Schottky diodes into an SGM41523 single-cell charger; the
Qi receiver (MT5705) is a 5 W WPC receiver <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^fcc-crl] (the topology is inferred; the schematic is
confidential).

## Reading battery values

<!-- power facts 17-27, 30-31, 50 -->
The keyboard never pushes battery values; NayaCore polls each half about every 6 s <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (NayaCore's
own log timing and its `set_handshake_frequency` example "6000")[^nc]. Percentages are computed on the
host from millivolts, not sent by the device <span class="tag measured">MEASURED</span>.

| Command | What it reads | Reply (site byte convention) | Units | Evidence |
|---|---|---|---|---|
| `fe/1006` (NayaCore: GET KB BATTERY LEVEL) | the half's own cell; NayaFlow shows it as "Internal Battery Voltage (mV)" | `00 <mV hi> <mV lo>`, for example `00 0f f5` = 4085 mV | mV, big-endian | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-11)[^nc] (also reported by nayactl[^nx] and naya-create-kb) |
| `de/100b` (GET PRECISE BATTERY LEVEL) | the docked module's cell | `00 <mV hi> <mV lo> <valid>` (`valid` `00` = good) | mV, big-endian | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, module 2.3.3, 2026-09-07)[^nx-i4][^nx-pr5] |
| `de/1009` (GET BATTERY) | the module's cell and its charging rail (USB or Qi input) | `00 <b0> <batt hi> <batt lo> <rail hi> <rail lo>`, for example `00 00 a2 37 c8 f6` = 4.1527 V battery, 5.1446 V rail | 0.1 mV, big-endian | <span class="tag measured">MEASURED</span>[^nx-i4] |

- **`de/100b` is the cell, not the rail.** Back to back on the same modules: Track `de/100b` 4152 mV
  versus the `de/1009` battery field 4142.3 mV, and Tune 4236 mV versus 4257.2 mV; the rail read 4.58-5.14
  V on USB <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, module 2.3.3)[^nx-i4]. naya-create-kb calls `de/100b` the module
  rail[^kb-power]. Its four-byte payload `[00, HI, LO, 00]` is exactly this site's reply form (status,
  value, validity byte); only its reading of the value is wrong. Its `de/1009` layout `[00][batt][usb]`
  misses the `b0` byte between the status and the battery value <span class="tag measured">MEASURED</span>. See
  [Transport](../protocol/transport.md) for the byte convention and [Modules](../protocol/modules.md)
  for the commands.
- **Module firmware differences.** 2.1.2 does not implement `de/100b` (no payload and about 1.09 s of
  timeout on every request); `de/1009` works on 2.1.2 and 2.3.3 <span class="tag measured">MEASURED</span> (a second board, 3.28.7, module 2.1.2,
  2026-09-19). The nayactl maintainer reports that 2.2.2 does not reply to `de/100b` at all and that
  `de/1009` works there <span class="tag reported">REPORTED</span>[^nx-pr5].
- **Units.** Feeding the millivolt value into tenth-of-a-millivolt math shows every module at 1 %; tools
  must use the right unit per command (fixed in nayactl pull request 5) <span class="tag measured">MEASURED</span>[^nx-pr5].
- **Readings.** Half cells: 4.152 V and 4.066 / 4.094 V (right / left) on the owner's halves, 4.21 V on a
  half after recharge <span class="tag measured">MEASURED</span> (owner's board, 3.41.0; a second board, 3.28.7). The nayactl maintainer reports
  4.173, 4.176 and 4.194 V on full halves and 2.771 V on a drained right half that tools show as 1 %
  <span class="tag reported">REPORTED</span>[^nx][^nx-pr2][^nx-pr5]. naya-create-kb's dumps read about 4088 / 4087 mV and later 4091 / 4098 mV,
  rising on USB charge <span class="tag reported">REPORTED</span> (raw data checked: its maintainer's published dumps show 4084-4098 mV left and
  4094-4105 mV right)[^kb-power]. Modules: full modules 4.12-4.26 V; a Tune on module 2.1.2 read 4000 mV
  through `de/1009` <span class="tag measured">MEASURED</span>[^nx-i4]; a module at 1 % read 2.8311 V with its USB rail at 4.8706 V (nayactl
  thread) <span class="tag reported">REPORTED</span>[^nx-pr2].
- **Noise.** The nayactl maintainer saw a full keyboard cell swing between about 90 and 100 %, and tools
  read it five times and take the median <span class="tag reported">REPORTED</span> <span class="tag static">STATIC</span>[^nx-i4][^nx]. Other public raw data (6 s polls at rest)
  show smaller spreads of 13-31 mV per session, which is 1.5-3.5 points on the vendor's 9 mV-per-point
  scale; this has not been measured on our boards.
- **Host facts.** NayaCore tracks per device `InternalBatteryVoltage`, `ModuleBatteryVoltage`,
  `ChargingSource` (`Battery` or `USB_Qi`) and `USBVoltage`; the protocol also has a category `0xCA`
  named IC_CHARGER with no known subcommands <span class="tag static">STATIC</span>[^nc]. nayactl labels a module's rail "Qi" below 4.5 V
  and "USB" at or above (a tool heuristic, thresholds unverified) <span class="tag static">STATIC</span>[^nx].

**Rails at a glance on a healthy board on USB** (labels corrected): module cell about 4.1-4.26 V full
(`de/100b`, mV; `de/1009` on older module firmware); module charging rail about 4.6-5.1 V on USB
(`de/1009` second field, 0.1 mV); half cell about 4.1-4.2 V (`fe/1006`, mV) <span class="tag measured">MEASURED</span>. naya-create-kb labels the
module cell as the "module rail" and gives about 4200 mV full, 3700 mV low[^kb-power].

### Presence versus voltage

<!-- power facts 32-33 -->
Take presence from the handshake (`de/1001`), not from a voltage. With an empty dock naya-create-kb saw
the right half report `de/100b` as zeros while the left floated near `0x1060` (it reads this as an
unloaded charger rail) <span class="tag reported">REPORTED</span> (raw data checked)[^kb-power]. In its maintainer's published dumps the right
half's zero reply carries the invalid flag (`00 00 00 01`), while the left half's phantom 4192 mV is
flagged valid (`00 10 60 00`). `de/1001` replies `00 01 <addr>` for a docked, booted module <span class="tag measured">MEASURED</span> (owner's
board, 3.41.0). A docked module that has not booted (at about 0-1 % on pogo power) stays dark and answers
as `0xF0`/`0xF1` with firmware 0.0.0, the same reply an empty dock gives <span class="tag measured">MEASURED</span> (a second board, 3.28.7,
2026-09-19); the nayactl maintainer reports that it boots and lights at about 1 % <span class="tag reported">REPORTED</span>[^nx-pr2]. See
[Module dock](dock.md#what-the-host-sees).

## Percentages

<!-- power facts 28-29 -->
NayaFlow's module percentage is `(clamp(mV, 3300, 4200) - 3300) * 100 / 900`, truncated, then clamped
to 1-100 %, from the `de/100b` millivolts <span class="tag static">STATIC</span> (NayaCore 6.11.0, the
function feeding `connectedModuleBatteryLevel`)[^nc]. That is 9 mV per point; any valid reading at or
below 3309 mV shows 1 %, and an invalid reading shows "?". NayaFlow computes no
percentage for the half's own cell; it shows that cell in millivolts <span class="tag static">STATIC</span>[^nc].

| Point | Source | Reading | NayaFlow showed | Formula gives |
|---|---|---|---|---|
| naya-create-kb sample | <span class="tag static">STATIC</span> (also reported by naya-create-kb[^kb-power]) | about 4222 mV | 100 % | 100 % |
| naya-create-kb sample | same | 3910 mV | 67 % | 67 % |
| naya-create-kb sample | same | 3709 mV | 45 % | 45 % |
| a Tune on module 2.3.3 | <span class="tag measured">MEASURED</span>[^nx-i4] | 4228 mV | 100 % | 100 % |
| the same Tune | <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>[^nx-i4] | 4127 mV | 92 % | 91 % (the displayed reading was probably at least 4128 mV) |

naya-create-kb published NayaFlow's calibration points first; its slope estimate from them, "about
9.3 mV per percent", is close, but the exact slope is 9 mV. Its
samples: a full Touch read `0x1064` = 4196 mV and a discharged Track `0x0E82` = 3714 mV <span class="tag reported">REPORTED</span> (raw data
checked). NayaFlow 1.20.0's notes acknowledge a 5-10 point fluctuation in module percentages
<span class="tag doc">DOC</span>[^nf-rel]. nayactl and OpenFlow use the same linear 3.3-4.2 V scale as NayaCore (nayactl floors,
OpenFlow clamps to 1-100 %) <span class="tag static">STATIC</span>[^nx].

## Flat modules and module recovery mode

<!-- power facts 34-37, 42 -->
Long docking can drain a module until its battery protection makes it unchargeable ("Battery Zero"); the
vendor answered with firmware and hardware changes and a recovery mode, and the manual advises undocking
modules for long storage <span class="tag doc">DOC</span>[^ks-21][^man-c][^man-tu]. naya-create-kb found that unplugged with modules
docked, the module packs drain slowly, and that the half's cells only sag when the modules are undocked
overnight <span class="tag reported">REPORTED</span>[^kb-power]. Its maintainer's published overnight dumps show the first part (raw data
checked): a docked Touch fell from 4184 to 3920 mV and a docked Track from 4166 to 3714 mV while the half
cells held near 4.10 V; the second part has not been tested.

### Module recovery mode and the indicator

Module recovery mode is the key action `MODULE_FORCE_CHARGING` (NayaCore action 401; key record type
`0x06`). The v1.1.0 manual puts it on `LA5` of the System layer ("Module Force Charge" on Windows,
"Module Recovery Mode" on macOS). NayaFlow's tooltip: it recovers a module "from a critically drained
battery", the module does not work meanwhile, and a keyboard restart turns it off <span class="tag doc">DOC</span> <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>
[^man-c][^nc] (stock System layer record `06` with 401 on the owner's board, 3.41.0, 2026-09-08).

Measured behavior: recovery mode acts only on the half whose key is pressed (each half needs its own
key), puts that half's LEDs out, force-charges that bay, times out on its own, and a restart clears it;
it revived an unresponsive Tune and Touch <span class="tag measured">MEASURED</span> (a second board, 3.28.7, module 2.1.2, 2026-09-19; only
this firmware) ([details](../open-questions.md#oq-f22)).

Because module firmware 2.3.3 disabled the battery blink, the manual's "blinking red = battery low" may
not appear on current module firmware <span class="tag inferred">INFERRED</span>[^nf-rel]. One module was seen repeating three red breaths and
one green blink; its meaning is unknown <span class="tag measured">MEASURED</span> (owner's board, Touch docked right, 2026-09)
([details](../open-questions.md#oq-h32)). The indicator table is on
[Manuals](../product/manuals.md#the-module-indicator-led).

!!! warning "Recovery mode"
    Recovery mode stops the module working until it times out or the keyboard restarts; use it only for
    a module that does not respond, as the manual says. It writes nothing to the keymap. Tested by us on
    3.28.7 only.

## Sleep and idle

<!-- power facts 38-40 -->
The manual gives sleep after 1.5 min and deep sleep after 10 min (deep sleep drops Bluetooth); NayaFlow
1.25.1 defaults to 90 s idle and 300 s sleep <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^um106][^man-c][^nc]. The device takes three
timeouts; NayaCore names them `idle_time_ms`, `sleep_time_ms` and `sleep_battery_time_ms`, and the third
stayed 30 s in every one of our captures <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board, 3.41.0, 2026-09-11). A board not yet
written by NayaFlow held 90 000 / 600 000 / 15 000 ms, which matches the manual's 1.5 and 10 minutes <span class="tag reported">REPORTED</span>
(raw data checked: the naya-create-kb maintainer's capture of 2026-09-15). The firmware refuses values
under 30 s and treats 0 as off <span class="tag measured">MEASURED</span>. Details on [Settings and timing](../protocol/settings.md).

The LED idle timeout did not run with the cable in and USB output selected, and ran on battery (LEDs off
at 90 s, one tap restores); whether the power source or the output mode gates it is not settled <span class="tag measured">MEASURED</span>
(owner's board, 3.41.0, 2026-09-11) <span class="tag open">OPEN</span>. The "LED scan mode" (PWM) setting exists to reduce power use
and LED wear; the vendor's 3.31.1 LED PWM control cut consumption at full brightness by about 50 %
<span class="tag doc">DOC</span>[^nc][^nf-rel][^nf-beta].

## Resets

<!-- power facts 43-46 -->

| Action | A real reset? | How to see it | Evidence |
|---|---|---|---|
| Power switch OFF, then ON, with USB connected | yes: OFF shuts the half off, ON restarts it | the half drops off USB | <span class="tag measured">MEASURED</span> (owner's board, 2026-09-23); <span class="tag doc">DOC</span> "Create will respect the ON/OFF state even while connected over USB"[^man-c] |
| "True cold boot": USB out, modules undocked, switches off, then on | yes, like any power-on | bootloader PID for about 1-1.7 s | <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span> (also reported by naya-create-kb[^kb-power]) |
| `ee/10ae` into the bootloader, then SMP `os reset` on the data port | yes; the application is back in about 8 s | bootloader PID, then application PID | <span class="tag measured">MEASURED</span> (a second board, 3.28.7, 2026-09-19; owner's board, 2026-09-20) |
| `ee/10ce` (NORMAL_RESET) | yes; the half reboots through MCUboot | it leaves USB within a fraction of a second and shows its bootloader PID for about 1-2 s | <span class="tag measured">MEASURED</span> <span class="tag reported">REPORTED</span> |
| One half powers on and re-links | yes, for the central: it reboots through the bootloader | about 2 s off USB | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-22) |

Every boot shows the half's bootloader PID (`0x006F` left, `0x00D3` right) for about 1-1.7 s (right 0.98 s
and left 1.40 s on 3.41.0; 1.6-1.7 s on 3.28.7) <span class="tag measured">MEASURED</span> (2026-09-19, 2026-09-22). naya-create-kb says the only
real reset besides `ee/10ce` is the cold boot, that a switch flip on USB is not a reset, and that
`ee/10ce` reboots both halves with USB dropping for about 0.13 s[^kb-power][^kb-recovery]. The first two
are contradicted above. For the third, its own notes give 0.13 s as the delay before USB drops, not the
length of the outage, which lasts through the 1-2 s bootloader pass. See
[Bootloader](../firmware/bootloader.md) and [Recovery](../recovery.md).

The half's LEDs can stay lit on its internal cell while it has no data connection to the host, so a lit
half is not proof of a working link <span class="tag inferred">INFERRED</span> (follows from the power model).

## Vendor power fixes by firmware

<!-- power fact 41 -->

| Firmware | Change | Evidence |
|---|---|---|
| NayaFlow 0.1.0 | "Batch 1 / DVT#2" units can charge modules over USB | <span class="tag doc">DOC</span>[^nf-rel] |
| keyboard 3.31.1 (announced in beta 1.16.0; the image first ships in beta 1.17.1) | LED PWM: about 50 % less at maximum brightness | <span class="tag doc">DOC</span>[^nf-rel][^nf-beta] |
| module 2.3.2 | Tune LEDs about 20 % less | <span class="tag doc">DOC</span>[^nf-rel] |
| keyboard 3.35.4 | module battery management about 10 % better | <span class="tag doc">DOC</span>[^nf-rel] |
| keyboard 3.39.4 (the beta note says 3.39.3; reached stable with 3.41.0) | fixed power cycling on a low internal battery plus a depleted module battery | <span class="tag doc">DOC</span>[^nf-beta] |
| keyboard 3.40.4 | lower low-battery LED threshold; fixed "Track not keeping the Create awake" | <span class="tag doc">DOC</span>[^nf-beta] |
| module 2.3.3 | disabled the battery blink because "NayaFlow can read the battery" | <span class="tag doc">DOC</span>[^nf-rel] |

See [Firmware versions](../firmware/versions.md).

## Cables and hubs

<!-- power facts 47-49 -->
The manual's Y-cable carries power and data for both halves to one host port; NayaFlow 1.25.1 warns that
Y-cables "are known to cause issues" for updates and pairing and asks for two direct USB-C to USB-C cables
<span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^um106][^nc]. A USB hub or dock gave the halves and the dongle power but no data in one session;
use a port on the machine for configuration <span class="tag measured">MEASURED</span> (owner's board and dongle, 2026-09-11, single session).

Pre-production runtime claims (2023): "a full work week with LEDs turned up to the max or up to 100 days
with LEDs off"; the campaign spec sheet gave 80 days for the Track and Touch and 100 days for the Tune and
Float; marketing later claimed a 14-day runtime for the Tune. None is measured <span class="tag doc">DOC</span>[^reddit-jn3wrmk][^ks-camp][^wb-naya].

## Safety

- Do not charge from a wall outlet (manuals); the vendor gives no reason, but it is the manual's rule.
- Never short or bridge the dock contacts: `VBAT` is the module battery.
- A drained half cell (the 2.8 V region) is below a Li-ion cell's comfortable range; recharge it promptly
  <span class="tag inferred">INFERRED</span>.

## Open questions

- <span class="tag open">OPEN</span> Retail module capacities; one or two Touch cells ([details](../open-questions.md#oq-h21), [Touch cells](../open-questions.md#oq-h20)).
- <span class="tag open">OPEN</span> Whether the power source or the output mode gates the LED idle timer.
- <span class="tag open">OPEN</span> What the third timeout field does (always 30 s) ([details](../open-questions.md#oq-p20)).
- <span class="tag open">OPEN</span> The meaning of the red-red-red-green module blink ([details](../open-questions.md#oq-h32)).
- <span class="tag open">OPEN</span> The half's power-tree ICs and rail voltages ([details](../open-questions.md#oq-h03)).
- <span class="tag open">OPEN</span> Recovery mode per side on firmware other than 3.28.7 ([details](../open-questions.md#oq-f22)).
- <span class="tag open">OPEN</span> Whether the half cells sag overnight only when the modules are undocked; how noisy the half-cell reading is on our boards.

## Sources

[^fcc-crl]: FCC ID 2BQ4V0825CRL (left half; the module photos are in both filings): exhibits on the FCC record ([FCC EAS search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm), grantee 2BQ4V; mirror [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL)). Codes are explained on [Regulatory records](regulatory.md#how-to-cite-an-fcc-photo).
[^fcc-crr]: FCC ID 2BQ4V0825CRR (right half), including the label artwork; mirror [fccid.io/2BQ4V0825CRR](https://fccid.io/2BQ4V0825CRR).
[^fcc-dg]: FCC ID 2BQ4V0825DG (dongle); mirror [fccid.io/2BQ4V0825DG](https://fccid.io/2BQ4V0825DG).
[^um106]: Naya Create User Manual Version 1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits ([fccid.io](https://fccid.io/2BQ4V0825CRR)); see [Manuals](../product/manuals.md).
[^man-c]: Naya Create User Manual Version 1.1.0 (vendor PDF, 2025-11-10), p4-p5, p11, p20, p23, p25; see [Manuals](../product/manuals.md).
[^man-to]: Naya Touch User Manual Version 1.1.0 (vendor PDF), p2, p5.
[^man-tu]: Naya Tune User Manual Version 1.1.0 (vendor PDF), p2, p7.
[^man-tr]: Naya Track User Manual Version 1.1.0 (vendor PDF), p2.
[^nc]: NayaFlow 1.25.1 (Windows): NayaCore 6.11.0 strings and disassembly (the module percentage function), the renderer, the settings table and user-interface strings (static reading).
[^nf-rel]: Vendor release notes, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases) (0.1.0, 1.17.2, 1.19.1, 1.20.0, 1.25.0).
[^nf-beta]: Vendor beta release notes, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (1.16.0, 1.22.0, 1.24.0).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (README, `cli/status.py`, commit 9799866).
[^nx-i4]: nayactl, [issue #4](https://github.com/Qonfused/nayactl/issues/4) (module battery readings from the owner's board on 3.41.0 with modules on 2.3.3, and the maintainer's comments).
[^nx-pr2]: nayactl, [pull request #2](https://github.com/Qonfused/nayactl/pull/2) and its comments (maintainer's board on 3.30.1, modules on 2.2.2).
[^nx-pr5]: nayactl, [pull request #5](https://github.com/Qonfused/nayactl/pull/5) (the unit fix; maintainer's comments on 2.2.2).
[^kb-power]: naya-create-kb, [power architecture](https://nemezzizz.github.io/naya-create-kb/device/power/) (third party).
[^kb-hardware]: naya-create-kb, [hardware deep dive](https://nemezzizz.github.io/naya-create-kb/device/hardware/) (third party).
[^kb-exhibits]: naya-create-kb, [exhibit inventory](https://nemezzizz.github.io/naya-create-kb/device/exhibits/) (third party).
[^kb-recovery]: naya-create-kb, [recovery](https://nemezzizz.github.io/naya-create-kb/recovery/) (third party).
[^ks-camp]: Kickstarter campaign page with its Specs Sheet and Risks section, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023).
[^ks-11]: Kickstarter update 11, [2024-02-15](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4029736).
[^ks-15]: Kickstarter update 15, [2024-09-03](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4095301).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^ks-connect]: Kickstarter Naya Connect FAQ, [archived 2026-03-14](https://web.archive.org/web/20260314000000*/kickstarter.com/projects/naya-create/naya-connect*).
[^reddit-j34wi1g]: Reddit, vendor comment [j34wi1g](https://www.reddit.com/comments/101pr7o/_/j34wi1g/) (2023-01-06); archived text, not live-verified.
[^reddit-jn3wrmk]: Reddit, vendor comment [jn3wrmk](https://www.reddit.com/r/ErgoMechKeyboards/comments/13jydnp/_/jn3wrmk/) (2023-06-06); archived text, not live-verified.
[^wb-naya]: The vendor's former website, archived by the Wayback Machine ([naya.tech captures](https://web.archive.org/web/2025*/naya.tech/*)); cited only, images not reproduced.

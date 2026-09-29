# LEDs on the wire

This page covers everything the protocol does with light: the per-layer LED map (`30/100d` and
`30/100e`), the live `ed` commands and their measured framing, the three persistent LED settings,
runtime effects versus the stored layer animations, the LED key records, the module bay blocks, and
the known dark-board and dim-board problems with the evidence for and against each. The one thing to
know first: an `ed` ack proves nothing, because short parameters are silently zero-filled, and the
`ed/1013` ceiling is stored, so an `ed/1013` of 0 would keep the keys dark across reboots.

!!! note "At a glance"
    - Each layer has its own map of 136 entries `[led][hue lo][hue hi][sat]`; byte 3 is saturation, not brightness, and brightness is never stored per key.
    - `ed` params are `00 <target> <values>`; the target's value is ignored and missing bytes become 0.
    - `ed/1012`, `ed/1013` and `ed/1014` are persistent device settings with no read command.
    - Rewriting the layer list byte for byte clears a runtime effect on both halves in one frame.
    - The left half holds every LED map; the right half's lights are driven from it.

Byte strings follow the [byte convention](transport.md#byte-convention): params and replies start
with the flag or status byte. LED entries are quoted as record bytes `[led][hue lo][hue hi][sat]`
unless a row says "params".

## What decides what a key shows

Three things combine: the layer's stored LED map (color per index), the layer's stored animation
(byte 2 of its entry in the [layer list](layers.md)), and runtime state (an effect chosen by a key
or by `ed/1011`, the brightness level, and the persistent ceilings). The sections below take them in
that order.

## The LED map

<!--LD-01-->Each layer has its own map of 136 LED entries, indices 0-135. The bands were found by
painting each band a distinct color; 3.28.7 has the same 136 entries
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08; 3.28.7, 2026-09-19. Physical key
positions belong to [Layout and positions](../hardware/layout.md).

| Indices | Count | What they light |
|---|---|---|
| 0-73 | 74 | the keys (index = key position `00`-`49`) |
| 74-80 | 7 | one edge bar (which physical edge is open: one note says right, NayaFlow draws it on the left outer edge) |
| 81-87 | 7 | the other edge bar |
| 88-111 | 24 | the LEFT module bay block |
| 112-135 | 24 | the RIGHT module bay block |

<!--LD-02-->An entry is 4 bytes, `[led index][hue lo][hue hi][saturation]`: hue is a u16
little-endian in degrees (0-360) and saturation runs 0-100
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08. The palette hues nayactl's LED
work lists encode the same way: `00 00` = 0, `26 00` = 38, `35 00` = 53, `78 00` = 120,
`ab 00` = 171, `f0 00` = 240[^nx-pr6].

<!--LD-03-->Byte 3 is SATURATION, not brightness: white is hue 0 / saturation 0 and red is hue 0 /
saturation 100, so a tool that reads byte 3 as brightness turns every white key red when it writes
the map back. It was settled by a NayaFlow flash and a device read in which 17 of 18 color classes
matched, all 40 white keys included <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08.
NayaCore logs the same fields in the same order ("LED at index: %1 Hue: %2 Sat: %3")
<span class="tag static">STATIC</span>[^nc].

| NayaFlow color | Stored (hue, saturation) |
|---|---|
| `#ffffff` | (0, 0) |
| `#ff0000` | (0, 100) |
| `#21ffaa` | (157, 87) |
| `#808080` | (0, 0) |

<!--LD-04-->Brightness is not stored per key. It is a device-level setting (the brightness command,
the brightness keys and the ceiling), so the map is lossy in brightness (`#808080` is stored as
white), not in saturation <span class="tag measured">MEASURED</span> 3.41.0 and 3.28.7, 2026-09.

<!--LD-05-->Saturation 150 is NayaFlow's "no color assigned" sentinel (its `#xxxxxx` placeholder),
deliberately outside 0-100 <span class="tag static">STATIC</span>[^nf][^nx]. A layer written by
NayaFlow read back 76 entries at (0, 150) <span class="tag measured">MEASURED</span> 3.41.0,
2026-09. What the board shows for 150 is not recorded.

<!--LD-06-->NayaFlow's conversion from a hex color to (hue, saturation) matches its stored values byte
for byte only with the integer 60-degree formula, truncated: `#0084ff` gives hue 208, where
floating-point rounding gives 209 <span class="tag measured">MEASURED</span> 3.41.0, 2026-09
(against NayaFlow's stored values).

<!--LD-07-->naya-create-kb lists named colors as (hue, saturation) pairs: red 0/70, green 120/70, cyan
180/100, blue 240/100, purple 266/70, magenta 300/100, pink 300/100, white 0/0 and "factory amber"
38/100[^kb-led]. Its maintainer's LED-map dumps hold exactly those entries, so these are colors set on
that board, not a vendor palette <span class="tag reported">REPORTED</span> (raw data
checked)[^kb-raw]. The factory amber is real: early reads of our board returned `[led] 26 00 64` for
every entry <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01, and NayaFlow gives a new
layer's keys the color `#FFA500`, which converts to 38/100 <span class="tag static">STATIC</span>[^nf].
NayaCore's LED-key color table, a different table, has magenta at hue 270 and pink at 300
<span class="tag static">STATIC</span>[^nc].

NayaFlow's stock color palette ("Rainbow") and the values its conversion stores:

| Swatch | Hue | Saturation | Evidence |
|---|---|---|---|
| `#ff0000` | 0 | 100 | <span class="tag static">STATIC</span> palette, <span class="tag inferred">INFERRED</span> conversion (LD-06 formula) |
| `#ff6f00` | 26 | 100 | as above |
| `#ffe500` | 53 | 100 | as above |
| `#00ff00` | 120 | 100 | as above |
| `#00ffd9` | 171 | 100 | as above |
| `#0000ff` | 240 | 100 | as above |
| `#6f00ff` | 266 | 100 | as above |
| `#ffffff` | 0 | 0 | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08 |
| `#FFA500` (new-layer default) | 38 | 100 | <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 |

## Reading and writing the map

<!--LD-08-->**Reading.** Send `30/100d` with params `00 <layer>`, then `01 <layer>` while the reply
status is `01`. The 544 record bytes come back in three chunks of 241 + 241 + 62 with reply byte 3
counting `02`, `01`, `00` <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. A layer with
no stored map answers status `16` with the layer echo and no records: seen by us on 3.28.7
<span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19, and in a third-party 3.41.0 capture
<span class="tag reported">REPORTED</span> (raw data checked)[^kb-raw]. The map lives on the left half
only; the right half answers nothing to `30/100d`[^nx-pr6]. Chunking rules are on
[Transport](transport.md).

!!! warning "Map writes are live and persistent"
    `30/100e` takes effect at once and survives a reboot; there is no commit and no undo. Read and
    save the whole map (all layers) before writing. On 3.28.7 never send a map that needs three frames.

<!--LD-09-->**Writing.** `30/100e` params are `00 <layer>` followed by entries. Sparse writes are
native: NayaFlow sent `00 00 22 f0 00 64` (layer 0, LED `22`, hue 240, saturation 100). A full map is
NayaFlow's three-frame write: each frame's params are `00 <layer>` plus the next 241 / 241 / 62-byte
slice of the 544-byte entry stream (params 243 / 243 / 64; the slices split entries), with byte 3
`02`, `01`, `00`; for layer 3 the acks were `01 03`, `01 03`, `00 03`
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. naya-create-kb attributes the
full-map form to a nayactl claim; it is NayaFlow's own form[^kb-led].

!!! danger "3.28.7: three-frame writes wedge the half"
    On 3.28.7 a write that needs three frames stops the half answering and typing until it is
    unplugged. Split a full map into two writes of whole entries (below). Tested on a donor board.

<!--LD-10-->On 3.28.7 the three-frame form wedges the half, while two writes of whole entries land
fine: 120 entries (480 record bytes, params 243 + 241 in two frames), then 16 entries (64 record bytes,
params 66) <span class="tag measured">MEASURED</span> 3.28.7, 2026-09-19. See
[Differences by firmware](firmware-differences.md).

<!--LD-11-->naya-create-kb's per-key ritual (read the whole map, write one entry, read again) works: no
commit is needed and the entry persists <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01; also reported by naya-create-kb, read-back proven on layers 1 and 2[^kb-led].

<!--LD-12-->A map write that covers only part of the map leaves the rest as last written: a writer that
stopped at 82 of the 136 entries left the module bay LEDs on an older color
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--LD-13-->A third party (the author of nayactl PR #6) saw oversized `30/100e` writes of 241 or 41
bytes wedge the CDC parser until a power cycle, and a 5-byte single entry ack without effect, on
3.41.0 <span class="tag reported">REPORTED</span>[^nx-pr6]. The 5-byte case most likely lacked or
misplaced the layer byte <span class="tag inferred">INFERRED</span>. naya-create-kb reports the same
wedge for oversized single frames[^kb-led].

## `ed` commands

!!! warning "Every `ed` command is a write, and acks prove nothing"
    Short or empty params are zero-filled, not refused, and every such frame acks like a correct one.
    Judge the result by eye and keep the last known good values written down. Never send `ed/1013`
    with 0, with short params or with empty params: the ceiling is stored, so the key array would
    stay dark across reboots.

<!--LD-20-->**Framing, settled for this site.** An `ed` request's params are the flag byte `00`, then a
TARGET byte, then the command's values: `ed/1008` brightness 40 is params `00 00 28`, the frame
`aa 00 50 00 ed 05 10 08 00 00 28 30 04`. The target's value is ignored: targets 0, 1, 2, 3 and 200
behaved the same for brightness. Short params are zero-filled from the end, so a missing value becomes
0 and a missing target becomes 0, and every such frame acks exactly like a correct one
<span class="tag measured">MEASURED</span> left half, 3.41.0, 2026-09-09[^nx-pr6]. naya-create-kb
agrees in substance (a target byte, `ff` for all, value ignored, short sends zero-filled)[^kb-led].

<!--LD-21-->The measured series, params as sent <span class="tag measured">MEASURED</span> left half,
3.41.0, 2026-09-09:

| Command | Params sent | Read as | Result |
|---|---|---|---|
| `ed/1008` | `00 10` | target `10`, level 0 | off |
| `ed/1008` | `00 64` | target `64`, level 0 | off |
| `ed/1008` | `00 00 0f` | target 0, level 15 | dim |
| `ed/1008` | `00 03 64` | target 3, level 100 | full |
| `ed/1008` | `00 c8 0f` | target 200, level 15 | dim |
| `ed/1011` | `00 01` | target 1, effect 0 | solid |
| `ed/1011` | `00 00 01` | target 0, effect 1 | breathing |
| `ed/1004` | `00` | target 0 | off |

Reading the first params byte as the target would give brightness 100 for `00 64`, which the board
did not show. naya-create-kb and its tools write `ed` params as `[target, value]` with no leading flag
byte, for example `ed/1013` as `[ff, 64]`; in this site's convention the same logical command (target
`ff`, value 100) is `00 ff 64`[^kb-led] <span class="tag reported">REPORTED</span> (raw data checked:
their tools send the params verbatim)[^kb-raw]. How the device treats a frame without the flag byte is
not measured by us.

<!--LD-22-->A consequence for nayactl's command line on 3.41.0: `led brightness N` and `led effect N`
send one byte after the flag, so they set brightness 0 and effect 0
<span class="tag inferred">INFERRED</span> from the series above[^nx].

<!--LD-23-->Brightness and effect commands act on the half they are addressed to: the right half stayed
solid while the left breathed <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10.

<!--LD-24-->Command list and parameter rules, from NayaCore 6.11.0's LED message builder
<span class="tag static">STATIC</span>[^nx-pr6]. NayaCore clamps out-of-range values to 100 with a
warning and refuses to build an LED command with an empty target, so NayaFlow never sends empty `ed`
params. Per-command rows are on [Command map](commands.md).

| Command | Params (this site) | NayaCore's rule |
|---|---|---|
| `ed/1003` ON, `1004` OFF, `1005` TOGGLE | `00 <target>` | target only |
| `ed/100f` HALT, `1010` RESUME, `100d` EFFECT CYCLE | `00 <target>` | target only |
| `ed/1006` INCREMENT, `1007` DECREMENT | `00 <target> <amount>` | amount < 101 |
| `ed/1008` ADJUST BRIGHTNESS | `00 <target> <level>` | 0-100 |
| `ed/1011` SELECT EFFECT | `00 <target> <index>` | index < effect count |
| `ed/100e` HUE SATURATION | `00 <target> <hue lo> <hue hi> <sat>` | hue < 361, saturation < 101 |
| `ed/1050` RGB BRIGHTNESS | `00 <target> <r> <g> <b> <brightness>` | brightness < 101 |
| `ed/1012`, `1013`, `1014` | `00 <target> <value>` | persistent settings (below) |

<!--LD-25-->`ed/1011` SELECT EFFECT numbers the effects 0 solid, 1 breathe, 2 swirl, 3 spectrum; the
stored per-layer animation in the layer list uses 2 spectrum, 3 swirl
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-09. See [Layers](layers.md).

| Value | `ed/1011` and the LED effect keys | Layer-list animation byte |
|---|---|---|
| 0 | solid | solid |
| 1 | breathe | breathe |
| 2 | swirl | spectrum |
| 3 | spectrum | swirl |

<!--LD-26-->naya-create-kb reports four further behaviors, untested by us: `ed/1004` OFF and a
brightness of 0 are separate states (ON does not relight a board at brightness 0, INCREMENT does);
`ed/10d1` and `ed/10d2` get no reply; `ed/1014` gets no reply from the right half; and empty params act
on the half addressed <span class="tag reported">REPORTED</span>[^kb-commands][^kb-led]. The last one
agrees with our zero-fill measurement (LD-20).

## Persistent settings, ceilings and the `ed/1050` override

!!! warning "Persistent LED settings"
    `ed/1012`, `ed/1013` and `ed/1014` survive a reboot and have no read command. Write them only
    with a known good value, and never `ed/1013` 0.

<!--LD-30-->`ed/1013` SET LED MAX BRIGHTNESS is a persistent ceiling over the key array: params
`00 00 1e` (30) visibly dimmed the board and `00 00 64` (100) restored it, and both values persisted
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-13. A ceiling of 0 would therefore keep the
keys dark across reboots while every LED command still acks <span class="tag inferred">INFERRED</span>,
as the author of nayactl PR #6 reports <span class="tag reported">REPORTED</span>[^nx-pr6]; we have never
sent 0, and OpenFlow refuses to. The same author reports that module LEDs are not
under this ceiling (lit modules beside dark keys are the tell)
<span class="tag reported">REPORTED</span>[^nx-pr6].

<!--LD-31-->After both halves were updated to 3.41.0 the board came up very dim; re-sending
`ed/1013` 100 (params `00 00 64`) fixed it, so a low ceiling is one measured cause of a dim board and
re-sending it is the measured fix <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-20/22.
Whether the flash changed the stored ceiling or only the live level was not recorded: no read of the
ceiling exists, and none was taken before and after.

<!--LD-32-->`ed/1012` SET SCANMODE PWM (a bool) and `ed/1014` SET LED LAYER OVERRIDE (0 = an LED action
pressed on a key lasts until the keyboard restarts, 1 = until the next layer change) are persistent
device settings too <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-13 and 2026-09-16; see
[Settings and timing](settings.md). None of `ed/1012`-`1014` has a read command: NayaCore 6.11.0 names
every LED command it can send, and none reads a setting <span class="tag static">STATIC</span>[^nc];
also reported by naya-create-kb[^kb-commands].

<!--LD-33-->Empty or one-byte params to `ed/1012`-`1014` are writes (zero-filled), not reads: an empty
`ed/1013` sets a ceiling of 0 by the measured zero-fill rule <span class="tag inferred">INFERRED</span>
from LD-20. naya-create-kb describes the empty-param frame as a read that returns a bare ack; the ack
is real, but the probe is a write[^kb-commands][^kb-led].

<!--LD-34-->naya-create-kb reports `ed/1050` RGB BRIGHTNESS as a global color override: it survives a
reboot, beats the map (a white override over a zeroed map still lights the keys), and bulk `30/100e`
writes drop it back to following the map; no value that clears it back to the map is known
<span class="tag reported">REPORTED</span>[^kb-led][^kb-settings]. Untested by us. A layer-list
rewrite (below) is an untested candidate for clearing it <span class="tag inferred">INFERRED</span>.

## Runtime effects and restoring the stored lighting

<!--LD-40-->A runtime effect (from an LED key or `ed/1011`) survives layer-data, LED-map and module
writes, and even NayaFlow flashes. Writing the FULL layer list back to the left half, byte-identical
to what it holds, drops BOTH halves to the stored animation and colors in one frame and changes
nothing stored; otherwise only a power cycle clears it. The same rewrite clears the lighting state a
half comes back with after a bootloader pass <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-10 and 2026-09-20/22.

!!! warning "Recipe: restore the stored lighting (measured, 3.41.0)"
    1. Read the layer list from the left half: `30/1001` params `00 00`.
    2. Write the same entries back unchanged to the left half: `30/1002` params `00 00` + every entry
       exactly as read.
    3. Both halves return to their stored colors and animations. Nothing stored changes, but this is
       a write: send exactly the bytes you read, to the left half only. Tested on the owner's board.

<!--LD-41-->LED effect keys are global and latching at run time: the effect stays across layer
switches until it is cleared (and, with the override setting at 0, until restart)
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

## LED key records (type `09`)

<!--LD-50-->An LED key is a `09` record (ZMK's `&rgb_ug`[^zmk]) with `[subcommand u32 LE][argument u32
LE]`. The subcommands were paired with NayaFlow's database after a default-profile flash
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08:

| Subcommand | Action | Argument |
|---|---|---|
| `00` | effect on/off | 0 |
| `07` | brightness up | 0 |
| `08` | brightness down | 0 |
| `09` | speed up | 0 |
| `0a` | speed down | 0 |
| `0b` | next effect | 0 |
| `0d` | select effect | index in NayaCore's order: 0 solid, 1 breathe, 2 swirl, 3 spectrum |
| `0f` | set color | `[brightness][saturation][hue u16 LE]`, ZMK's HSB packing |

<!--LD-51-->The stock System layer's LED keys: position 9 solid, 10 breathe, 11 swirl, 12 spectrum, 23
next effect, 24 brightness up, 25 speed up, 39 on/off, 40 brightness down, 41 speed down, 55-58 white,
red, green and blue. The captured colors (brightness, saturation, hue) are white (100, 0, 0), red (100,
100, 0), green (100, 100, 120) and blue (100, 100, 240) <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-08. NayaCore's 19-entry table adds cyan 180, magenta 270, yellow 60, orange 30 and pink
300, all at 100/100 <span class="tag static">STATIC</span>[^nc]. Record layouts are on
[Keymap](keymap.md).

## Module bays and the right half

<!--LD-60-->The bay blocks are keyed to the BAY, not to the module: swapping a Tune and a Track
between halves kept each side's color. A module's address (`de/1007`), not which LEDs look lit, tells
which bay it is in <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08; 3.28.7, 2026-09-19.

<!--LD-61-->NayaFlow paints each 24-entry bay block in one color per layer, from its module color
(database positions 88 and 89; which feeds which side is open); its stored key-row colors at app
positions 90-96 never reach the board. Per-layer module colors do reach the modules: holding the
layer keys changed a Tune and a Touch to that layer's colors
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-09/10.

<!--LD-62-->What each module lights: a Touch takes only the first index of its block (88 or 112),
as naya-create-kb also reports[^kb-led]. The Tune carries 24 LEDs
<span class="tag doc">DOC</span> (Kickstarter and filings, see [Tune](../hardware/tune.md)); how many
map indices a docked Tune follows is open and may depend on module firmware: on 2.1.2 indices 88-93
took the color and 94-111 stayed white, a 2026-09-08 band test saw 88-96 lit, and index 88 alone lit
it on 2026-09-10 <span class="tag measured">MEASURED</span> 3.41.0 and 3.28.7, 2026-09 (conflicting).
Whether a Track follows one index or a band is open.

<!--LD-63-->Module LEDs are driven outside the key array's gate: with the key ceiling at 0 the modules
stay lit, according to naya-create-kb and the author of nayactl PR #6
<span class="tag reported">REPORTED</span>[^kb-led][^nx-pr6]. We have no measurement of our own of
lit modules beside a zero ceiling, since OpenFlow refuses to send 0.

<!--LD-64-->A "module green blink" (three red breaths, a green blink, repeating, with a Touch docked on
the right) persisted after the module color was changed in NayaFlow, so it is firmware signaling, not
the map; its meaning is open <span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

<!--LD-65-->Why the right half looks unreachable for LED commands: its LED map lives on the left, the
right answers no `30/100d`, one layer-list write to the left restores lighting on both halves, and a
firmware mismatch darkens only the peripheral's LEDs. So the left (the central) drives the right
half's LED state over the split link <span class="tag inferred">INFERRED</span> from those measured
facts. naya-create-kb describes the right half as deaf to LED commands in general, with a
firmware-internal recovery path[^kb-led]; see [Split link](../connectivity/split-link.md).

## Known problems

<!--LD-70-->**The "cold-boot saturation drop".** naya-create-kb reports a firmware bug in which white
keys come back red after a power cycle while the map stays byte-identical[^kb-led]. On our 3.41.0 board
the stored map was byte-identical across a power cycle and white keys stayed white (2026-09-10); 17 +
24 white keys have come through every power cycle since 2026-09-08
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-10. The red keys we once saw came from a
misunderstanding of the map layout (byte 3 read as brightness), not from the firmware. It is not
reproduced here. A 30-second check: power cycle, hold layer 1 before any write, and look at the white
keys.

<!--LD-71-->**The "dark saga".** naya-create-kb reports that wrong-arity `ed` writes parked its key LEDs
dark for hours, through reboots and NayaFlow resets, by zero-filling 0 into the `ed/1013` ceiling and
the scan mode <span class="tag reported">REPORTED</span>[^kb-led]. Its recovery ladder, sent to the
left half with every step at target `ff`, is: `ed/1013` 100, `ed/1012` 1, `ed/1014` 0, `ed/1050`
white at 100, `ed/1008` 100, `ed/1011` solid, `ed/1003` on (plus resume); it calls the ladder
idempotent, and adds `30/10ca` for a store that is "truly wedged" even across a firmware reflash. In
this site's convention those steps are params `00 ff 64`, `00 ff 01`, `00 ff 00`, and so on (see
LD-21). Our measured parts: the ceiling persists across reboots (LD-30), re-sending it fixed a dim
board after a firmware flash, though whether the flash changed it was not recorded (LD-31), and short
params zero-fill (LD-20). Our non-destructive first step for a runtime lighting state is the
layer-list rewrite (LD-40). The ladder as a whole is untested by us.

<!--LD-72-->**Dim halves, progressive dimming, inverted brightness keys.** naya-create-kb's open item
(2026-09-18: scan mode 0 + brightness 100 + ON changed nothing on a dim left half; progressive
dimming; brightness keys inverted)[^kb-led] is partly explained. Scan mode is invisible by eye
(flicker shows only on camera). The LED idle timer did not run with the cable in and USB output
selected, but did on battery (LEDs off at 90 s, one tap restores; whether the power source or the
output mode gates it is open), so a dim half on USB is not the idle timer
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11. A low ceiling after a flash is one
measured cause (LD-31). The vendor's notes for 3.39.4 to 3.41.0 add LED notifications and a lower
low-battery LED threshold, untested causes <span class="tag doc">DOC</span>[^nh-cl]. For the
brightness-key inversion there is no data.

<!--LD-73-->A NayaFlow keymap flash sends no `ed` frame at all: three captured flashes that changed LED
override and max brightness in the UI sent none, and none of our captures (flashes on 2026-09-01, -07
and -17, an LED-override change on 2026-09-14) contains one
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17. A third-party
settings-flash capture has none either (raw data checked)[^kb-raw]; naya-create-kb draws the same
conclusion[^kb-settings].

<!--LD-74-->**LED changes by firmware**, as the vendor dated them <span class="tag doc">DOC</span>[^nh-cl][^beta]:

| Keyboard firmware | LED change in the vendor notes |
|---|---|
| 3.31.1 | LED PWM power control (about 50 % less at maximum); fix for colors out of sync between halves on boot and after sleep |
| 3.39.4 (its beta note says 3.39.3) | firmware-side LED remapping; LED notifications |
| 3.40.0 | per-LED OFF |
| 3.40.4 | LED remap no longer overwrites LED actions (effect and color keys take priority until restart); LEDs stuck half on / half off fixed; module update no longer needs the Solid effect |
| 3.41.0 | the LED action override setting; fix for colors offset onto wrong keys during rapid updates |

Between 3.35.4 and 3.41.0 the LED data exchanged between the halves changed: halves on those two
versions leave the peripheral's LEDs dark while typing works
<span class="tag measured">MEASURED</span> 3.35.4 and 3.41.0, 2026-09-20[^fp-mismatch]. Behavior by
firmware is collected on [Differences by firmware](firmware-differences.md).

### Dark or dim board: what to check first

Least destructive first. Each row names its basis.

!!! danger "The last row wipes the board"
    `30/10ca` formats the data partition (keymaps, LED maps, module configs and, reportedly, the layer
    list). It has never been sent by us and its restore is untested; take a complete snapshot first
    and make first attempts on a donor board.

| Symptom | Check | Fix | Basis |
|---|---|---|---|
| Wrong effect or colors after an LED key, a flash or a bootloader pass | runtime effect | rewrite the layer list byte for byte (LD-40) | <span class="tag measured">MEASURED</span> 3.41.0 |
| Whole key array dim after a firmware update | LED ceiling | re-send `ed/1013` 100 (params `00 00 64`) (LD-31) | <span class="tag measured">MEASURED</span> 3.41.0 |
| Key array dark, every `ed` command acks | ceiling at 0 (for example after an empty or short `ed/1013`) | re-send `ed/1013` 100 (LD-30, LD-33) | <span class="tag measured">MEASURED</span> ceiling; <span class="tag inferred">INFERRED</span> cause |
| Right half's LEDs dark, typing works | halves on different firmware (`fe/1002` on both) | match the firmware (LD-74) | <span class="tag measured">MEASURED</span> 3.35.4 / 3.41.0 |
| Keys go dark on battery after 90 s, one tap restores | idle timer | none needed; change the timeout on [Settings and timing](settings.md) | <span class="tag measured">MEASURED</span> 3.41.0 |
| Still dark | the KB's recovery ladder (LD-71), then `30/10ca` | untested by us; `30/10ca` wipes the keymaps, LED maps and (reportedly) the layer list: see [Factory reset](../storage/factory-reset.md) | <span class="tag reported">REPORTED</span> |

## Open questions

- <span class="tag open">OPEN</span> Which physical edge carries indices 74-80; how many bay indices a Tune and a Track follow ([details](../open-questions.md#oq-h08))
- <span class="tag open">OPEN</span> What the board shows for saturation 150; which NayaFlow row (88 or 89) feeds each bay; what changed in the inter-half LED data between 3.35.4 and 3.41.0; the dimming and brightness-inversion reports ([details](../open-questions.md#oq-p19))
- <span class="tag open">OPEN</span> The `ed/1050` clear value; `ed/1009`-`100c`; what `ed/10d1` / `10d2` do ([details](../open-questions.md#oq-p06))
- <span class="tag open">OPEN</span> Whether a layer-list rewrite clears an `ed/1050` override ([details](../open-questions.md#oq-p17))
- <span class="tag open">OPEN</span> The community observations nobody else has measured: `ed/1050` persistence, ON versus brightness 0, `ed/1014` on the right half, module LEDs under a zero ceiling ([details](../open-questions.md#oq-p25))
- <span class="tag open">OPEN</span> The meaning of the module's red-red-red-green blink ([details](../open-questions.md#oq-h32))
- <span class="tag open">OPEN</span> How the device treats `ed` params sent without the leading flag byte: left to the conversation with naya-create-kb's maintainer, not measured by us.

## Sources

[^kb-led]: naya-create-kb, [protocol/led](https://nemezzizz.github.io/naya-create-kb/protocol/led/) (commit 7668067).
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-settings]: naya-create-kb, [protocol/settings](https://nemezzizz.github.io/naya-create-kb/protocol/settings/) (commit 7668067).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`cli/led.py`, LED palette and color decoding).
[^nx-pr6]: nayactl, [pull request 6](https://github.com/Qonfused/nayactl/pull/6) (NayaCore 6.11.0 LED command table, `ed/1012`-`1014`, the zero-fill comment and the author's oversized-write and module-LED observations).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): LED log line, LED command names, LED-key color table.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings, templates and the default "Rainbow" palette (static reading).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (LED-map dumps, USB CDC capture logs and tool sources); raw data decoded by us, never copied.
[^zmk]: ZMK documentation, [RGB underglow](https://zmk.dev/docs/keymaps/behaviors/underglow).
[^nh-cl]: create-legacy-firmware, vendor release notes, [changelogs/](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (v1.17.2, v1.25.0).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (v1.17.1, v1.22.0, v1.23.0, v1.24.0).
[^fp-mismatch]: create-legacy-firmware, [FLASHING-PROCEDURE.md, "Pairing and firmware mismatch"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L369-L384) (commit cdd897c).

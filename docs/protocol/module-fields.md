# Module fields

This page goes inside one module config slot: the field record types, the two-word motion
categories, the field map of each module (Track 15 fields, Tune 36, Touch 31 in the stock profile),
the setting fields and their units, how axes pair and split, which fields the module firmware owns,
what a field accepts, and what the host actually receives when a gesture fires. The one thing to know
first: every gesture direction is its own field, a field takes almost any record type, and what
reaches the computer is plain HID, so a module gesture bound to a key cannot be told apart from a
keyboard key. Where configs live and how slots are chosen is on [Modules](modules.md).

!!! note "At a glance"
    - A field is `[field][type][len][value]`, the same shape as a key record; the type decides what it holds.
    - Fields `00`-`04` are one-byte settings on every module; the Tune adds `05`-`07` (detents).
    - A two-word record `0f` carries a motion category (0-8) and a signed selector (+1 / -1) or a button mask.
    - Every axis is two fields, one per direction; invert is a selector swap, not a flag.
    - Two-finger gestures stream events; one-, three- and four-finger swipes, taps and dial detents send one.

Stock readings are from the owner's board (keyboard 3.41.0; module 2.3.3 for the Tune and the Track;
the Touch read from 2026-09-08) unless a row says otherwise. Field records are quoted as
`[field][type][len][value]`; a write carries them after params `00 <slot>` (see [Modules](modules.md)
and the [byte convention](transport.md#byte-convention)). Direction names are attributed to their
vocabulary (NayaFlow's module editor, NayaCore's action map).

## Field records and categories

<!--MF-01-->A field is `[field][type][len][value]`, the same shape as a key record, and the TYPE decides
what it holds <span class="tag measured">MEASURED</span> 3.41.0, 2026-09. naya-create-kb describes the
same records from a static decode[^kb-modules].

| Type | Len | Holds | Example |
|---|---|---|---|
| `01` | 1 | a setting byte | `00 01 01 0a` = field 0, value 10 |
| `01` | 4 | a key press `[usage lo][usage hi][page][mods]` | `08 01 04 2a 00 07 00` = field 8, Backspace |
| `0f` | 8 | a two-word `[category u32 LE][selector i32 LE]` | `0b 0f 08 03 00 00 00 01 00 00 00` = button M1 |
| `07` | 0 | empty (on four Touch fields: "module firmware default", MF-34) | `08 07 00` |
| `00` | 0 | the blank-template record | `05 00 00` |
| `0c` | 4 | a TO-layer record (also accepted) | `22 0c 04 01 00 00 00` |

<!--MF-02-->The two-word categories are NayaCore's enum, in order
<span class="tag static">STATIC</span>[^nc]; the host effect of 0, 1, 3, 4, 6 and 8 is measured
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09 (zoom 2026-09-18). Motion selectors are
+1 / -1. Categories 2, 5 and 7 were written and "work but are not useful". naya-create-kb lists the
same nine names as "host gesture slots"[^kb-settings]; they are the categories of this record, used in
module fields and on keys, not slots.

| Category | NayaCore name | Meaning | Selector |
|---|---|---|---|
| 0 | MOUSE_HORIZONTAL | pointer X | -1 / +1 |
| 1 | MOUSE_VERTICAL | pointer Y | -1 / +1 |
| 2 | MOUSE_STATIC | (works, not useful) | |
| 3 | MOUSE_BUTTONS | mouse buttons | mask 1 / 2 / 4 / 8 / 16 = M1-M5 |
| 4 | MOUSE_SCROLL_VERTICAL | vertical scroll | -1 / +1 |
| 5 | STATIC_SCROLL_VERTICAL | (works, not useful) | |
| 6 | MOUSE_SCROLL_HORIZONTAL | horizontal scroll | -1 / +1 |
| 7 | STATIC_SCROLL_HORIZONTAL | (works, not useful) | |
| 8 | STATIC_ZOOM | zoom | pinch -1 = zoom out, spread +1 = zoom in |

<!--MF-03-->Single-direction motion records exist for categories 4, 6, 0 and 1 (eight records, each at
-1 and +1) and for 8 (the zoom pair). Mouse button M5 (mask 16) was proven by writing it into a Tune
tap: it drove the browser's Forward <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-06.

<!--MF-04-->Granularity comes from the gesture, not from the category: gestures that stream motion
(the Touch's one finger, two fingers on either module) move smoothly; three- and four-finger gestures
emit discrete events, so a motion record there moves a few pixels or scrolls one line per event
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-18.

## Setting fields

<!--MF-10-->Fields `00`-`04` on every module are one-byte settings
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11: `00` pointer speed (10 stock), `01`
scroll speed (Touch 50, Track and Tune 10), `02` pointer acceleration (50), `03` acceleration on (1;
the name is <span class="tag inferred">INFERRED</span> from NayaFlow's settings order and NayaCore's
`pointer_acceleration_toggle`), and `04` unknown (0 everywhere; setting it to 1 changed nothing
observed). NayaCore 6.11.0 writes every field below its per-type first gesture field (5 for Touch and
Track, 8 for Tune) as a one-byte `01` setting record, which fixes the setting ranges at `00`-`04` and
`00`-`07` <span class="tag static">STATIC</span>[^nc-disasm].

<!--MF-11-->Pointer speed clamps at 100 (255 behaves as 100); acceleration at 50 or 100 changed nothing
observable on the Tune's two-finger pointer records <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-05.

<!--MF-12-->Tune field `05` is the detent spacing in DEGREES: detents per turn = 360 / value. The stock
5 is NayaFlow's default of 72 detents; the minimum of NayaFlow's slider (5-170 detents) is the byte
72; 36 gave about 10 detents, 10 about 33, and 90 exactly 4. Detent strength did not change with it
<span class="tag measured">MEASURED</span> 3.41.0, module 2.3.3, 2026-09-16. Tune `06` (75 stock) and
`07` (1) are <span class="tag inferred">INFERRED</span> to be detent strength and detents on/off
(NayaCore names `tick_current` and `tick_toggle`); NayaCore's own defaults are 5 for `05` and 75 for
`06` <span class="tag static">STATIC</span>[^nc-disasm].

| Field | Module | Setting | Stock | Evidence |
|---|---|---|---|---|
| `00` | all | pointer speed (clamps at 100) | 10 | <span class="tag measured">MEASURED</span> |
| `01` | all | scroll speed | Touch 50, Track and Tune 10 | <span class="tag measured">MEASURED</span> |
| `02` | all | pointer acceleration | 50 | <span class="tag measured">MEASURED</span> |
| `03` | all | acceleration on | 1 | <span class="tag inferred">INFERRED</span> name |
| `04` | all | unknown | 0 | <span class="tag measured">MEASURED</span> (no effect seen) |
| `05` | Tune | detent spacing, degrees (360 / value detents) | 5 (72 detents) | <span class="tag measured">MEASURED</span> |
| `06` | Tune | detent strength | 75 | <span class="tag inferred">INFERRED</span> |
| `07` | Tune | detents on/off | 1 | <span class="tag inferred">INFERRED</span> |

## Field maps

!!! warning "Field writes change a live config"
    Probe a field with a sparse single-field write (params `00 <slot>` + one record): back up the
    slot, write one field, read back and compare every other field, test with a binding whose result
    differs from before, then restore the saved slot.

<!--MF-20-->**Track** (15 fields, `00`-`0e`, which is NayaCore's `maxSlots` for the Track
<span class="tag static">STATIC</span>[^nc-disasm]): `00`-`04` settings; `05`/`06` vertical
(category 1, -1 / +1); `07`/`08` horizontal (category 0; -1 fires on physical left, +1 on right);
`09`/`0a` rotate (category 4: `09` is the +1 half and `0a` the -1 half, the opposite field order to
the other axes); `0b`-`0e` buttons 1-4 (category 3; the stock Track Left masks are 1, 4, 2, 8 = M1, M3,
M2, M4). The Track Right on the board differs: `0b` empty (a NayaFlow flash had cleared it), `0c` M2,
`0d` M3, `0e` M1 <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02. naya-create-kb lists
the Track's vocabularies on its hardware page[^kb-hardware].

<!--MF-21-->The Track has no field for a button HOLD: asked for tap `d` / hold `a` on button 1, NayaFlow
wrote `a` into `0b` and `d` nowhere, and the button then emits `a`. Track buttons also accept key-press
records (a NayaFlow profile stored D, R, S and T in `0b`-`0e`). Swapping the rotate pair's selectors
makes clockwise scroll down <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-02/03.

<!--MF-22-->**Tune** (36 fields, `00`-`23`, NayaCore's `maxSlots` for the Tune
<span class="tag static">STATIC</span>[^nc-disasm]) <span class="tag measured">MEASURED</span> 3.41.0,
module 2.3.3, 2026-09-02 to 2026-09-18:

| Field | Gesture | Stock binding |
|---|---|---|
| `00`-`07` | settings (MF-10, MF-12) | |
| `08` | one-finger tap | empty |
| `09` | spare (never fires) | |
| `0a` / `0b` | one-finger vertical (category 4): `0a` fires on swipe UP, `0b` on DOWN | scroll |
| `0c` / `0d` | one-finger horizontal (category 6): left / right | scroll |
| `0e` | two-finger tap | C_PLAY_PAUSE |
| `0f` | spare | |
| `10`-`13` | two-finger swipe up / down / left / right | C_BRIGHTNESS_INC, C_BRIGHTNESS_DEC, C_REWIND, C_FAST_FORWARD |
| `14` / `15` | pinch / spread (the two-finger zoom pair) | empty |
| `16` | three-finger tap | C_MUTE |
| `17` | spare | |
| `18` / `19` | three-finger swipe up / down | empty key presses (NayaFlow's LED Brightness Up / Down) |
| `1a` / `1b` | three-finger swipe left / right | C_PREVIOUS, C_NEXT |
| `1c`-`21` | unknown | |
| `22` | dial clockwise | C_VOL_UP |
| `23` | dial counter-clockwise | C_VOL_DOWN |

<!--MF-23-->**Touch** (stock "Naya Touch Windows", 31 fields `00`-`1e`, NayaCore's `maxSlots` for the
Touch <span class="tag static">STATIC</span>[^nc-disasm]) <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-09/10:

| Field | Gesture | Stock binding |
|---|---|---|
| `00`-`04` | settings (MF-10) | |
| `05`-`08` | one-finger cursor | empty (module default) |
| `09` / `0a` | unknown (a second category-4 pair position) | unused |
| `0b` | one-finger tap | empty (module left click) |
| `0c` | two-finger tap | empty (module right click) |
| `0d` / `0e` | two-finger vertical scroll, up / down | scroll |
| `0f` / `10` | two-finger horizontal scroll, left / right | scroll |
| `11` / `12` | pinch / spread | empty |
| `13` | three-finger tap | M3 |
| `14` | spare | |
| `15`-`18` | three-finger swipes | LAlt+LShift+Esc, LAlt+Esc, LCtrl+LShift+Tab, LCtrl+Tab |
| `19` | four-finger tap | LGui+Tab |
| `1a` | spare | |
| `1b`-`1e` | four-finger swipes | LAlt+PgUp, LAlt+PgDn, LGui+LCtrl+Left, LGui+LCtrl+Right |

<!--MF-24-->Gesture fields repeat per finger count as `[tap][spare][up][down][left][right]`, with extra
trailing fields at two and three fingers on the Tune. The spare after each tap fired for neither hold
nor double tap <span class="tag measured">MEASURED</span> 3.41.0, 2026-09.

## Axis model and firmware-owned fields

<!--MF-30-->Every axis gesture is TWO fields, one per direction, and the selector's sign is the
direction (-1 = left / up / counter-clockwise / pinch, +1 = right / down / clockwise / spread). There is
no combined field. Splitting an axis in NayaFlow just writes the two halves independently (a captured
split wrote `07` = key press `s`, `08` = key press `g`). The Tune dial is a pair of key-press fields
(`22` +, `23` -) <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03.

```
axis = two fields          left / up  field: 0f category -1        right / down field: 0f category +1
invert = swap selectors    left / up  field: 0f category +1        right / down field: 0f category -1
split = independent        left / up  field: 01 key press "s"      right / down field: 01 key press "g"
```

<!--MF-31-->Invert is a selector swap, not a stored flag: settings `03` and `04` did not change across an
invert. Whether NayaFlow's invert reaches the device is disputed between two of our readings: a
capture of unchecking invert showed no write at all (2026-09-03), while a later reading of a user
database whose inversion works on hardware carries `invert = 1` on the inverted axes (2026-09-12); the
later reading is preferred <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03 and
2026-09-12.

<!--MF-32-->Cross-axis records are honored: a vertical-scroll record written into the Touch's
horizontal minus field made a two-finger LEFT swipe scroll vertically
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-16.

<!--MF-33-->Scroll direction naming: NayaFlow's module editor names follow macOS natural scrolling, so
the record it calls "Scroll up" (category 4, -1) scrolled the page DOWN on a Windows host. The stock
Tune and Touch bind a finger swipe up to (4, -1) <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-16. NayaCore's single-action map lists SCROLL_UP as (4, +1)
<span class="tag static">STATIC</span>[^nc]. Horizontal and pointer signs per host OS are not measured.

<!--MF-34-->On the Touch, four fields are owned by the module firmware while they are empty: `05`-`08`
(one-finger cursor), `0b` (one-finger tap = left click) and `0c` (two-finger tap = right click).
NayaFlow writes them empty and locks them; a key press written into `0b` or `0c` reads back but is
ignored (the taps still click). Explicit pointer records give only coarse motion. Whether a key in
`05`-`08` does anything is untested <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-09/10.
Keep these fields empty.

## What a field accepts, and what is not a field

<!--MF-40-->Fields are not type-locked: Tune `08` took a key press and later a mouse button, and Track
button fields took key presses. The dial field `22` accepted a chord (LCtrl+Tab cycled tabs), a
two-word scroll record (clockwise scrolled up) and a `0c` TO-layer record (rotation switched layers).
Among layer records only TO-layer has been tried <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-03.

<!--MF-41-->Pointer records written into the Tune's two-finger swipe fields move the cursor, but only in
four directions, in about 20 quantized steps per swipe, with slow drags traveling further than fast
flicks. The Tune ships no pointer records; that is stock content, not a firmware limit
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-05.

<!--MF-42-->The module firmware validates record types: a type `7e` record was dropped
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-07.

<!--MF-43-->Not available as fields: a Track button hold (MF-21); any Tune hold (a held finger fires the
swipe-up binding on lift); and double tap on the Touch and the Tune
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09. NayaCore refuses a double tap there
("Encountered unsupported double tap behaviour for Touch/Tune module type"), and NayaFlow never writes
the pinch and spread fields: its database held pinch bindings that the flash dropped
<span class="tag static">STATIC</span>[^nc].

## Stock bindings and names

<!--MF-50-->NayaFlow's installer embeds the fresh-install module bindings: a Track profile (horizontal
and vertical rows), "Naya Tune" (13 rows), "Naya Touch Windows" (12) and "Naya Touch MacOS" (11). Touch
MacOS differs from Windows in its three- and four-finger chords (for example three-finger up
LGui+Grave, four-finger left LCtrl+Left). No one-finger or one- and two-finger-tap Touch rows exist,
because the firmware owns them <span class="tag static">STATIC</span>[^nf].

<!--MF-51-->NayaCore 6.11.0's gesture list (110 names) has Touch 35, Track 28, Tune 38 and Float 9
entries (Float: `translation_x/y/z:float:3d_nav`, `rotation_x/y/z:float:3d_nav`, and dial rotation,
clockwise and anti-clockwise). Beside them NayaCore names Float-like settings and directions
(`dial_tracking_speed`, `translation_sensitivity`, `rotation_sensitivity`, `response_curve`,
`crown_cw`, `x_left` ... `yaw_right`) <span class="tag static">STATIC</span>[^nc]. These are the app's
vocabulary, not a list of what firmware supports. naya-create-kb lists gesture vocabularies on its
hardware page[^kb-hardware].

## What the host receives

<!--MF-52-->What the host receives is plain HID: keyboard usages, consumer usages, mouse buttons,
motion and wheel. A module gesture bound to a key is indistinguishable from a keyboard key
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09. The config that decides what each gesture
sends lives on the keyboard's left half and is picked per layer by the bays, while gesture
recognition and streaming happen inside the module's own firmware
<span class="tag inferred">INFERRED</span> (strong). naya-create-kb observes the same for the trackball
over Bluetooth[^kb-ble]; see [Bluetooth](../connectivity/bluetooth.md).

<!--MF-53-->Tune two-finger swipes STREAM, quantized on accumulated motion rather than time: about 1 cm
fast gives 8-9 events in about 85 ms, the whole pad fast 16, slowly 24-27; the stream stops when the
fingers stop; small circles give 32; gaps can be as short as 2 ms. One- and three-finger swipes, taps
and dial detents send exactly one event (classified on release). A tap is a key blip of about 1 ms on
lift; a double tap fires the single-tap binding twice. Dial detents arrive about 400-500 ms apart at
moderate speed and about 40 ms apart in fast bursts. Module chords press and release the modifier
around every event, the modifier leading by at most 1 ms (Tune) or 5 ms (Touch)
<span class="tag measured">MEASURED</span> 3.41.0, Windows host, 2026-09-04/05.

<!--MF-54-->The Touch with the stock profile: two-finger scroll streams wheel reports; one finger streams
cursor reports; four-finger up and down stream chords (runs of 8 and 7); three-finger swipes and
four-finger left and right send one. Bound to plain keys, the two-finger axes send one key per scroll
report and four-finger up and down scale with distance; the unflashed one-finger defaults leak a click
or a few cursor pixels during multi-finger gestures. Pinch and spread arrive as runs scaled to finger
travel. The Track ball sends 400-1500 HID reports per movement
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03 to 2026-09-18.

<!--MF-55-->Because two-finger gestures stream, a one-shot action (Play/Pause) bound to a Tune
two-finger swipe fires 11-20 times <span class="tag measured">MEASURED</span> 3.41.0, 2026-09. Host
tools that remap module keys collapse such a run: Create Companion groups keys within 300 ms
<span class="tag static">STATIC</span>[^cc].

| Gesture | Stream or one-shot | Events measured |
|---|---|---|
| Tune two-finger swipe | stream | 8-9 (1 cm fast), 16 (whole pad fast), 24-27 (slow), 32 (small circles) |
| Tune one- and three-finger swipe, tap | one-shot | 1 (on release) |
| Tune dial detent | one per detent | 400-500 ms apart, about 40 ms in bursts |
| Touch one finger | stream (cursor) | continuous |
| Touch two-finger scroll | stream (wheel) | continuous |
| Touch four-finger up / down | stream (chords) | runs of 8 and 7 |
| Touch three-finger swipe, four-finger left / right | one-shot | 1 |
| Touch pinch / spread | stream | scaled to finger travel |
| Track ball | stream | 400-1500 reports per movement |

## Open questions

- <span class="tag open">OPEN</span> Field `04` on every module; Tune `06` / `07` on the wire, Tune `1c`-`21`; Touch `09` / `0a`; the spare fields; whether keys in the Touch's `05`-`08` act; whether MO and sticky-layer records work in a field; horizontal and pointer signs per host OS; whether the stock Track axes carry invert = 1 ([details](../open-questions.md#oq-p22))
- <span class="tag open">OPEN</span> What the keyboard does with the Tune's empty-key-press LED gestures ([details](../open-questions.md#oq-p13))

## Sources

[^kb-modules]: naya-create-kb, [protocol/modules](https://nemezzizz.github.io/naya-create-kb/protocol/modules/) (commit 7668067).
[^kb-settings]: naya-create-kb, [protocol/settings](https://nemezzizz.github.io/naya-create-kb/protocol/settings/) (commit 7668067).
[^kb-hardware]: naya-create-kb, [device/hardware](https://nemezzizz.github.io/naya-create-kb/device/hardware/) (commit 7668067).
[^kb-ble]: naya-create-kb, [connectivity/ble](https://nemezzizz.github.io/naya-create-kb/connectivity/ble/) (commit 7668067).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): the category enum, the gesture list, the single-action map, the double-tap refusal.
[^nc-disasm]: NayaFlow 1.25.1, NayaCore 6.11.0 (Windows x64), our disassembly (2026-09-23): `ModuleConfig::maxSlots`, `ModuleConfig::behaviourSlotStart`, `ModuleConfig::defaultValue` and the module-config serializer.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings and templates (static reading): the fresh-install module bindings.
[^cc]: Create Companion, [github.com/create-collective/create-companion](https://github.com/create-collective/create-companion) (MIT).

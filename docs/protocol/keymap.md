# Keymap records

This page describes what a layer's key data looks like on the wire: the 156 positions of a layer,
the record format, every record type, the two hold-tap forms, the second bank that carries double
tap and tap and hold, and the module bay records that sit in the middle of the key data. It also
covers how NayaCore and other writers change a layer, and the traps that have corrupted real
boards. The one thing to know first: a layer read is lossless only if the reader keeps both banks
and the bay records; a writer that drops either one corrupts the board silently.

!!! note "At a glance"
    - One layer = 156 positions, all stored on the left half: keys `00`-`49`, module bays `4a`-`51`,
      second bank `52`-`9b`.
    - Every record is `[position][type][len][param]`; reads and writes use the same format.
    - `03` and `10` are the two hold-tap forms; the flavor byte and the tapping term live inside
      each record, not in a device setting.
    - A key's double tap and tap and hold sit in its second-bank record, `0x52` positions later.
    - `30/1004` writes take effect at once and persist; there is no commit and no undo.

Byte strings follow the site's [byte convention](transport.md#byte-convention). On this page,
records are quoted as record bytes `[position][type][len][param]` (no flag byte and no layer
byte) unless a string is labeled "params"; `pp` stands for any position. Positions written in
prose ("position 62") are decimal; inside byte strings they are hex (62 = `3e`). Physical key
positions and labels belong to [Layout and positions](../hardware/layout.md).

## Positions

<!--KM-01-->One layer covers the whole keyboard, both halves. Positions `00`-`49` are the 74
keys, `4a`-`51` are the eight module bays, and `52`-`9b` are the second bank (one extra record per
key, keys only), so a layer has 82 + 74 = 156 positions. All of it is stored and served by the left
half. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

| Positions | What they hold |
|---|---|
| `00`-`49` | the 74 keys (tap and hold) |
| `4a`-`51` | the eight module bays (a config slot number, not a binding; see [Bays](#module-bays-in-layer-data)) |
| `52`-`9b` | the second bank: double tap and tap and hold for key `p` at `p + 52` |

<!--KM-02-->The position byte is the key's index and equals NayaFlow's database `position_id`
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09. naya-create-kb calls the same byte
"KK"[^kb-keymap].

<!--KM-03-->Layers are not fixed at three. They come from the layer list and can be added and
deleted (NayaFlow created layers 3 and 4 in one captured flash); NayaCore names a `MAX_LAYERS`
constant whose value we have not recovered. See [Layers](layers.md).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 + <span class="tag static">STATIC</span>[^nc]

<!--KM-04-->Layer 0 of the stock profile starts along the top row with Esc (`29`), Grave (`35`),
`1` (`1e`) and `2` (`1f`): the stock read on the owner's board begins `00 01 04 29 00 07 00`,
`01 01 04 35 00 07 00`, `02 01 04 1e 00 07 00`, `03 01 04 1f 00 07 00`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 + <span class="tag static">STATIC</span>
(NayaFlow's default template[^nf]); also reported by naya-create-kb[^kb-keymap].

## The record format

<!--KM-10-->Every record is `[position][type][len][param x len]`, so a record is `len + 3` bytes.
Writes use exactly the read format. The rule closes over every layer read we have made, whether the
layer returned 82 or 156 records, and over every third-party read we decoded.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 to 2026-09-17. naya-create-kb reports
the same rule, proven by its own census of 1 776 records[^kb-keymap].

<!--KM-11-->The type byte is an index into NayaCore's behavior table: `00` bluetooth, `01`
key_press, `02` macro, `03` mod_tap, `04` grave_escape, `05` mo, `06` naya_integrations, `07` none,
`08` outputs, `09` rgb_ug, `0a` sticky_key, `0b` sticky_layer, `0c` to_layer, `0d` toggle_layer,
`0e` trans, `0f` mouse. `10` (the hold-tap used for multi-behavior keys, "OneKey" in OpenFlow) sits
outside that table, and `78` appears only at bays. Eight of the indices were matched against
captured records. <span class="tag static">STATIC</span>[^nc] + <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

| Type | NayaCore name | ZMK behavior | Param | Example record | Evidence | In NayaFlow |
|---|---|---|---|---|---|---|
| `00` | bluetooth | `&bt` | `[command u32 LE][argument u32 LE]` | `pp 00 08 03 00 00 00 01 00 00 00` (device 1) | <span class="tag measured">MEASURED</span> | action type "bluetooth" |
| `01` | key_press | `&kp` | `[usage lo][usage hi][page][mods]` | `22 01 04 07 00 07 00` (D) | <span class="tag measured">MEASURED</span> | key action |
| `02` | macro | `&macro` | accepted, does nothing | (none flashed) | <span class="tag measured">MEASURED</span> | macro (flashed as `07 00`) |
| `03` | mod_tap | `&mt` / `&lt` | the 21-byte hold-tap body | stock layer-tap at `07`, `08` | <span class="tag measured">MEASURED</span> | a key with tap and hold |
| `04` | grave_escape | `&gresc` | no serializer | (cannot be flashed) | <span class="tag static">STATIC</span> | none |
| `05` | mo | `&mo` | target layer u32 LE | `pp 05 04 01 00 00 00` | <span class="tag measured">MEASURED</span> | Hold Layer |
| `06` | naya_integrations | (vendor) | command u32 LE | `3e 06 04 91 01 00 00` | <span class="tag measured">MEASURED</span> | action type "naya" |
| `07` | none | `&none` | none | `pp 07 00` | <span class="tag measured">MEASURED</span> | an unbound key |
| `08` | outputs | `&out` | selector u32 LE | `pp 08 04 02 00 00 00` | <span class="tag measured">MEASURED</span> | BT_OUT, USB_DEVICE |
| `09` | rgb_ug | `&rgb_ug` | `[subcommand u32][argument u32]` | see [LEDs](led.md) | <span class="tag measured">MEASURED</span> | action type "LED" |
| `0a` | sticky_key | `&sk` | no serializer | (cannot be flashed) | <span class="tag static">STATIC</span> | none |
| `0b` | sticky_layer | `&sl` | target layer u32 LE | `pp 0b 04 01 00 00 00` | <span class="tag measured">MEASURED</span> | `layer_polite_oneshot` |
| `0c` | to_layer | `&to` | target layer u32 LE | `pp 0c 04 02 00 00 00` | <span class="tag measured">MEASURED</span> | `layer_rude_toggle` |
| `0d` | toggle_layer | `&tog` | target layer u32 LE | `pp 0d 04 01 00 00 00` | <span class="tag measured">MEASURED</span> | `layer_polite_toggle` |
| `0e` | trans | `&trans` | none | `pp 0e 00` | <span class="tag measured">MEASURED</span> | a new layer's unassigned key |
| `0f` | mouse | (vendor) | `[category u32 LE][selector i32 LE]` | `2e 0f 08 03 00 00 00 01 00 00 00` (left click) | <span class="tag measured">MEASURED</span> | mouse button |
| `10` | (outside the table) | hold-tap with term | `[term u16 LE][03]` + body | `49 10 18 c8 00 03 ...` | <span class="tag measured">MEASURED</span> | tap, hold, double tap, tap and hold |
| `78` | (bays only) | | none | `4a 78 00` | <span class="tag measured">MEASURED</span> | a bay that follows layer 0 |

## Key press parameters

<!--KM-12-->A `01` KEY_PRESS record carries four param bytes, `[usage lo][usage hi][page][mods]`:
ZMK's u32 `(mods<<24)|(page<<16)|usage`, stored little-endian. Page `07` is the keyboard page and
`0c` the consumer page; NayaCore's key table also uses page `01` (Generic Desktop) for
SYSTEM_POWER, SLEEP and WAKE_UP (`81`-`83`). Worked record: `22 01 04 07 00 07 00` is position `22`,
key D. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09. naya-create-kb names the fields
HID, PAGE_BE and MOD; its formula is right, but byte 1 is the usage's high byte and the page is a
single byte[^kb-keymap].

<!--KM-13-->`mods` is the HID modifier bitmap (naya-create-kb's MODMASK): `01` LCtrl, `02` LShift,
`04` LAlt, `08` LGui, `10` RCtrl, `20` RShift, `40` RAlt, `80` RGui. A bare modifier key is its own
usage (`e0`-`e7`) with mods 0; a shifted glyph is the base usage plus LShift (`)` is key 0 plus
`02`). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09. In the stock profile the only
records with modifiers are layer 1 positions `1c` and `1d`, the parentheses: `26 00 07 02` and
`27 00 07 02` (param bytes). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01; also
reported by naya-create-kb[^kb-keymap]. Edited profiles carry other modifiers, and so do stock
module fields.

<!--KM-14-->Consumer usages seen on the wire include `b5` Next, `b6` Previous, `cd` Play/Pause, `e2`
Mute, `e9` Volume Up and `ea` Volume Down. naya-create-kb's example "C_MUTE `20 01 04 b6 00 0c 00`"
is Previous Track: in the HID Consumer page `b6` is Scan Previous Track and Mute is `e2`[^hid]. The
stock Tune fields confirm it (`e2 00 0c 00` for mute, `b6 00 0c 00` for previous).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09 + <span class="tag doc">DOC</span>

<!--KM-15-->A key press of four zero bytes (`pp 01 04 00 00 00 00`) presses nothing and is not
the same record as NONE (`07 00`). The board carries it on an unset hold-tap half and on the two
stock Tune gestures NayaFlow labels LED Brightness Up and Down. What the keyboard does with it is
open. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-16-->Modifier-only records exist. NayaFlow flashes "LALT + CLICK" as usage 0, page 0, mods
`04` (param `00 00 00 04`). A bracketed modifier in NayaFlow's chord syntax ("[LALT] + TAB") marks a
key that is already held and does not set its bit (`2b 00 07 00`). NayaFlow stores "LALT + ENTER" as
`00 00 00 04`, losing the Enter: a vendor bug. <span class="tag measured">MEASURED</span> NayaFlow
1.25.1 captures on 3.41.0, 2026-09

<!--KM-17-->The international usages `87`-`8f` and the LANG usages `90`-`98` are standard and
encodable. NayaCore's 249-entry key table (in ZMK order) adds PIPE2 = LShift + NON_US_BACKSLASH and
TILDE2 = LShift + NON_US_HASH. <span class="tag static">STATIC</span>[^nc]

## Record types in detail

<!--KM-18-->**`02` macro.** The firmware reserves the type and the macro opcodes but keeps no macro
table: a `02` record is accepted on read-back and does nothing. NayaCore flashes a macro binding as
`07 00` (see [Command map](commands.md)). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-07

<!--KM-19-->**`05` MO (momentary layer, "Hold Layer").** The param is the target layer, u32 LE:
`pp 05 04 01 00 00 00` holds layer 1. Stock layer 0 uses `05` layer 1 on the two thumb keys at
positions 67 and 68 (LH4, RH4) and `05` layer 2 on the two bottom-corner keys at 62 and 73 (LA5,
RA5, "hold System" in the vendor template), whose keycap print differs from the action. On the
owner's board the stock read holds `43 05 04 01 00 00 00`, `44 05 04 01 00 00 00`,
`3e 05 04 02 00 00 00` and `49 05 04 02 00 00 00`. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-01 + <span class="tag static">STATIC</span> (template[^nf]); also reported by
naya-create-kb[^kb-keymap].

<!--KM-20-->**`06` Naya system action.** The param is a u32 LE command. The only value known on the
wire is 401 = MODULE_FORCE_CHARGING, on the stock System layer at position 62:
`3e 06 04 91 01 00 00` (NayaFlow: "Activate Module Recovery Mode"; see [Modules](modules.md)).
NayaCore's table also names TUNE_MODE_L / TUNE_MODE_R (150 / 151), WINDOWS_OS (200), MAC_OS (201),
SCROLL_DIRECTION_L / _R (300 / 301) and MODULE_CHARGING (400); none has been seen on a board.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08; 3.28.7, 2026-09-19 +
<span class="tag static">STATIC</span>[^nc]. naya-create-kb lists the same eight values but states
that no genuine wire sample exists; the stock record above is one[^kb-keymap]. It also reports that
the palette's macOS entry is flashed as a plain LGUI key press rather than a `06` record
<span class="tag reported">REPORTED</span>[^kb-keymap]; a captured NayaFlow flash of that palette
key would settle it.

<!--KM-21-->**`07` NONE** (`&none`) has no param. Every unbound position reads back as `07 00`; a
board read returns about 220 NONE records. naya-create-kb calls it DISABLE[^kb-keymap].
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-22-->**`08` outputs** (`&out`) takes a u32 LE selector: 1 = USB, 2 = wireless. The stock
System layer holds `pp 08 04 02 00 00 00` (BT_OUT) at positions 47 and 71 and `pp 08 04 01 00 00 00`
(USB_DEVICE) at 48 and 72. Decoding `08` as a layer switch and flashing the result back turned those
keys into "force layer 2 / 1": a real corruption. <span class="tag measured">MEASURED</span> 3.41.0,
2026-09-08

<!--KM-23-->**`0b` sticky layer, `0c` TO layer ("force"), `0d` TOGGLE layer** are all live on the
wire, each with the target layer as a u32 LE param. A probe profile read back four sticky records,
and a 2026-09-10 board read held seven TO and four sticky records among 182, all round-tripping byte
for byte. NayaFlow calls them `layer_polite_oneshot`, `layer_rude_toggle` and
`layer_polite_toggle`. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08, 2026-09-10.
naya-create-kb lists these three as dead types never seen on the wire[^kb-keymap].

<!--KM-24-->**`0e` TRANS** (transparent) has no param. NayaCore writes a new layer's unassigned keys
as `0e 00`. It picks `07` or `0e` for an unassigned key from the profile's "transparent as default"
setting: its logs print "transparent as default" per profile and "(Transparent from default)" or
"(Transparent from settings)" per key. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01
+ <span class="tag static">STATIC</span>[^nc]; also reported by naya-create-kb[^kb-keymap].

<!--KM-25-->**`00` bluetooth** (`&bt`) takes `[command u32 LE][argument u32 LE]`. `(3, n)` selects
Bluetooth device n, ONE-based: keys Dev 1-4 read back `(3, 1)` to `(3, 4)`. `(0, 0)` is BT_CLEAR, a
real record, not NONE. `(1, 0)` next and `(2, 0)` previous come from NayaCore's table and have never
been read off a board. BT_DEVICE_1 as a record: `pp 00 08 03 00 00 00 01 00 00 00`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08, 2026-09-10 +
<span class="tag static">STATIC</span>[^nc]

<!--KM-26-->**`09` rgb_ug** (LED keys) takes `[subcommand u32][argument u32]`; the subcommands and
colors are on [LEDs](led.md). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-08

<!--KM-27-->**`0f` two-word** takes `[category u32 LE][selector i32 LE]`. On a key, category 3 with a
mouse-button mask (1, 2, 4, 8, 16 = M1-M5) makes a mouse button: `2e 0f 08 03 00 00 00 01 00 00 00`
gave a real left click at position 46. A short param (`pp 0f 04 01 00 00 00`) is stored, read back
verbatim, and ignored. The categories are on [Module fields](module-fields.md).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-07

<!--KM-28-->naya-create-kb's "vendor action" id `(A<<16)|(X<<8)|Y` for types `00`, `09` and `0f` is
not a wire field: on the wire each of these records is the type byte plus two independent u32 LE
words (for `0f` the second is signed)[^kb-keymap]. <span class="tag inferred">INFERRED</span> from
the three measured forms above.

<!--KM-29-->`03` and `10` are the two hold-tap forms (next section). `03` is the general
two-behavior hold-tap (home-row modifiers, the stock layer-tap), not a "hold-only" record, and
naya-create-kb's "`03` (macro)" is a different thing: NayaCore's macro index is `02`[^kb-keymap].
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-30-->`04` grave_escape and `0a` sticky_key are named in NayaCore's table but have no
serializer, so nobody can flash them. <span class="tag static">STATIC</span>[^nc]

<!--KM-31-->The firmware validates the type: a record of unknown type `7e` was dropped and the
previous record survived. A stored record is still not necessarily live (the short `0f` param above).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-07

## Hold-tap records and the second bank

<!--KM-40-->The hold-tap body is 21 bytes:

| Offset in body | Bytes | Field |
|---|---|---|
| 0 | 1 | hold kind (`01` key press, `05` momentary layer) |
| 1 | 1 | tap kind |
| 2 | 1 | flavor (Interrupt Flavor) |
| 3-4 | 2 | tapping term, u16 LE (`c8 00` = 200 ms) |
| 5-8 | 4 | hold param |
| 9-12 | 4 | `00 00 00 00` |
| 13-16 | 4 | tap param |
| 17-20 | 4 | `00 00 00 00` |

A type `03` record's param is the body (len `15`, a 24-byte record). A type `10` record's param is
`[term u16 LE][03]` followed by the same body (len `18`, a 27-byte record), so the term appears twice.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-41-->The two kind bytes are per-slot behavior kinds, not a constant `01 01`: `01` is a key
press and `05` a momentary layer (the hold param is then the layer index). The stock layer-tap (hold
for layer 2, tap Return or Backspace, positions 7 and 8) is a `03` record whose body is
`05 01 00 c8 00 | 02 00 00 00 | 00 00 00 00 | 28 00 07 00 | 00 00 00 00`, i.e. the whole record
`07 03 15 05 01 00 c8 00 02 00 00 00 00 00 00 00 28 00 07 00 00 00 00 00`. Only kinds `01` and `05`
have ever been seen, and the `10` form with a layer hold never. <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-21, checked on a board 2026-09-22

!!! danger "Never sweep the flavor byte"
    Writing a flavor of `04` or higher into any hold-tap record is accepted and stored, and then
    every key stops working until the board is unplugged (a power cycle). Rewriting the record does
    not help while it is powered. Measured on 3.41.0, 2026-09-03.

<!--KM-42-->The byte after the two kinds is the flavor, NayaFlow's Interrupt Flavor setting. `02`
is tap-preferred (measured). Valid values are 0-3; writing `04` or more stops every key until the
board is unplugged. The mapping of 0, 1 and 3 is open; see [Settings and timing](settings.md).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01, 2026-09-03. naya-create-kb leaves the
flavor encoding open[^kb-settings].

<!--KM-43-->The tapping term lives only inside hold-tap records, per record and per bank. Moving
NayaFlow's slider from 200 to 180 ms rewrote `c8 00` to `b4 00` in every hold-tap record on every
layer; untouched second-bank records kept an older 200 / flavor 1 while their primaries were
rewritten at 180 / 0. Both copies in a `10` record carry the same term. No double-tap window,
hold-start, wait or overlap parameter exists anywhere on the wire.
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1 capture on 3.41.0, 2026-09-17.
naya-create-kb reads the two `c8 00` as a hold threshold and a double-tap window; the second role is
not supported by any capture[^kb-keymap].

<!--KM-44-->The `03` byte inside every `10` param has been constant in every capture; its meaning
is open. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-45-->A key's four behaviors are two records `0x52` apart. The primary (position `p`) holds tap
and hold; the second-bank record (`p + 52`) holds double tap in its tap slot and tap and hold in its
hold slot. A captured NayaFlow write of one key, as record bytes:

```text
49 10 18 c8 00 03 01 01 00 c8 00 1d 00 07 00 00 00 00 00 05 00 07 00 00 00 00 00
9b 10 18 c8 00 03 01 01 00 c8 00 1c 00 07 00 00 00 00 00 1b 00 07 00 00 00 00 00
```

Pressing it gave `b`, `zzz`, `x` and `yyy` for tap, hold, double tap and tap and hold.
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0, 2026-09-03; the slot
assignment is also reported by naya-create-kb[^kb-keymap].

| Record | Hold slot | Tap slot |
|---|---|---|
| primary, position `p` | hold | tap |
| second bank, position `p + 52` | tap and hold | double tap |

<!--KM-46-->Double tap and tap and hold fire only if the PRIMARY record is a hold-tap. A plain `01`
primary with a double-tap second-bank record typed the tap twice ("aa") and never the double-tap
binding. The fix is a hold-tap primary with an empty hold half (four zero bytes).
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-21

<!--KM-47-->An empty slot half (four zero bytes) means "not bound" in a key-press slot but "layer 0"
(a real target) in a layer slot. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-48-->NayaFlow writes a user tap and hold as a `10` record; the stock layer-tap is `03`. A
writer that emits `03` where the board holds `10` (or the reverse) makes every later flash rewrite
that key. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--KM-49-->naya-create-kb describes the record shapes by behavior count: two behaviors are a single
`03` record with no second-bank record; three are a `10` primary plus a 10-byte second-bank record
(its "mini shadow", `74 10 07 c8 00 01 05 00 07 00`); four are a `10` primary plus a full 27-byte
second-bank record[^kb-keymap]. Our USB capture of a four-behavior key shows full 27-byte records in
both banks <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03. For three behaviors, the
naya-create-kb maintainer's device reads of 2026-09-17 hold the short form at the second-bank
position: `74 10 07 c8 00 01 05 00 07 00` (term 200, then `01`, then a key press) behind a
`22 10 18 ...` primary, and the record stays when the key drops back to a plain press
<span class="tag reported">REPORTED</span> (raw data checked[^kb-raw]). The same shape is what
NayaCore prints for a key in its own logs (`wire: 351007c800012a000700`)
<span class="tag static">STATIC</span>[^nc]. Which writer produced the stored record, NayaFlow or the
maintainer's tool, the dump does not say. The same page says NayaFlow's editor enforces the order
tap, then hold, then double tap, then tap and hold; the renderer confirms it: hold depends on tap,
double tap on tap and hold, and tap and hold on all three <span class="tag static">STATIC</span>[^nf];
also reported by naya-create-kb.

<!--KM-50-->The hold-tap keys of layer 0 as read from the owner's board on 2026-09-01 (term 194,
flavor 0): `20` hold LCtrl / tap A (`03`); `21` hold LShift / tap S (`03`); `25` hold Backspace /
tap Delete (`03`); `35` hold LCtrl / tap Backspace (`10`); `3f` hold LCtrl / tap LGui (`03`); `43`
hold LAlt / tap Return (`03`); `87` is the second bank of `35`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01

<!--KM-51-->NayaFlow's verify read-back renders every record at term 200 and flavor 1 (its
defaults), so a board whose records carry another term shows "differences" that have no effect on
typing. <span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0, 2026-09-17

## Module bays in layer data

<!--KM-60-->At positions `4a`-`51` the type byte is a module-config SLOT number and the length is 0:
`N` means "use config slot N", `78` means "inherit from the BASE layer (layer 0)", and `00` means
disabled. naya-create-kb calls `78` an empty filler[^kb-keymap]. Details are on
[Modules](modules.md). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03

| Position | Bay | Position | Bay |
|---|---|---|---|
| `4a` | Touch left | `4e` | Tune left |
| `4b` | Touch right | `4f` | Tune right |
| `4c` | Track left | `50` | Float left |
| `4d` | Track right | `51` | Float right |

<!--KM-61-->naya-create-kb describes a "tail index triplet" that changes from `4b 00 00` to
`4b 02 00` once any `10` record exists, and reads it as a layout-version or dirty flag[^kb-keymap].
It is the Touch-right bay record: `4b 02 00` means "the right Touch uses module-config slot 2". It
changed when NayaFlow flashed a module assignment, not because of a `10` record, and setting `4b` to
`02` by hand repoints that bay at whatever slot 2 holds. <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-03. The maintainer's own factory dump shows layer 0 bays `4a 00`, `4b 00`, `4c 01`,
`4d 01` (Tune and Float `00`) and every bay `78` on layers 1 and 2
<span class="tag reported">REPORTED</span> (raw data checked[^kb-raw]).

<!--KM-62-->A bay decoded through the behavior table invents bindings: slot 1 reads as a key press
and slot 5 as a layer hold with no target. Decoders must treat `4a`-`51` separately, and a
full-layer writer must carry the board's bay bytes through, or every module becomes unassigned.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09 (a real corruption in one tool, since fixed)

## Reading a layer

!!! note "Read-only"
    `30/1003` reads change nothing. Layer 0, first chunk:
    `aa 00 50 00 30 04 10 03 00 00 13 04`; every further chunk:
    `aa 00 50 00 30 04 10 03 01 00 12 04`. The chunk loop is on [Transport](transport.md).

<!--KM-63-->How long a read is depends on the firmware and on what is stored. 3.35.4 never returns
the second bank: the read stops at `51` <span class="tag measured">MEASURED</span> 3.35.4,
2026-09-21/22. On 3.41.0 the owner's board returned the whole bank, padded with `07 00` (156
records, highest `9b`), even for layers that had no second-bank record at all
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. A third-party 3.41.0 capture of
2026-09-15 returned 82 records per layer for layers that apparently never had a second bank written,
and the same layers read 156 after NayaFlow flashed them <span class="tag reported">REPORTED</span>
(raw data checked[^kb-raw]). So the length most likely follows what is stored, not only the firmware
<span class="tag inferred">INFERRED</span>. A reader that stops at `51` drops every double tap and
tap and hold; treat an absent position as NONE when comparing.

<!--KM-64-->A freshly created layer that was never written already reads 156 records (148 unbound),
has its own 136-entry LED map, and has all eight bays at `00`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-03

## Writing

!!! warning "Writes are live and persistent"
    Every `30/1004` write takes effect at once and survives a reboot; there is no commit and no
    undo. Read and save the whole layer (both banks and the bays) before editing, and send REMAP
    writes to the left half only.

<!--KM-65-->NayaCore writes changes as sparse diffs: only changed records, several per frame. Layer
1, two keys: params `00 01 24 01 04 04 00 07 00 34 01 04 1e 00 07 00`, ack `00 01`. A NEW layer is
written in full: 82 records `00`-`51`, unassigned keys `0e 00`, bays `78 00`; writes stop at `51`
while reads pad to 156. <span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0,
2026-09-01. naya-create-kb describes a per-key write[^kb-keymap].

One key, as a whole frame (layer 0, position `20`, key B), with its ack:

```text
aa 00 50 00 30 0b 10 04 00 00 20 01 04 05 00 07 00 33 04
aa 50 00 00 30 04 10 04 00 00 14 04
```

This frame is computed, not captured; its shape is the one NayaFlow sends.

<!--KM-66-->Length-changing writes apply: a 7-byte `01` record replaced by a 27-byte `10` record plus
its second-bank record, and back again, both read back correctly with a plain `30/1004`. An earlier
"same-length rule" was a client bug. <span class="tag measured">MEASURED</span> 3.41.0, from
2026-09-03; also reported by naya-create-kb, which retracted the same rule[^kb-keymap].

<!--KM-67-->When a key loses its double tap and tap and hold, its second-bank record must be
written too, or the stale record keeps acting and NayaFlow's verify fails on every flash. The proven
clear is `[pp+52] 07 00` (NONE): orphaned second-bank records cleared this way let NayaFlow's next
flash verify. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-09. naya-create-kb clears
with `[pp+52] 00 00` <span class="tag reported">REPORTED</span>[^kb-keymap]; that is the bay
"disabled" idiom, and on a key position type `00` is the Bluetooth record, so a zero-length `00`
there is untested.

<!--KM-68-->The layer byte is mandatory in `30/1004` params: `00 <layer>` followed by the records.
Our own captures always carry it. naya-create-kb reports that without it the device answers status
`19` with the key number and applies nothing (3.41.0, 2026-09-22, unchanged after `ee/10ce`)
<span class="tag reported">REPORTED</span>[^kb-keymap]. The status itself is measured: reads of layer
indices that do not exist (`81`, `e4`, `e5`) answered `19 <index>`
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. So a write without its layer byte
reads the first position as a layer index. If a write acks but changes nothing, check the params
prefix first (the maintainer's advice).

<!--KM-69-->`30/1004` writes take effect immediately and persist; there is no commit step.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09; also reported by
naya-create-kb[^kb-keymap].

<!--KM-70-->Layer sizes vary with the bindings. The stock NayaFlow profile reads 764 / 636 / 660
bytes for layers 0 / 1 / 2, both on the owner's board and in the naya-create-kb maintainer's factory
dump <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01. The maintainer's later board
read 789 / 636 / 660, and a third-party capture shows a 772-byte layer 0
<span class="tag reported">REPORTED</span> (raw data checked[^kb-raw]; [^kb-keymap]). Whatever the
size, the record lengths must close exactly.

!!! warning "Never bind TOGGLE to layer 0"
    A `0d` record that toggles to the base layer strands the keyboard on the current layer until a
    power cycle.

<!--KM-71-->A `0d` toggle record with target 0 (toggle to base) does not deactivate the layer you
stand on; the keyboard stays stranded until a power cycle. NayaFlow removes the base layer from its
Toggle target list. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09 +
<span class="tag static">STATIC</span>[^nf]

<!--KM-72-->naya-create-kb's writer recipe for a `10` key ("emit the primary and the second-bank
record and set `4b` to `02`, exactly like stock") is right about the two records and wrong about
`4b`, which repoints the right Touch's bay (see above)[^kb-keymap].
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09; the two-record part is also reported by
naya-create-kb (live test of 2026-09-18).

<!--KM-83-->NayaCore's serializer checks the record length for key_press, to_layer, toggle_layer,
mo, sticky_layer, bluetooth, rgb_ug, outputs, naya_integrations and mouse, and none for sticky_key,
grave_escape and macro; a mod_tap needs at least 21 bytes and is rejected when a half is missing.
<span class="tag static">STATIC</span>[^nc]

## The stock default profile

<!--KM-80-->NayaFlow 1.25.1's default Windows template ("Naya Default Windows") has three layers:
Typing (base), Keypad + Arrow Keys, and System. <span class="tag static">STATIC</span>[^nf] +
<span class="tag measured">MEASURED</span> (positions, 3.41.0, 2026-09-10)

| Layer | Contents |
|---|---|
| 0, Typing | Esc, Grave, the number row; positions 7 and 8 tap Return / Backspace and hold System (`03` layer-tap); thumbs Space, Backspace, Return; two keys hold layer 1 (67, 68); two keys hold System (62, 73) |
| 1, Keypad + Arrow Keys | keypad and arrow keys; the parentheses at `1c` / `1d` are the only shifted keys |
| 2, System | C_POWER, BT_DEVICE_1-4 and BT_CLEAR, LED effect and color keys, media keys, BT_OUT and USB_DEVICE, MODULE_FORCE_CHARGING at 62, PrintScreen; a full set of connection keys on EACH half (left 2-6, 47, 48; right 15, 29, 45, 61, 73, 71, 72) |

The other templates are Naya Default MacOS, Naya Japanese Windows and Naya Japanese MacOS, each also
as a "(07-18-2026)" variant.

<!--KM-82-->Position numbering (decimal) follows the vendor's key labels row by row: 0 LA1 ... 7 LH1,
8 RH1 ... 15 RA1; 16-22 LA2-LG2, 23-29 RG2-RA2; 30-36, 37 LH2, 38 RH2, 39-45; 46-52, 53 LH3, 54 RH3,
55-61; 62 LA5, 63 LB5, 64 LC5, 65 LD5, 66 LE5, 67 LH4, 68 RH4, 69 RE5, 70 RD5, 71 RC5, 72 RB5, 73 RA5.
So the MODULE_FORCE_CHARGING key at 62 is LA5, and naya-create-kb's MO keys at 67 / 68 are the LH4 /
RH4 thumbs[^kb-keymap]. Full geometry is on [Layout and positions](../hardware/layout.md).
<span class="tag static">STATIC</span> (vendor labels[^man-c]) + <span class="tag measured">MEASURED</span>
(stock positions, 3.41.0, 2026-09-10)

## History

<!--KM-84-->Remapping arrived late. The Batch 0 tester firmware (shipped 2025-01) had a fixed QWERTY
layout and no remapping, and the first Flow build could only flash firmware[^ks-19]. "Naya Flow
Version 1" brought key remapping[^ks-21]. The release notes date remapping to NayaFlow 1.3.8 (press
only, no combinations on one key); Double Tap and Tap and Hold arrived in NayaFlow 1.25.0 with
NayaCore 6.11.0; keyboard 3.28.7 fixed hold-tap keys sticking when two activated together[^nh-cl].
<span class="tag doc">DOC</span>

<!--KM-85-->The keyboard firmware is a customized ZMK fork. The Kickstarter campaign (2023) says
remapping is done "between our custom ZMK firmware and Naya Flow"[^ks-camp], update 9 (2023-12-07)
says the firmware is "based on a customized ZMK base" with features ZMK lacks[^ks-9], and the FAQ
said building and flashing one's own ZMK layout was "not available for now"[^ks-faq]. The wire
records follow ZMK's behaviors[^zmk]: the u32 key encoding, `&out` (type `08`), `&rgb_ug` (type `09`)
and the hold-tap flavors. The fork's source has not been published; see [ZMK](../firmware/zmk.md).
<span class="tag doc">DOC</span> + <span class="tag static">STATIC</span>

## Writer checklist

<!--KM-81-->Each item below caused a real corruption or a silent failure in one open-source tool
(OpenFlow[^openflow]) before it was fixed. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

| Trap | Rule |
|---|---|
| `08` read as a layer switch | `08` is `&out`: 1 USB, 2 wireless |
| zero-based Bluetooth devices | `(3, n)` is one-based |
| bays decoded as bindings | carry `4a`-`51` through untouched |
| a reader that stops at `51` | keep the second bank; treat absent positions as NONE |
| `03` versus `10` | write the form the board already holds |
| four zero bytes | "unbound" in a key-press slot, layer 0 in a layer slot |
| a stale layer reference that defaults to 0 | it flashes "switch to base" |
| continuation acks | accept status `01` on non-final frames |
| another program on the port mid-write | hold the port for every frame of a write |
| an unfamiliar status | it is not "empty"; see the status table on [Transport](transport.md) |

A read-then-write round trip can corrupt a board silently when the decoder is wrong (the `08`,
bay and second-bank traps above): re-encode what you read and compare it with the raw bytes before
writing anything back.

## Open questions

- <span class="tag open">OPEN</span> Flavor values 0, 1 and 3, and the constant `03` inside every
  `10` record ([details](../open-questions.md#oq-p09)).
- <span class="tag open">OPEN</span> Whether a per-key or per-bank tapping term behaves differently
  from the global one ([details](../open-questions.md#oq-p10)).
- <span class="tag open">OPEN</span> Why some 3.41.0 layers read 82 records and others 156
  ([details](../open-questions.md#oq-p11)).
- <span class="tag open">OPEN</span> Which writer produces the 10-byte second-bank record, and how
  the firmware acts on it ([details](../open-questions.md#oq-p12)).
- <span class="tag open">OPEN</span> What a zero-length `00` record on a key position does, and what
  an empty key press does ([details](../open-questions.md#oq-p13)).
- <span class="tag open">OPEN</span> Hold-tap slot kinds other than `01` and `05`; a `10` record
  with a layer hold ([details](../open-questions.md#oq-p14)).
- <span class="tag open">OPEN</span> The value of `MAX_LAYERS` ([details](../open-questions.md#oq-p15)).

## Sources

[^kb-keymap]: naya-create-kb, [protocol/keymap](https://nemezzizz.github.io/naya-create-kb/protocol/keymap/) (commit 7668067).
[^kb-settings]: naya-create-kb, [protocol/settings](https://nemezzizz.github.io/naya-create-kb/protocol/settings/) (commit 7668067).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): the behavior table, key table, Naya system action names, serializer checks and log formats.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings, and its default templates (static reading).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs and device dumps, including a factory-default layer dump of 2026-09-15 and two probe dumps of 2026-09-17); raw data decoded by us, never copied.
[^hid]: USB-IF, [HID Usage Tables](https://usb.org/document-library/hid-usage-tables-15) (Consumer page: `b5` Scan Next Track, `b6` Scan Previous Track, `cd` Play/Pause, `e2` Mute).
[^zmk]: ZMK documentation, [behaviors](https://zmk.dev/docs/keymaps/behaviors).
[^man-c]: Naya Create User Manual v1.1.x (key labels), see [Manuals](../product/manuals.md).
[^nh-cl]: create-legacy-firmware, vendor release notes, [changelogs/](https://github.com/create-collective/create-legacy-firmware/tree/79eeefb/changelogs) (v1.3.8, v1.14.5, v1.25.0).
[^ks-camp]: Kickstarter campaign page, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023), read 2026-09-23.
[^ks-faq]: Kickstarter campaign FAQ, [naya-create/naya-create/faqs](https://www.kickstarter.com/projects/naya-create/naya-create/faqs), read 2026-09-23.
[^ks-9]: Kickstarter update 9, [2023-12-07](https://www.kickstarter.com/projects/naya-create/naya-create/posts/3982337).
[^ks-19]: Kickstarter update 19, [2025-02-11](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4312089).
[^ks-21]: Kickstarter update 21, [2025-06-16](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4409531).
[^openflow]: [OpenFlow](https://github.com/create-collective/openflow/releases).

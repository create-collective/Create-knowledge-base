# Layout and positions

This page ties the physical keys (body, wing, dock) to the manual's keycap coordinates, to the position
numbers the firmware uses (`0x00`-`0x51`), and to the LED map indices (0-135), with what is known and
unknown about the light bars and module LEDs. The one thing to know: positions `0x00`-`0x49` are the 74
keys, `0x4A`-`0x51` are the eight module bays (not keys), and for keys the LED index equals the position.

!!! note "At a glance"
    - 74 keys, 37 per half: 24 on the body, 10 on the wing, 3 thumb keys on the dock.
    - Each keycap carries a coordinate: side `L`/`R`, column `A`-`H`, row `1`-`5`.
    - Key positions `0x00`-`0x49` run row by row, left A to H, then right H to A.
    - The LED map has 136 entries: keys 0-73, light bars 74-87, module-bay blocks 88-111 (left) and 112-135 (right).
    - Which light bar is 74-80, and how many bay indices a Tune or Track follows, are open.

## Key groups and coordinates

<!-- layout facts 1-4 -->
The keyboard has 74 keys, 37 per half: 24 on the body, 10 on the wing (the two outer columns) and 3
thumb keys on the dock around the module bay <span class="tag doc">DOC</span>[^fcc-crl][^um106]. Every keycap is labeled with a
coordinate: side `L`/`R`, column `A`-`H`, row `1`-`5`. Per half, columns A-E have rows 1-5, columns F-G
rows 1-4 and column H rows 1-4: 37 keys <span class="tag doc">DOC</span>[^um106] (the key map in the manual's text layer lists all 74).
Columns A and B are the wing (10 keys); columns C-G plus `H1` (the tall inner key) are the body (24);
`H2`-`H4` are the three dock thumb keys <span class="tag inferred">INFERRED</span> (the manual's map matched with the key counts in the photos).
NayaFlow 1.25.1 uses the same 74 labels as the manual <span class="tag static">STATIC</span>[^nc].

## Position numbers

<!-- layout facts 5-13 -->
Position numbers for the keys are `0x00`-`0x49` (0-73), covering both halves in one layer; the left half
stores and serves the whole table <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, layer reads and writes, 2026-09). The mapping below comes from NayaFlow's label map, and the
database position equals the firmware position <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc]:

- Row 1: 0 `LA1`, 1 `LB1`, 2 `LC1`, 3 `LD1`, 4 `LE1`, 5 `LF1`, 6 `LG1`, 7 `LH1`, 8 `RH1`, 9 `RG1`,
  10 `RF1`, 11 `RE1`, 12 `RD1`, 13 `RC1`, 14 `RB1`, 15 `RA1` (left A to H, then right H to A).
- Row 2: 16 `LA2` to 22 `LG2`, then 23 `RG2` to 29 `RA2` (no column H in row 2: `H1` is the tall key).
- Row 3: 30 `LA3` to 36 `LG3`, 37 `LH2`, 38 `RH2`, 39 `RG3` to 45 `RA3`.
- Row 4: 46 `LA4` to 52 `LG4`, 53 `LH3`, 54 `RH3`, 55 `RG4` to 61 `RA4`.
- Row 5: 62 `LA5`, 63 `LB5`, 64 `LC5`, 65 `LD5`, 66 `LE5`, 67 `LH4`, 68 `RH4`, 69 `RE5`, 70 `RD5`,
  71 `RC5`, 72 `RB5`, 73 `RA5`.

Key roles: 64 finger keys; 6 thumb keys (`LH2`-`LH4`, `RH2`-`RH4` at positions 37, 53, 67 and 38, 54,
68); 2 tall inner keys (`LH1` = 7, `RH1` = 8); 2 wide space keys (`LE5` = 66, `RE5` = 69) <span class="tag static">STATIC</span>[^nc].

Positions `0x4A`-`0x51` in every layer are the module bays, not keys; each holds a module-config slot
number (or inherit, or empty) <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board, 3.41.0, capture 2026-09-03)[^nc]:

| Position | Bay | Dock address of that module | LED block of that half |
|---|---|---|---|
| `0x4A` | Touch left | `0x10` | 88-111 |
| `0x4B` | Touch right | `0x11` | 112-135 |
| `0x4C` | Track left | `0x20` | 88-111 |
| `0x4D` | Track right | `0x21` | 112-135 |
| `0x4E` | Tune left | `0x40` | 88-111 |
| `0x4F` | Tune right | `0x41` | 112-135 |
| `0x50` | Float left (never shipped) | `0x80` (inferred) | 88-111 |
| `0x51` | Float right (never shipped) | `0x81` (inferred) | 112-135 |

The primary table is therefore `0x00`-`0x51` (82 positions). Double-tap and tap-then-hold behaviors live
in a second bank at key position + `0x52` (`0x52`-`0x9B`, keys only) <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-03 and 2026-09-21). Detail on
[Keymap](../protocol/keymap.md). A 2024 vendor answer described the module configuration as 9 sublayers
per layer, 1 for the keyboard and 4 for each dock (one per module type: Touch, Track, Tune, Float), which
matches the 8 bay positions <span class="tag doc">DOC</span> <span class="tag inferred">INFERRED</span>[^ks-11].

!!! note "For tool authors"
    Positions `0x4A`-`0x51` are bays, not keys: decoding them as key bindings invents bindings. See
    [Keymap](../protocol/keymap.md).

### The full position table

<!-- table built from layout facts 3, 6-11 -->
Positions are firmware positions (read and written on 3.41.0); coordinates come from NayaFlow's label
map and the manual; the section column follows the mapping above <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>. For keys the LED index
equals the position (next section).

| Position | Hex | Key | Side | Section | Role |
|---|---|---|---|---|---|
| 0 | `0x00` | `LA1` | left | wing | finger key |
| 1 | `0x01` | `LB1` | left | wing | finger key |
| 2 | `0x02` | `LC1` | left | body | finger key |
| 3 | `0x03` | `LD1` | left | body | finger key |
| 4 | `0x04` | `LE1` | left | body | finger key |
| 5 | `0x05` | `LF1` | left | body | finger key |
| 6 | `0x06` | `LG1` | left | body | finger key |
| 7 | `0x07` | `LH1` | left | body | tall inner key |
| 8 | `0x08` | `RH1` | right | body | tall inner key |
| 9 | `0x09` | `RG1` | right | body | finger key |
| 10 | `0x0A` | `RF1` | right | body | finger key |
| 11 | `0x0B` | `RE1` | right | body | finger key |
| 12 | `0x0C` | `RD1` | right | body | finger key |
| 13 | `0x0D` | `RC1` | right | body | finger key |
| 14 | `0x0E` | `RB1` | right | wing | finger key |
| 15 | `0x0F` | `RA1` | right | wing | finger key |
| 16 | `0x10` | `LA2` | left | wing | finger key |
| 17 | `0x11` | `LB2` | left | wing | finger key |
| 18 | `0x12` | `LC2` | left | body | finger key |
| 19 | `0x13` | `LD2` | left | body | finger key |
| 20 | `0x14` | `LE2` | left | body | finger key |
| 21 | `0x15` | `LF2` | left | body | finger key |
| 22 | `0x16` | `LG2` | left | body | finger key |
| 23 | `0x17` | `RG2` | right | body | finger key |
| 24 | `0x18` | `RF2` | right | body | finger key |
| 25 | `0x19` | `RE2` | right | body | finger key |
| 26 | `0x1A` | `RD2` | right | body | finger key |
| 27 | `0x1B` | `RC2` | right | body | finger key |
| 28 | `0x1C` | `RB2` | right | wing | finger key |
| 29 | `0x1D` | `RA2` | right | wing | finger key |
| 30 | `0x1E` | `LA3` | left | wing | finger key |
| 31 | `0x1F` | `LB3` | left | wing | finger key |
| 32 | `0x20` | `LC3` | left | body | finger key |
| 33 | `0x21` | `LD3` | left | body | finger key |
| 34 | `0x22` | `LE3` | left | body | finger key |
| 35 | `0x23` | `LF3` | left | body | finger key |
| 36 | `0x24` | `LG3` | left | body | finger key |
| 37 | `0x25` | `LH2` | left | dock | thumb key |
| 38 | `0x26` | `RH2` | right | dock | thumb key |
| 39 | `0x27` | `RG3` | right | body | finger key |
| 40 | `0x28` | `RF3` | right | body | finger key |
| 41 | `0x29` | `RE3` | right | body | finger key |
| 42 | `0x2A` | `RD3` | right | body | finger key |
| 43 | `0x2B` | `RC3` | right | body | finger key |
| 44 | `0x2C` | `RB3` | right | wing | finger key |
| 45 | `0x2D` | `RA3` | right | wing | finger key |
| 46 | `0x2E` | `LA4` | left | wing | finger key |
| 47 | `0x2F` | `LB4` | left | wing | finger key |
| 48 | `0x30` | `LC4` | left | body | finger key |
| 49 | `0x31` | `LD4` | left | body | finger key |
| 50 | `0x32` | `LE4` | left | body | finger key |
| 51 | `0x33` | `LF4` | left | body | finger key |
| 52 | `0x34` | `LG4` | left | body | finger key |
| 53 | `0x35` | `LH3` | left | dock | thumb key |
| 54 | `0x36` | `RH3` | right | dock | thumb key |
| 55 | `0x37` | `RG4` | right | body | finger key |
| 56 | `0x38` | `RF4` | right | body | finger key |
| 57 | `0x39` | `RE4` | right | body | finger key |
| 58 | `0x3A` | `RD4` | right | body | finger key |
| 59 | `0x3B` | `RC4` | right | body | finger key |
| 60 | `0x3C` | `RB4` | right | wing | finger key |
| 61 | `0x3D` | `RA4` | right | wing | finger key |
| 62 | `0x3E` | `LA5` | left | wing | finger key |
| 63 | `0x3F` | `LB5` | left | wing | finger key |
| 64 | `0x40` | `LC5` | left | body | finger key |
| 65 | `0x41` | `LD5` | left | body | finger key |
| 66 | `0x42` | `LE5` | left | body | wide space key |
| 67 | `0x43` | `LH4` | left | dock | thumb key |
| 68 | `0x44` | `RH4` | right | dock | thumb key |
| 69 | `0x45` | `RE5` | right | body | wide space key |
| 70 | `0x46` | `RD5` | right | body | finger key |
| 71 | `0x47` | `RC5` | right | body | finger key |
| 72 | `0x48` | `RB5` | right | wing | finger key |
| 73 | `0x49` | `RA5` | right | wing | finger key |

## Default layer keys

<!-- layout facts 14-15, 29 -->
In the v1.0.6 base layer `LA5` and `RA5` (positions 62 and 73) hold Layer 2 and `LH4` and `RH4` (67 and
68) hold Layer 1; v1.1.0 keeps these four and adds a Layer 2 hold on the tall inner keys (`LH1` Enter and
`RH1` Backspace, each with "Hold: Layer 2") <span class="tag doc">DOC</span>[^um106][^man-c]. NayaFlow 1.25.1's stock profile binds 62
and 73 to the System layer and 67 and 68 to Layer 1 as "polite" holds <span class="tag static">STATIC</span>[^nc].

The thumb and inner defaults changed between manuals: v1.0.6 has `LH1` Backspace, `LH2` Space, `LH3`
Enter (the right side mirrored, with Enter on `RH1` and Backspace on `RH3`); v1.1.0 (Windows) has `LH1`
Enter with a Layer 2 hold, `LH2` Space, `LH3` Backspace, `RH1` Backspace with a Layer 2 hold, `RH2` Space
and `RH3` Enter <span class="tag doc">DOC</span>[^um106][^man-c]. The v1.0.6 default keymap duplicates Tab, Caps Lock and Shift on both
wing columns (A and B) of the left half, and Shift on both on the right <span class="tag doc">DOC</span>[^um106]. See
[Manuals](../product/manuals.md#the-default-keymap).

## The LED map

<!-- layout facts 16-25, 32 -->
The LED map has 136 entries per layer, the same on 3.28.7 and 3.41.0: 0-73 the keys, 74-80 and 81-87 the
two light bars (7 each), 88-111 the left module-bay block (24), 112-135 the right module-bay block (24)
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, band painting 2026-09-08; a second board, 3.28.7, highest index 135,
2026-09-19). For keys, the LED index equals the key's position
number: a single-key LED write to index `0x49` recolored that key, and NayaFlow's one-key writes use the
position as the index <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01 captures and 2026-09-03 write test). The
count fits the hardware: per half 24 + 10 + 3 key LEDs plus a 7-LED light bar = 44, two halves = 88 =
indices 0-87 <span class="tag inferred">INFERRED</span>[^fcc-crl]. Details on [LEDs](../protocol/led.md).

| Indices | What | Evidence |
|---|---|---|
| 0-73 | the keys, index = position | <span class="tag measured">MEASURED</span> |
| 74-80 and 81-87 | the two light bars on the outer edges; which bar is 74-80 is open | <span class="tag measured">MEASURED</span> <span class="tag open">OPEN</span> |
| 88-111 | left module-bay block | <span class="tag measured">MEASURED</span> |
| 112-135 | right module-bay block | <span class="tag measured">MEASURED</span> |

- **Light bars.** They sit on the outer edge of each half (on the wing board). NayaFlow's color view
  draws 74-80 on the left half's outer edge and 81-87 on the right's; an earlier reading of ours put
  74-80 on the right; which physical bar answers 74-80 is not settled <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> <span class="tag open">OPEN</span>[^nc]
  ([details](../open-questions.md#oq-h08)).
- **Bay blocks belong to the bay.** Swapping a Tune and a Track between halves kept each side's color
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-08).
- **Touch.** A Touch lights through the first index of its block only (88 left, 112 right) <span class="tag measured">MEASURED</span>
  (owner's board, 3.41.0, 2026-09-10).
- **Tune and Track.** For a Tune the number of indices it follows is unsettled (88-96 lit in a band test;
  88 alone lit it in a single-index test; on module 2.1.2 only 88-93 took color); the Tune board carries
  24 LEDs. For a Track (one LED on the board) no single-index test exists; an early 112-126 reading was a
  band artifact <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span> (owner's board, 3.41.0, 2026-09-08 and 2026-09-10; a second board, 3.28.7,
  2026-09-19) ([details](../open-questions.md#oq-h08)).
- **NayaFlow's model.** NayaFlow keeps 97 rows per layer (positions 0-96), of which 90 are placed in its
  drawing: 74 keys, 14 light-bar LEDs (74-87) and 2 module slots (88 left, 89 right). It paints the whole
  left bay block from its module color and the whole right block likewise; rows 90-96 carry colors in the
  stock profile but are never sent to the board <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span>[^nc] (owner's board, 3.41.0, 2026-09-09). Which
  NayaFlow row (88 or 89) feeds each bay's color is not distinguished (both carried the same color in
  every profile checked) <span class="tag inferred">INFERRED</span> ([details](../open-questions.md#oq-p19)).
- **New layers.** A freshly created layer is not empty: the firmware initializes its key records, its own
  136-entry LED map and the eight bay positions <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-03). See
  [Layers](../protocol/layers.md).
- **Campaign zones.** The 2023 campaign described two side-glow zones per half for battery, charging or
  connection status, and listed LED zones of 68 (body), 6 (dock edge) and 10 (wing indicators) under a
  "90 LEDs" headline; the shipped map has one 7-LED bar per half and 74 key LEDs <span class="tag doc">DOC</span>[^ks-camp].

## The key matrix

<!-- layout fact 26 -->
The key matrix on the mainboard has row pads `SR1`-`SR5` and column pads `SC1`-`SC6`; the dock board adds
its own `SR*_2` and `SC8_2`; keyscan events carry `[row][col][state]`. How matrix row and column map to
position numbers is not recovered <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^fcc-crl][^nx] ([details](../open-questions.md#oq-h34)). See
[The keyboard half](half.md#per-key-lighting-and-the-key-matrix).

## Key geometry as NayaFlow draws it

<!-- layout facts 27-28, 30, 33 -->
NayaFlow's renderer (exported 2026-09-14) draws adjacent columns 48 px apart (49.6 px between A and B), a
plain key 44 x 44 px at 16 px/rem, thumb keys 44 x 58, the tall inner keys 45 x 100, the space keys
112 x 53; it has 34 distinct keycap outlines, and the key board is 992 x 240 px <span class="tag static">STATIC</span>[^nc]. This is a
drawing, not a measurement: the physical key pitch and the real positions of the keys on the plates are
not measured <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-h34)).

Naya's CAD (shown in a marketing screenshot) named keycap parts per section (`Cap_Body_…`, wing and dock
sets), with the coordinate letters in reversed order (for example `C4L` for `LC4`) <span class="tag doc">DOC</span>[^wb-naya]. The 2023
campaign gave a typing height of 11.2 mm for the main keys and 9 mm for the dock keys; the dock keys
became about 3 mm taller when they moved to PG1232 switches (2024-09) <span class="tag doc">DOC</span>[^ks-camp][^ks-15].

## Open questions

- <span class="tag open">OPEN</span> Which light bar is indices 74-80: paint 74 alone and look ([details](../open-questions.md#oq-h08)).
- <span class="tag open">OPEN</span> How many bay indices a Tune (on module 2.3.3) and a Track follow ([details](../open-questions.md#oq-h08)).
- <span class="tag open">OPEN</span> Which NayaFlow row feeds each bay color ([details](../open-questions.md#oq-p19)).
- <span class="tag open">OPEN</span> Matrix row/column to position mapping; physical key pitch and plate geometry ([details](../open-questions.md#oq-h34)).
- <span class="tag open">OPEN</span> The physical LED chain order (LED designators on the boards) versus the map indices ([details](../open-questions.md#oq-h08)).
- <span class="tag open">OPEN</span> Whether the corner keycaps' printed legends match their stock actions (a look at a retail unit).

## Sources

[^fcc-crl]: FCC IDs 2BQ4V0825CRL and 2BQ4V0825CRR: internal photos of the mainboard, wing and dock boards ([FCC EAS search](https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm), grantee 2BQ4V; mirror [fccid.io/2BQ4V0825CRL](https://fccid.io/2BQ4V0825CRL)).
[^um106]: Naya Create User Manual Version 1.0.6, FCC ID 2BQ4V0825CRR user manual exhibits, part 3 (key map and default layers) ([fccid.io](https://fccid.io/2BQ4V0825CRR)).
[^man-c]: Naya Create User Manual Version 1.1.0 (vendor PDF, 2025-11-10), p6, p18; see [Manuals](../product/manuals.md).
[^nc]: NayaFlow 1.25.1: renderer label map and key geometry, stock profile database and drawing model (static reading).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (constants for keyscan events).
[^ks-camp]: Kickstarter campaign page with its Specs Sheet, [naya-create/naya-create](https://www.kickstarter.com/projects/naya-create/naya-create) (2023).
[^ks-11]: Kickstarter update 11, [2024-02-15](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4029736).
[^ks-15]: Kickstarter update 15, [2024-09-03](https://www.kickstarter.com/projects/naya-create/naya-create/posts/4095301).
[^wb-naya]: The vendor's former website (an Onshape screenshot), archived by the Wayback Machine ([naya.tech captures](https://web.archive.org/web/2025*/naya.tech/*)); cited only, not reproduced.

# Settings and timing

This page lists every user-visible setting and where it lives on the keyboard: the three activity
timeouts (`fe/100a` / `fe/100b`), the tapping term and interrupt flavor (stored inside every hold-tap
record, not as a device setting), the three persistent LED settings (`ed/1012`-`1014`), host OS,
release mode and keyscan. It gives NayaFlow's names, defaults and ranges, and what the keyboard
validates or refuses. The one thing to know first: there is no global "profile header" on the wire,
and a NayaFlow flash always re-sends the timeouts but never sends the LED settings.

!!! note "At a glance"
    - Timeouts: `fe/100a` params `00` + three u32 LE milliseconds; anything under 30 s is refused
      with status `ea`.
    - Tapping term and flavor are bytes inside each hold-tap record; moving NayaFlow's slider
      rewrites every hold-tap record on every layer.
    - Flavor `02` = tap-preferred (measured); `04` or more stops every key until the board is unplugged.
    - `ed/1012` scan mode, `ed/1013` max brightness and `ed/1014` action override are real,
      persistent device settings with no read command.

Byte strings follow the site's [byte convention](transport.md#byte-convention): params and replies
start with the flag or status byte.

## Where each setting ends up

| NayaFlow control | NayaFlow default | On the keyboard | Read back with |
|---|---|---|---|
| Idle Timeout (0-6000 s) | 90 s | `fe/100a` field 1 (`idle_time_ms`) | `fe/100b` |
| Sleep Timeout (0-6000 s) | 300 s | `fe/100a` field 2 (`sleep_time_ms`) | `fe/100b` |
| (no control) | 30 s | `fe/100a` field 3 (`sleep_battery_time_ms`) | `fe/100b` |
| Tapping Term (10-1000 ms) | 200 ms | term u16 inside every hold-tap record | `30/1003` |
| Interrupt Flavor (4 choices) | Balanced | flavor byte inside every hold-tap record | `30/1003` |
| LED scan mode | on | `ed/1012` | none |
| LED max brightness (1-100) | 100 | `ed/1013` | none |
| LED action override | until keyboard restart | `ed/1014` | none |
| Hold layer LED activation delay (0-3000 ms) | 0 | unknown | unknown |
| Pointer speed, scroll speed, acceleration; Tune detents | per module | one-byte fields in each module config | `30/100b` |

## Activity timeouts

<!--ST-01-->`fe/100a` SET ACTIVITY TIMEOUTS and `fe/100b` GET ACTIVITY TIMEOUTS (NayaCore's names):
the params of `100a` are `00` followed by three u32 little-endian millisecond values; the ack is `00`
with no data; the reply to `100b` (params `00`) is `00` followed by the same 12 bytes. NayaCore names
the fields `idle_time_ms`, `sleep_time_ms` and `sleep_battery_time_ms`.
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-01 + <span class="tag static">STATIC</span>[^nc].
naya-create-kb calls the fields idle, sleep and deep and reads the leading `00` as a status
byte[^kb-settings][^kb-commands]; it is the request's flag byte.

!!! note "Read-only"
    `aa 00 50 00 fe 03 10 0b 00 1b 04` reads the three timeouts and changes nothing.

<!--ST-01b-->NayaCore's verify block for device settings lists `tapping_term_ms`,
`tap_hold_flavour`, `idle_time_ms`, `sleep_time_ms`, `sleep_battery_time_ms`, `scanmode_pwm` and
`led_layer_override` <span class="tag static">STATIC</span>[^nc]. NayaFlow describes sleep as a deep
sleep "disabling lighting, bluetooth and memory"[^nf], and the manual gives sleep after 1.5 minutes
idle and deep sleep (Bluetooth disconnected) after 10 minutes, both configurable[^man-c].
<span class="tag doc">DOC</span> naya-create-kb quotes the same manual defaults[^kb-manual].

<!--ST-02-->NayaFlow's defaults are params `00 90 5f 01 00 e0 93 04 00 30 75 00 00`: idle 90 000,
sleep 300 000, third field 30 000 ms. Other captured values are 88 000 / 304 000 / 30 000 and
69 000 / 264 000 / 30 000. NayaFlow never changed the third field in any capture.
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0, 2026-09. naya-create-kb's user
sample 6 000 000 / 6 000 000 / 30 000 is params `00 80 8d 5b 00 80 8d 5b 00 30 75 00 00`
<span class="tag reported">REPORTED</span> (raw data checked: its maintainer's captures carry
exactly these bytes[^kb-raw]; [^kb-settings]).

The default write and its ack, as whole frames:

```text
aa 00 50 00 fe 0f 10 0a 00 90 5f 01 00 e0 93 04 00 30 75 00 00 e6 04
aa 50 00 00 fe 03 10 0a 00 1a 04
```

To build the params, convert seconds to milliseconds and write each value as four bytes, least
significant first: 90 s = 90 000 ms = `0x00015f90` = `90 5f 01 00`.

<!--ST-03-->In the naya-create-kb maintainer's earliest captures (2026-09-15, 3.41.0, before NayaFlow
wrote any timeouts) the board held 90 000 / 600 000 / 15 000 ms: `fe/100b` replied
`00 90 5f 01 00 c0 27 09 00 98 3a 00 00` <span class="tag reported">REPORTED</span> (raw data
checked[^kb-raw]). That matches the manual's "sleep after 1.5 min idle, deep sleep after 10 min"
<span class="tag doc">DOC</span>[^man-c], and the third value is below the 30 s floor that writes
enforce, so something other than a normal write set it
<span class="tag inferred">INFERRED</span>.

!!! warning "Timeout writes change a persistent setting"
    `fe/100a` is stored at once and survives reboots. Values under 30 s are refused with status
    `ea` and nothing is stored; a tool that treats any non-zero status as a transport error will
    misreport this as a failed link.

<!--ST-04-->Validation on 3.41.0: any value under 30 s is refused with status `ea` and nothing is
stored; 30 s and up are stored; 0 means "off" for idle and sleep but is not accepted for the third
field; idle may exceed sleep. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11

| Field | Refused with `ea` | Stored |
|---|---|---|
| idle | 10, 15, 20, 29 s | 0 (off), 30, 45, 60, 400 s |
| sleep | 20 s | 0 (off); 300 s (NayaFlow's default) |
| third | 5, 15 s (0 is not accepted either) | 45 s |

<!--ST-05-->NayaCore sends `fe/100a` on every NayaFlow flash, changed or not (identical bytes across
sessions), and then reads `fe/100b` as its verify ("Settings mismatch: X Write=%1 Read=%2"). There is
no commit step in this protocol. `fe/100b` is stable across reboots because the timeouts are
persistent, and it changes whenever the timeouts change (captured at 88 s / 304 s after a UI change).
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0, 2026-09-01, 2026-09-17 +
<span class="tag static">STATIC</span>[^nc]. naya-create-kb agrees that `fe/100a` is not a commit but
calls `fe/100b` a token that never changes[^kb-settings]; it changes with the settings. Re-sending
valid `fe/100a` bytes is not a hazard in our records (see the never-send list on
[Command map](commands.md)).

<!--ST-06-->naya-create-kb reports `fe/100b` unchanged across reboots and across a factory
restore[^kb-littlefs]. <span class="tag reported">REPORTED</span> (the reboot part matches our
measurement; the factory part needs a donor-board test).

<!--ST-07-->NayaFlow's Behavior Settings map onto the first two fields: Idle Timeout and Sleep
Timeout sliders, 0-6000 s, stored in seconds in NayaFlow's database; NayaFlow 1.25.1 has no control
for the third field <span class="tag static">STATIC</span>[^nf]. The timeout settings first shipped,
unannounced, in NayaFlow beta 1.22.0 (keyboard 3.39.4; its note says 3.39.3), and keyboard 3.40.4
fixed three activity-timeout bugs: the right half waking the left when entering idle, a Track not
keeping the keyboard awake, and LEDs stuck half on and half off[^beta].
<span class="tag doc">DOC</span> naya-create-kb describes the same two sliders[^kb-settings].

<!--ST-08-->The first field's idle timer turns the key LEDs off. It did not run with the cable in
and USB output selected, and it did run on battery (LEDs off at 90 s, one tap restores them). Whether
the power source or the output mode gates it is open. What the second and third fields do beyond
being stored has not been measured. <span class="tag measured">MEASURED</span> 3.41.0, 2026-09-11

## Typing timing: tapping term and interrupt flavor

<!--ST-09-->There is no device-wide tapping term and no "profile header" on the wire. The term is
the u16 inside every hold-tap record (once in a `03` record, twice in a `10` record), stored per
record and per bank. NayaFlow writes its single global term and flavor into every hold-tap record,
so moving its slider rewrites every hold-tap record on every layer; nothing else carries the term
(`fe/100a` does not). <span class="tag measured">MEASURED</span> NayaFlow 1.25.1 capture on 3.41.0,
2026-09-17. naya-create-kb derives a tapping term of 200 ms, flavor 0 and "transparent-as-default 1"
from a stock profile header[^kb-settings]; the record bytes are on [Keymap records](keymap.md).

<!--ST-10-->NayaFlow's Tapping Term slider defaults to 200 ms with a range of 10-1000 ms. Its only
timing controls are Tapping Term, Idle Timeout, Sleep Timeout and the Interrupt Flavor dropdown;
there is no double-tap window, hold-start, wait-for-release or overlap setting in its UI, in its
settings schema, or on the wire. <span class="tag static">STATIC</span>[^nf] +
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09. naya-create-kb agrees, and has
retracted an earlier claim of timing presets[^kb-settings].

!!! danger "Flavor `04` or higher stops every key"
    A hold-tap record with flavor `04` or more is accepted and stored, and then no key works until
    the board is unplugged (a power cycle). Never sweep this byte. Measured on 3.41.0, 2026-09-03.

<!--ST-11-->Interrupt Flavor: NayaFlow offers four policies (Balanced, Hold-Preferred,
Tap-Preferred, Tap-Unless-Interrupted; schema default "balanced")
<span class="tag static">STATIC</span>[^nf]. On the wire it is byte 2 of the hold-tap body in every
record, both banks (byte 5 of a `03` record, byte 8 of a `10` record): switching only the dropdown to
Tap-Preferred changed every layer-0 hold-tap record from `00` to `02`, and NayaFlow's reset flash
wrote `00`. Valid values are 0-3; `04` stops every key until the board is unplugged; `02` is
tap-preferred (measured); the mapping of 0, 1 and 3 is open.
<span class="tag measured">MEASURED</span> NayaFlow 1.25.1 on 3.41.0, 2026-09-01, 2026-09-03.
naya-create-kb's settings page lists the same four choices and leaves the wire encoding open[^kb-settings].

<!--ST-12-->Two orders fit the unmeasured flavor values. ZMK's order (0 hold-preferred, 1 balanced,
2 tap-preferred, 3 tap-unless-interrupted)[^zmk-ht] is supported by NayaFlow re-rendering unread
records as flavor 1, its default "balanced". The UI's order (0 balanced, ...) is supported by the
default and reset flashes writing `00`. NayaCore's own name list reads "balanced, tap-preferred,
tap-unless-interrupted, hold-preferred"; indexed 0-3 it contradicts the one measured point, so it is
not the wire enum. <span class="tag measured">MEASURED</span> (one point) +
<span class="tag static">STATIC</span>[^nc] + <span class="tag inferred">INFERRED</span>

| Byte | Measured | ZMK order (candidate) | NayaFlow UI order (candidate) | NayaCore name list (ruled out) |
|---|---|---|---|---|
| `00` | written by default and reset flashes | hold-preferred | balanced | balanced |
| `01` | shown for unread records by NayaFlow's verify | balanced | hold-preferred | tap-preferred |
| `02` | tap-preferred | tap-preferred | tap-preferred | tap-unless-interrupted |
| `03` | not seen | tap-unless-interrupted | tap-unless-interrupted | hold-preferred |
| `04`+ | stops every key | (invalid) | (invalid) | (invalid) |

<!--ST-13-->"transparent-as-default" is a NayaCore setting for unset host slots: it decides whether
NayaCore writes an unassigned key as `0e 00` or `07 00`. On the device, an unbound position reads
`07 00`. <span class="tag static">STATIC</span>[^nc] + <span class="tag measured">MEASURED</span>
3.41.0, 2026-09

<!--ST-14-->Vendor fixes that touch these settings: NayaCore 6.1.4 fixed "Interrupt Flavor and
Tapping Term settings were not applied to NayaCreate in some cases" (beta 1.17.0, 2026-02-07), and
NayaCore 6.10.2 handles a hold-tap flavor mismatch on write[^beta]. <span class="tag doc">DOC</span>

## LED settings

<!--ST-15-->The three LED settings are real, persistent device settings that act when written:
`ed/1012` scan mode (a bool; NayaFlow "LED scan mode", default on; toggling shows only as flicker on
camera), `ed/1013` max brightness (1-100; NayaFlow default 100; 30 visibly dims), and `ed/1014`
action override (0 = an LED action pressed on a key lasts until restart, NayaFlow's default "until
keyboard restart"; 1 = until the next layer change). <span class="tag measured">MEASURED</span>
3.41.0, 2026-09-13, 2026-09-16. NayaCore 6.11.0 added protocol support for them (NayaFlow 1.25.0
release notes)[^nh-cl] <span class="tag doc">DOC</span>. A NayaFlow keymap flash sends none of them;
when NayaCore does send them has never been captured. naya-create-kb calls the three dead host-side
controls because a settings flash sent no LED frame[^kb-settings]; the missing frame is right, the
"dead" is not. Commands, params and the dark-board hazard of `ed/1013` 0 are on [LEDs](led.md).

!!! warning "`ed/1013` with 0, or with short or empty params, darkens the keys persistently"
    Short `ed` params are zero-filled, so an empty or one-byte `ed/1013` is a write of 0. The
    ceiling is stored, so the key array would then stay dark across reboots. See [LEDs](led.md).

<!--ST-16-->NayaCore's messages "No tap hold flavour found in the settings table. Resorting to
default." and the similar max-brightness message are about NayaFlow's settings table in its host
database (`user-data.db`), which NayaCore reads by fixed correlation ids: in NayaCore 6.11.0's
strings each such message sits beside a `SELECT value FROM settings WHERE correlation_id = '...'`
query. They say nothing about where the keyboard stores a value. The device side is known only by
behavior: the values persist across reboots, and whether a firmware flash changes the LED ceiling
was not recorded. <span class="tag static">STATIC</span>[^nc] +
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09. naya-create-kb uses these messages as
proof of device storage keys[^kb-littlefs]. See [App data](../software/app-data.md).

<!--ST-17-->NayaFlow's setting correlation ids are vendor constants in its database: interrupt
flavor `24de8555-1a56-4e02-a1c3-3641603a5ac9`, tapping term `8fe34f61-df0c-48c9-b0f7-ee9bfbaa2a05`,
idle `ded8e734-b10b-48c9-9ab1-536904e2c3de`, sleep `f198f968-2c42-4df6-8fdd-97de148cad1a`, LED action
override `385426f7-e454-4174-babe-4ca4a670cbe2`, LED max brightness
`321fe22c-74e0-48cf-a954-326bf4391fd7`, LED scan mode `66770f52-e917-4f17-b775-6308b1e4281a`. The
third timeout's id was not recovered. NayaFlow 1.25.1 also has "Hold layer LED activation delay"
(0-3000 ms, default 0, id `83dab362-...`), whose transport to the keyboard is unknown.
<span class="tag static">STATIC</span>[^nf]

## Host OS, release mode and keyscan

<!--ST-18-->`fe/1005` SET HOST OS takes one data byte below 2: 0 = Windows, 1 = macOS (params
`00 00` / `00 01`). It has never been sent by us and is not in the captured connect sequence.
NayaFlow ships separate Windows and macOS templates (see [Keymap records](keymap.md)).
<span class="tag static">STATIC</span>[^nc] naya-create-kb lists the name[^kb-commands].

<!--ST-19-->`fe/1007` SET RELEASE MODE takes one data byte: `00` and `01` were accepted, `ff` was
refused (`ea`), and nothing changed on USB. NayaCore re-asserts release mode only through the text
command `keyboard_mode_release_toggle` in its port-broker fallback; the captured connect sequence has
no `fe/1007`. <span class="tag measured">MEASURED</span> left half, 3.41.0, 2026-09-02 +
<span class="tag static">STATIC</span>[^nc] naya-create-kb lists the name[^kb-commands].

<!--ST-20-->`fe/1008` TOGGLE KEYSCAN MODE and `fe/1009` KEYSCAN EVENT are described on
[Command map](commands.md). <span class="tag static">STATIC</span>[^nx] +
<span class="tag measured">MEASURED</span> 3.41.0, 2026-09-20

## What a NayaFlow reset flash writes

<!--ST-21-->NayaFlow's full-reset flash writes: tapping term 200, flavor `00`, timeouts 90 s / 300 s
/ 30 s, module pointer speed / scroll speed / acceleration 10 / 10 / 50, the Tune's one-finger tap
cleared, and key `22`'s color back to hue 171. <span class="tag measured">MEASURED</span> NayaFlow
1.25.1 on 3.41.0, 2026-09-01

## Module settings

<!--ST-22-->naya-create-kb lists "9 host gesture slots" (0 MOUSE_HORIZONTAL ... 8
STATIC_ZOOM)[^kb-settings]. They are the categories of the two-word (`0f`) record, its first u32,
used in module fields and on keys, not slots. See [Module fields](module-fields.md).
<span class="tag static">STATIC</span>[^nc] + <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

<!--ST-23-->Module settings (pointer speed, scroll speed, acceleration and its switch, the Tune's
detent spacing, strength and on/off) are one-byte fields inside each module config; see
[Module fields](module-fields.md). <span class="tag measured">MEASURED</span> 3.41.0, 2026-09

## History

| Version | Change | Evidence |
|---|---|---|
| NayaCore 6.1.4 (beta 1.17.0, 2026-02-07) | Interrupt Flavor and Tapping Term sometimes not applied, fixed | <span class="tag doc">DOC</span>[^beta] |
| NayaCore 6.10.2 | hold-tap flavor mismatch on write handled | <span class="tag doc">DOC</span>[^beta] |
| NayaFlow beta 1.22.0 (keyboard 3.39.4) | Idle and Sleep timeouts first shipped (unannounced) | <span class="tag doc">DOC</span>[^beta] |
| keyboard 3.40.4 (beta 1.24.0) | three activity-timeout bugs fixed | <span class="tag doc">DOC</span>[^beta] |
| NayaCore 6.11.0 (NayaFlow 1.25.0) | protocol support for the three LED settings | <span class="tag doc">DOC</span>[^nh-cl] |

## Open questions

- <span class="tag open">OPEN</span> Flavor values 0, 1 and 3; one captured NayaFlow flash per
  dropdown value settles it ([details](../open-questions.md#oq-p09)).
- <span class="tag open">OPEN</span> What the second and third timeout fields do on the device;
  whether 0 is accepted for the third; whether USB power or USB output gates the idle timer; how
  "Hold layer LED activation delay" reaches the keyboard; who wrote the 90 / 600 / 15 s state seen
  before NayaFlow's first flash ([details](../open-questions.md#oq-p20)).
- <span class="tag open">OPEN</span> When NayaCore sends `ed/1012`, `ed/1013` and `ed/1014`
  ([details](../open-questions.md#oq-p21)).

## Sources

[^kb-settings]: naya-create-kb, [protocol/settings](https://nemezzizz.github.io/naya-create-kb/protocol/settings/) (commit 7668067).
[^kb-commands]: naya-create-kb, [protocol/commands](https://nemezzizz.github.io/naya-create-kb/protocol/commands/) (commit 7668067).
[^kb-manual]: naya-create-kb, [device/manual](https://nemezzizz.github.io/naya-create-kb/device/manual/) (commit 7668067).
[^kb-littlefs]: naya-create-kb, [storage/littlefs](https://nemezzizz.github.io/naya-create-kb/storage/littlefs/) (commit 7668067).
[^kb-raw]: The naya-create-kb maintainer's published captures and dumps (USB CDC capture logs, including a settings flash); raw data decoded by us, never copied.
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (static reading): settings field names, verify messages, settings-table queries, validation messages.
[^nf]: NayaFlow 1.25.1 renderer and flow-bg-server strings, and its settings schema (static reading).
[^nx]: nayactl, [github.com/Qonfused/nayactl](https://github.com/Qonfused/nayactl) (`constants.py`, `cli/keyscan.py`).
[^man-c]: Naya Create User Manual v1.1.x, p. 5 ("Turning Create ON/OFF": sleep and deep sleep), see [Manuals](../product/manuals.md).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases) (1.17.0, 1.22.0, 1.23.0, 1.24.0).
[^nh-cl]: nayaHistory, vendor release notes, [changelogs/](https://github.com/traviswye/nayaHistory/tree/79eeefb/changelogs) (v1.25.0).
[^zmk-ht]: ZMK documentation, [hold-tap behavior, flavors](https://zmk.dev/docs/keymaps/behaviors/hold-tap).

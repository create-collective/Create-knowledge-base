# App data

Where NayaFlow keeps its database, logs and backups, what the tables mean, which values reach the
keyboard, and how to back up and restore safely. The one thing to know: `user-data.db` is the
source of every NayaFlow flash, and several of its values reach the board (colors, the layer list,
animations), so a NayaFlow backup is a real backup of your configuration; the keyboard's own stores
are a second copy that NayaFlow never reads back.

!!! warning "Before you edit or restore"
    Quit all three NayaFlow programs before touching `user-data.db` by hand. Restoring a backup
    overwrites the database and restarts the app. Take a backup (NayaFlow's manual backup, or a device
    read with a tool) before any Danger Zone action or a flash from another tool.

!!! note "At a glance"
    - Windows: `%APPDATA%\NayaFlow\`; macOS: `~/Library/Application Support/NayaFlow/`.
    - flow-bg-server owns and migrates the SQLite database; NayaCore only reads it during a flash.
    - The stock database holds 201 `press` bindings over three layers and no macro.
    - Backups: a ring of ten automatic zips every 30 minutes (when data changed), plus manual backups.

## Where the data lives

| Platform | Location | Evidence |
|---|---|---|
| Windows | `%APPDATA%\NayaFlow\`: `user-data.db`, `logs\core\` (NayaCore), `logs\flow\` (bg-server), `logs\main.log` (Electron main), `components\` (component downloads), `backups\` | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (the owner's machine, 2026-09-23) |
| macOS | `~/Library/Application Support/NayaFlow/` | <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (the app is named `NayaFlow`, the main process hands Electron's `userData` path to the bg-server, and that path on macOS is `~/Library/Application Support/<name>`); also reported by naya-create-kb[^kb-appdata] |
| Linux | No NayaFlow data path to give. Only 0.0.1-0.1.1 shipped a Linux AppImage, and it carried no firmware service; the Linux NayaCore builds of 1.15.0-1.17.3 were not run by us | <span class="tag static">STATIC</span> (release assets[^nh-manifest]); <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-s09)) |
| NayaFlow-Beta | its own `NayaFlow-Beta` data folder; stable 1.17.3 fixed NayaCore logs being written there instead of into `NayaFlow` | <span class="tag doc">DOC</span>[^rel][^beta] |

## `user-data.db`

`user-data.db` is SQLite, created and migrated by flow-bg-server (goose migrations; queries generated
by sqlc). NayaCore only reads it, when an `update_keymap` event passes it `db_path` (see
[NayaFlow and NayaCore](nayaflow.md)) <span class="tag static">STATIC</span>[^bg][^nc].
naya-create-kb has NayaCore owning SQLite[^kb-nayaflow]; it does not.

- **21 tables**: color_palettes, color_swatches, dynamic_layer_groups, dynamic_layers,
  goose_db_version, key_bindings, keys, layers, loop_action_macro_steps, macros, module_bindings,
  module_config_bindings, module_configs, module_settings, mouse_action_macro_steps, profiles,
  settings, standard_action_macro_steps, templates, text_action_macro_steps,
  wait_for_release_macro_steps <span class="tag static">STATIC</span> (schema of a 1.25.1 database).
- **Nine goose migrations**: `20250609122327_initial`, `20250803231606_update_settings_column`,
  `20250821193635_add_module_setting_table`, `20250826171852_add_action_id_to_keybinding_and_module_binding`,
  `20250902212225_add_composite_primary_key_to_module_settings`,
  `20250902214523_change_settings_primary_key_to_correlation_id`,
  `20250903113837_add_module_config_binding_state_and_remove_is_transparent_and_is_disabled`,
  `20250929162102_add_context_to_keybinding`, `20260421070750_add_animation_to_layers`
  <span class="tag static">STATIC</span> (`goose_db_version` rows of the stock database).
- **The stock database** holds 201 `key_bindings` rows, all with behavior `press`, over the three
  layers of the "Naya Default Windows" profile, and no macro. Every Naya Default and Naya Japanese
  template (Windows and macOS) from 1.15.0 to 1.25.1 carries the same 201 `press` bindings, and three
  stock Windows databases hold the same <span class="tag static">STATIC</span>
  <span class="tag measured">MEASURED</span> (templates embedded in the installers; databases of
  2026-08-28, 2026-08-31 and 2026-09-08 opened read-only). naya-create-kb reports 190 rows and one
  BASIC macro in "the stock database"[^kb-appdata]; those figures describe its own, edited database.

| Table | Purpose | Reaches the keyboard? |
|---|---|---|
| `profiles` | profiles; `state = 'ON_BOARD'` marks the active one, the only one NayaCore flashes | through the flash |
| `layers` | layers per profile, with `animation_id` | the layer list (not the names) |
| `keys` | 97 rows per layer (`position_id` 0-96) with a `color_hex` | colors of 0-89 as the LED map |
| `key_bindings` | behaviors per key (`press`, `hold`, `double_tap`, `tap_hold`) | yes, as keymap records |
| `module_configs`, `module_bindings`, `module_config_bindings` | module profiles, their gesture bindings, and which config each layer uses where | yes, as module configs and bay records |
| `module_settings` | speeds, acceleration, Tune ticks | yes, as module config fields |
| `settings` | app settings by correlation id | some (timeouts, tapping term, flavor, LED settings) |
| `macros` and the five `*_macro_steps` tables | macros | no: the keyboard has no macro table |
| `color_palettes`, `color_swatches` | palettes | no |
| `dynamic_layer_groups`, `dynamic_layers` | a switched-off feature | no |
| `templates` | shipped templates | no |
| `goose_db_version` | migration bookkeeping | no |

## Profiles, layers, keys and positions

| Fact | Evidence |
|---|---|
| `profiles.state = 'ON_BOARD'` marks the active profile; NayaCore flashes only that one (`SELECT id, name FROM profiles WHERE state = 'ON_BOARD'`). | <span class="tag static">STATIC</span>[^nc] |
| `keys` holds 97 rows per layer (`position_id` 0-96) with a `color_hex`; `#xxxxxx` marks "no color set". | <span class="tag static">STATIC</span> (stock 1.25.1 database) |
| Positions 0-73 are the 74 keys (the only positions with bindings). 74-80 and 81-87 are the two 7-LED side bars; 88 and 89 carry the two module-bay colors, painted onto LED blocks 88-111 and 112-135 (which of 88/89 feeds which side is <span class="tag open">OPEN</span>: both held the same color in every capture). 90-96 carry colors in the stock profile but never reach the board. NayaCore's log says "Read 74 keys for layer with id:N". naya-create-kb calls 74-96 host-only spares; that holds for bindings, not for color. | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board, 3.41.0, 2026-09-08/09; the owner's NayaCore logs; key geometry as the 1.25.1 renderer draws it); positions on [Layout](../hardware/layout.md) |
| `keys.color_hex` is what NayaFlow flashes as the LED map: NayaCore turns each `#rrggbb` into hue and saturation ("LED at index: %1 Hue: %2 Sat: %3"); `#xxxxxx` becomes saturation 150 (the no-color value). A flash with known database colors read back matching on 17 of 18 color classes across three layers, including all 40 white keys. NayaFlow's hue is the integer 60-degree formula, truncated (`#0084ff` -> 208). naya-create-kb calls `color_hex` host-side UI state only; it is flashed. | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-08) |
| Layer names are host-only (the protocol has no names). The layer list itself (one 20-byte entry per layer: index, id, animation, `10`, 16-byte UUID) lives on the keyboard; NayaCore writes only changed entries, so its log line "No data to write for layer list" means no entry changed. | <span class="tag measured">MEASURED</span> (captures, 2026-09-01/03) <span class="tag static">STATIC</span>; see [Layers](../protocol/layers.md) |
| Layer names by template: the 1.25.x templates name the three layers "Typing", "Keypad + Arrow Keys" and "System"; the templates of 1.15.0 to 1.21.0 named the base layer "QWERTY" (the names naya-create-kb saw, from a database created before 1.25); the Create manual draws "Base Layer (QWERTY)", "Layer 1 (Function)" and "Layer 2 (System)". | <span class="tag static">STATIC</span> (embedded templates of 1.15.0, 1.15.1, 1.17.3, 1.19.1, 1.21.0 and 1.25.1) <span class="tag doc">DOC</span> (manual[^manual]); also reported by naya-create-kb[^kb-appdata] |
| `layers.animation_id` holds the layer's animation (added 2026-04-21); NayaCore defaults to SOLID when it is empty. | <span class="tag static">STATIC</span>[^nc] |

## Key bindings, module configs and module settings

- `key_bindings.behavior` is one of `press`, `hold`, `double_tap`, `tap_hold`; NayaCore's own words are
  `tap`, `hold`, `double_tap`, `tap_hold` (it has no `press` literal, so any other word counts as the
  tap slot). Other columns: `action_type`, `action_code`, `key_id`, `context` (added 2025-09-29)
  <span class="tag static">STATIC</span>; also reported by naya-create-kb[^kb-appdata].
- `module_config_bindings` ties a module config to a layer and a location: `touch`, `track`, `tune`
  or `float` crossed with `keyboard_left` / `keyboard_right` (8 locations); `state` is `transparent`,
  `disabled`, or NULL (use the bound config). Migration 20250903113837 replaced two booleans with
  `state` <span class="tag static">STATIC</span>[^nc]; naya-create-kb lists six locations[^kb-appdata].
- `module_bindings` rows: `behavior` (gesture id), `action_type`, `action_code`, `action_id`,
  `invert`, `threshold`, `direction` (default `+`), `mode` <span class="tag static">STATIC</span>.
- NayaCore refuses a module setting whose correlation id belongs to another module type ("Invalid
  correlation id for touch/track/tune config") <span class="tag static">STATIC</span>[^nc].

Module settings (1.25.1 defaults; ranges 1-100 unless stated) <span class="tag static">STATIC</span>[^bg]:

| Module | Settings |
|---|---|
| Touch | MS-2 scroll speed 50, MS-3 pointer speed 10, MS-4 pointer acceleration 50, MS-5 acceleration on |
| Track | MS-7 scroll 10, MS-8 acceleration 50, MS-9 pointer 10, MS-10 acceleration on |
| Tune | MS-12 scroll 10, MS-13 pointer 10, MS-14 acceleration 50, MS-15 acceleration on, MS-16 ticks per rotation 5-170 (72), MS-17 tick strength 0-100 (75), MS-18 ticks on |

MS-1, MS-6 and MS-11 are absent <span class="tag open">OPEN</span>
([details](../open-questions.md#oq-s03)). naya-create-kb gives MS-4 = 20; that is a user value, the
default is 50. On the keyboard these settings land in module config fields `0x00` pointer speed, `0x01`
scroll speed, `0x02` acceleration, `0x03` acceleration on (INFERRED for the Touch and Track); on the
Tune `0x05` = degrees per detent (360 / ticks, so 72 ticks = 5), `0x06` tick strength, `0x07` ticks on
<span class="tag measured">MEASURED</span> (owner's board, 3.41.0, module 2.3.3, 2026-09-11 and
2026-09-16). Details on [Module fields](../protocol/module-fields.md).

## App settings

Table `settings`, keyed by correlation id, with 1.25.1 defaults <span class="tag static">STATIC</span>[^bg]:

| Setting | Default and range |
|---|---|
| Language | en (en, jp) |
| Input source | qwerty (qwerty, jis) |
| Interrupt flavor | balanced (tap-preferred, hold-preferred, tap-unless-interrupted) |
| Tapping term | 200 ms (10-1000) |
| Auto check update | on |
| Hold layer LED activation delay | 0 ms (0-3000) |
| Idle timeout | 90 s (0-6000, 0 = off) |
| Sleep timeout | 300 s (0-6000, 0 = off) |
| Module battery in tray | off |
| Zoom level | 0 % (-500 to 500, step 25) |
| LED action override | `until_keyboard_restart` (or `until_layer_change`) |
| LED max brightness | 100 % (0-100) |
| LED scan mode | on |

- The idle and sleep sliders are in **seconds**, not milliseconds: a stored 6000 means 100 minutes and
  goes to the keyboard as 6 000 000 ms <span class="tag static">STATIC</span>[^bg]. naya-create-kb reads
  them as milliseconds[^kb-appdata].
- NayaCore reads these settings by correlation id and falls back to built-in defaults. The
  keyboard-side block it verifies has `tapping_term_ms`, `tap_hold_flavour`, `idle_time_ms`,
  `sleep_time_ms`, `sleep_battery_time_ms`, `scanmode_pwm`, `led_layer_override`;
  `sleep_battery_time_ms` has no NayaFlow setting <span class="tag static">STATIC</span>[^nc]. See
  [Settings and timing](../protocol/settings.md).

## Macros and other host-only tables

The macro tables (`macros`, `standard_`, `text_`, `mouse_`, `loop_`,
`wait_for_release_action_macro_steps`) are edited by the bg-server but never flashed; the keyboard has
no macro table (see [NayaFlow and NayaCore](nayaflow.md)) <span class="tag static">STATIC</span>
<span class="tag measured">MEASURED</span> (owner's board, 2026-09-07). The stock database holds no
macro. The stock palette "Rainbow" has 9 swatches `#ff0000`, `#ff6f00`, `#ffe500`, `#00ff00`,
`#00ffd9`, `#0000ff`, `#6f00ff`, `#00ff5e`, `#9000ff`. `dynamic_layer_groups` and `dynamic_layers`
exist but the feature is switched off in the renderer; `templates` holds the shipped templates
<span class="tag static">STATIC</span>.

## Logs

| Log | What it holds | Evidence |
|---|---|---|
| `logs/core/nayacore_<yyyy-MM-dd_HH-mm-ss>.log` (header "=== Naya Core Log File ===") and `debug_nayacore_<...>.log` | NayaCore: CDC traffic, ZMQ verdicts, profile dumps | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (file names on the owner's machine) |
| `logs/flow/NayaFlow-bg-<yyyy-mm-dd>.log` (daily) | flow-bg-server; every ZMQ message as "Sending ZMQ message to NayaCore: %+v" | <span class="tag static">STATIC</span>[^bg] <span class="tag measured">MEASURED</span>; also reported by naya-create-kb[^kb-appdata] |
| `logs/main.log` | the Electron main process | <span class="tag measured">MEASURED</span> |

Log rotation and a fix for logs over 100 MB came in 1.17.2 <span class="tag doc">DOC</span>[^rel].

- A NayaCore profile dump prints per key `tap: (ACTION)` and `wire: <hex>`
  <span class="tag static">STATIC</span>[^nc]; naya-create-kb decoded its record table from eight
  such dumps[^kb-appdata]. **A `wire:` line is NayaCore's re-encoding of the key as its own model has
  it, not the bytes on the board**: it printed `wire: 351007c800012a000700` for key `0x35` while the
  board held a plain `01` BACKSPACE there. Verification dumps show every hold-tap at term 200 / flavor
  1. A key with four behaviors goes on the wire as two full 27-byte type-`10` records (both banks).
  Record layouts learned from log lines need a USB capture or a `30/1003` read to confirm
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-09 and 2026-09-17; USB
  capture 2026-09-03).
- naya-create-kb's logs show a `repair_flash` that reported "success" after 1318 ms (mount only), and
  "FW Right/Left file uploaded successfully" after which its LED problem survived
  <span class="tag reported">REPORTED</span>[^kb-appdata]. Both fit what we know: Test and Format
  SPI-Flash formats only partitions whose self-test fails, and a firmware flash leaves stored maps and
  bond tables untouched <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span>
  (vendor text[^bg]; the owner's boards, 2026-09-20/22; create-legacy-firmware[^nh-hw]).

## Backups

- **Cadence**: automatic every 30 minutes when data changed (from 1.17.2); manual backups kept in a
  separate folder (1.25.0); 500-2000 KB each; the automatic set is a ring of 10 (`maxBackupCount`), and
  `/rpc/trigger-userdata-backup` pushes the oldest out <span class="tag doc">DOC</span>
  <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (release notes[^rel];
  the bg-server; the owner's machine, where `backups/1.25.1/` holds exactly ten
  `<yyyy-mm-dd_HH-mm-ss>.zip` files).
- **Format**: a backup zip holds `backup_meta.json` (`{"created_at": "...", "data": {"software_version":
  "1.25.1"}}`) and `user-data.db`, in a folder named after the app version (`backups/1.25.1/`).
  Restoring overwrites the database and restarts the app <span class="tag static">STATIC</span>
  <span class="tag doc">DOC</span> <span class="tag measured">MEASURED</span> (a 1.25.1 backup read
  2026-09-23; the restore overlay text[^bg]); also reported by naya-create-kb[^kb-appdata].
- A NayaFlow backup (zip or `user-data.db`) is a valid OpenFlow database: OpenFlow uses the same schema
  and imports it <span class="tag static">STATIC</span> ([OpenFlow](https://github.com/create-collective/openflow/releases)).
- App identity: appId `tech.naya.nayaflow`, author "NayaTech", "Copyright 2024 tech.naya"; the updater
  caches in `nayaflow-updater` <span class="tag static">STATIC</span> (0.0.1 `package.json`; 1.25.1
  `app-update.yml`).

### Third-party snapshots and restores

- naya-create-kb restores a device through a NayaFlow backup: it copies the live database as a skeleton
  and rewrites `key_bindings` only; its round trip gave 222 of 222 keys byte-equal
  <span class="tag reported">REPORTED</span>[^kb-appdata] (its published script does exactly this;
  code read 2026-09-23).
- Its own snapshot is one JSON (keymaps and LED maps of layers 0-2 plus telemetry: firmware versions,
  timeouts, module presence) restored per record with `30/1004` and `30/100e` and checked by read-back
  (`IDENTICAL` / `DIFFERS` per section) <span class="tag reported">REPORTED</span>[^kb-appdata] (code
  read 2026-09-23).
- A device-side snapshot should also keep the raw layer list (the `30/1001` reply): `30/10ca` wipes it,
  and writing it back first after a format is the proposed restore, untested after a format
  <span class="tag measured">MEASURED</span> (the list's write form, captured 2026-09-03/10)
  <span class="tag inferred">INFERRED</span>. See [Factory reset](../storage/factory-reset.md).
- OpenFlow keeps its own data apart: `%APPDATA%\OpenFlow` (Windows),
  `~/Library/Application Support/OpenFlow` (macOS), `$XDG_DATA_HOME/OpenFlow` (Linux), or
  `OPENFLOW_DATA_DIR`; next to `user-data.db` are `backups/`, `logs/backend.log`, `logs/sidecar.log`,
  `shell/`; uninstalling leaves the data <span class="tag static">STATIC</span> (OpenFlow README, link at
  release).

## Open questions

- <span class="tag open">OPEN</span> Which of positions 88 and 89 feeds which bay color (flash different colors at 88 and 89 and read the LED map).
- <span class="tag open">OPEN</span> NayaFlow's data path on Linux, and whether 1.19.1 or later shipped a Linux build ([details](../open-questions.md#oq-s09)).
- <span class="tag open">OPEN</span> Why MS-1, MS-6 and MS-11 are absent ([details](../open-questions.md#oq-s03)).
- <span class="tag open">OPEN</span> The effect of `sleep_battery_time_ms` (the third timeout field) on hardware.

## Sources

[^nc]: NayaFlow 1.25.1 for Windows, `core/NayaCore/NayaCore.exe` (NayaCore 6.11.0): strings (SQL queries, log formats, settings names).
[^bg]: NayaFlow 1.25.1, `flow/flow-bg-server.exe`: strings and embedded data (settings, module settings, templates, i18n, backup code).
[^rel]: Vendor release notes, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases), mirrored in create-legacy-firmware [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).
[^nh-manifest]: create-legacy-firmware, [`MANIFEST.json`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/MANIFEST.json) (the assets of every stable release).
[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^manual]: Naya Create manual v1.1.x, pp. 18-23 (see [Manuals](../product/manuals.md) for archived copies).
[^kb-appdata]: naya-create-kb, [software/app-data](https://nemezzizz.github.io/naya-create-kb/software/app-data/).
[^kb-nayaflow]: naya-create-kb, [software/nayaflow](https://nemezzizz.github.io/naya-create-kb/software/nayaflow/).

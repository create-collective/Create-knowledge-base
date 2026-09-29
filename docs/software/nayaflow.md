# NayaFlow and NayaCore

How the vendor's desktop app is built and how it talks to the keyboard: its three programs, the
HTTP and ZeroMQ bridge between them, the events that reach the device service, what a "Flash
Create" really sends, which features reach the keyboard, and the app's hazards. The one thing to
know: NayaFlow never reads your board back into its UI, so a NayaFlow flash overwrites whatever
another tool stored; and two of its buttons act on the keyboard without a dialog. All facts are for
NayaFlow 1.25.1 (NayaCore 6.11.0) unless a row says otherwise; our static work is on the Windows
build, checked against the macOS builds of the same version.

!!! danger "Two NayaFlow shortcuts and buttons act immediately"
    - **Ctrl/Cmd+D on the Hardware Manager page** starts a firmware update of both halves, with no
      dialog unless a warning is present.
    - The **Danger Zone** buttons (Test and Format SPI-Flash, Clear all keymap data, Clear BLE
      Devices) were seen to run without a confirmation (one observation, 2026-09-01). "Clear all
      keymap data" runs `30/10ca`, which wipes the keymaps: back up first (see [App data](app-data.md)).

!!! note "At a glance"
    - Three programs: the Electron app (renderer and main), the Go server `flow-bg-server`, and the
      C++/Qt service `NayaCore`, which does all device I/O.
    - The renderer talks HTTP and SSE to flow-bg-server on a port chosen at every launch; flow-bg-server
      talks to NayaCore over ZeroMQ publish/subscribe on runtime ports found through shared memory.
    - NayaCore accepts 16 named events; the renderer sends 9 of them.
    - A flash writes only what changed, to the left half only, then verifies by reading back.
    - No account, cloud or vendor server is needed; the only outbound calls are update checks, which
      fail against GitHub because of an unsubstituted token placeholder.

## The programs

NayaFlow 1.25.1 is four layers in three programs <span class="tag static">STATIC</span>[^main][^bg][^nc]:

| Layer | Program | Role |
|---|---|---|
| Renderer | NayaFlow (Electron, React) | the UI; talks HTTP and server-sent events to flow-bg-server |
| Main | NayaFlow (Electron main) | window, tray, auto-updater; starts flow-bg-server; no action model, no SQL and no ZMQ code |
| Background server | `flow-bg-server` (Go 1.25.5) | HTTP API and SSE, the SQLite user data, templates, backups, component updates, the ZMQ bridge to NayaCore |
| Device service | `NayaCore` (C++, Qt 6) | owns the USB serial ports (binary protocol and the MCUboot SMP upload); reads the user data itself |

The chain, in words: renderer -> (HTTP + SSE on a local port chosen at each launch) ->
flow-bg-server -> (ZeroMQ publish/subscribe, ports exchanged through Qt shared memory) -> NayaCore ->
(USB CDC, `dst 0x50`) -> left half -> (split link) -> right half. flow-bg-server creates and edits
`user-data.db`; NayaCore opens the same file for reading when a keymap flash hands it the path.

- **Electron main** holds the window, tray and auto-updater and starts flow-bg-server; a byte-level
  search of its bundle finds no action-catalog name, no SQL and no ZMQ code
  <span class="tag static">STATIC</span>[^main].
- **flow-bg-server**: Go 1.25.5 with gin, sqlc, goose, mattn/go-sqlite3 and pebbe/zmq4 (libzmq 4.3.5),
  about 25.7 MB. It serves the HTTP API and SSE, owns the SQLite user data (schema migrations and
  queries live in it), templates, backups, component updates, and the ZMQ bridge
  <span class="tag static">STATIC</span>[^bg]. naya-create-kb calls it a "Go helper, HTTP bridge"
  and says it runs with a fixed `-port 56486`; the port changes at every launch (below).
- **NayaCore 6.11.0**: C++ with Qt 6 (Core, SerialPort, Sql with the qsqlite driver), built with MSVC
  on Windows, libzmq 4.3.6; 8.5 MB on Windows, 12.6 MB (Intel) and 11.9 MB (arm64) on macOS. It owns
  the USB serial ports and reads `user-data.db` itself. It was compiled "Jul 17 2026 14:20:59"; its
  version string format is `v%1.%2.%3`; its command-line flags are `--version` and
  `enableFileLogging` <span class="tag static">STATIC</span>[^nc][^nc-mac].
- NayaCore reaches Bluetooth state only through keyboard commands over USB (the `be/10xx` family); no
  use of the host's own Bluetooth stack was found <span class="tag inferred">INFERRED</span> (no host
  Bluetooth API names in its strings). naya-create-kb says NayaCore owns "BLE" and SQLite; flow-bg-server
  owns the database, and NayaCore only reads it.
- NayaCore opens `user-data.db` with Qt's QSQLITE driver in a reader thread ("Spawned SQLReaderThread
  with dbPath: %1") when an `update_keymap` event hands it `db_path`, reads the profile whose `state`
  is `ON_BOARD`, and reads settings by correlation id with built-in defaults
  <span class="tag static">STATIC</span>[^nc].

## Where things live

| Platform | Layout | Evidence |
|---|---|---|
| Windows (1.25.1) | `resources/app.asar` (`dist/main`, `dist/renderer`); `flow/flow-bg-server.exe` + `libzmq-mt-4_3_5.dll`; `core/NayaCore/NayaCore.exe` + `Qt6Core.dll`, `Qt6SerialPort.dll`, `Qt6Sql.dll`, `libzmq-v143-mt-4_3_6.dll`, `sqldrivers/` (qsqlite, qsqlmimer, qsqlodbc, qsqlpsql) | <span class="tag static">STATIC</span> (installed tree of the public installer) |
| macOS | `NayaFlow.app` (the dmg installs it in `/Applications`); `Contents/flow/flow-bg-server`; `Contents/core/NayaCore.app/Contents/MacOS/NayaCore`; `Contents/Resources/app.asar` | <span class="tag static">STATIC</span> (1.25.1 release zips); also reported by naya-create-kb[^kb-nayaflow] |
| Where NayaCore sits, by release | Windows: inside the asar up to 1.17.3, `core/NayaCore/` from 1.19.1. macOS: under `Contents/core` since at least 1.11.11 (`naya_core_project.app`; `NayaCore.app` from 1.14.3); the macOS asars of 1.14.5 to 1.17.3 also carry a leftover copy of the Windows `NayaCore.exe` | <span class="tag static">STATIC</span> (release installers and zips); details on [History](history.md) |

**Build provenance.** The Windows NayaCore carries 60 source paths under `D:\a\NayaCore\NayaCore\...`
and the bg-server paths under `D:/a/NayaFlow/NayaFlow/apps/desktop/bg-server/...`: GitHub Actions
Windows runners, with NayaFlow a monorepo containing `apps/desktop/bg-server`
<span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span> (the CI reading). The
macOS builds carry `/Users/runner/work/NayaCore/NayaCore/...` (62 paths in the arm64 NayaCore) and
`/Users/runner/work/NayaFlow/NayaFlow/apps/desktop/bg-server`
<span class="tag static">STATIC</span>[^nc-mac]; also reported by naya-create-kb[^kb-nayaflow].

**NayaCore's source tree** (60 files) <span class="tag static">STATIC</span>[^nc]: `Naya_Data`
(Binding, Key, LED, Layer, ModuleConfig, Profile, Slot); `Naya_MainController`; `Naya_SQLReader`;
`Naya_SerialPort` with `MCUBootWorker` (base, CreateLeft, CreateLeft_Modules, CreateRight),
`NayaDevice`, `Naya_DeviceManager` (+ ClearAllData, ClearBLEDevices, Enqueue, FWUpdate,
ModuleFwUpdate, Operation, Pairing, TestSPIFlash), `Naya_SerialWorker`, `Naya_SerialWorkerBroker`,
`ProtocolCDCWorker` (Integration_Worker for keyscan events; Process_Worker groups BLE, Firmware, Flash,
LED, META, Module, Remap, SysPower, System; Utility Command, MessageQueue, Message, Process);
`Naya_Threads`; `Naya_ZMQHandler`; `main.cpp`.

## Electron main

| Fact | Evidence |
|---|---|
| At start-up the main process asks the OS for two free ports (it binds port 0): one for its own JSON-RPC server, one passed to flow-bg-server as `-port <n>`. The bg-server port therefore changes at every launch. naya-create-kb's fixed `56486` was one launch's value. | <span class="tag static">STATIC</span>[^main] |
| Observed on Windows: the bg-server listened on port 61957 on 2026-09-01 (IPv6 loopback). Find the current port through the listening socket of the flow-bg-server process (PowerShell `Get-NetTCPConnection -OwningProcess <pid>`, state Listen). | <span class="tag measured">MEASURED</span> (owner's machine, 2026-09-01) |
| The renderer learns the port from the preload (`window.EXPOSED.bgServerPort`, the second-to-last argv entry) and falls back to 3001 when it is absent; the update window also receives a `webSocketPort`. | <span class="tag static">STATIC</span>[^main][^rend] |
| Environment given to flow-bg-server: `ELECTRON_USER_DATA_PATH`, `ELECTRON_APP_NAME`, `ELECTRON_APP_VERSION`, `NAYA_CREATE_FW_VERSION` (3.41.0), `NAYA_MODULE_FW_VERSION` (2.3.3), `NAYA_CORE_EXE_DIR` (`resources/../core`), `GIN_MODE`, `ELECTRON_RESTARTED`, `ELECTRON_JSON_RPC_SERVER_PORT_MAIN`, `ELECTRON_IS_PACKAGED`, `PATH`, `TMPDIR`, and a GitHub token variable whose value is an unsubstituted build placeholder (not reproduced here). | <span class="tag static">STATIC</span>[^main] |
| Main's JSON-RPC server (`POST /json-rpc`) offers `quit`, `abort-quit`, `restart-main-process`, `open-in-browser`, `open-folder`, `save-file` (diagnostics zip, default name `nayaflow-diagnostics.zip`), `check-for-updates`, `enable-module-battery-indicator-tray`, `disable-module-battery-indicator-tray`, `change-zoom-level`. Main calls the bg-server's `get-setting-value-by-correlation-id` and, every 5 s for the tray battery display, `get-real-time-naya-device-info`. | <span class="tag static">STATIC</span>[^main] |

## flow-bg-server: routes, events and data

HTTP routes the 1.25.1 renderer calls <span class="tag static">STATIC</span>[^rend]:

| Kind | Routes |
|---|---|
| API | `/api/actions`, `/api/actions/${id}`, `/api/components/${type}`, `/api/diagnostics/report`, `/api/i18n/ui`, `/api/info/system`, `/api/list-userdata-backups`, `/api/templates`, `/api/ui/module-settings`, `/api/ui/settings`, `/api/ui/state`, `/api/userdata` |
| RPC | `/rpc/check-for-updates`, `/rpc/export-user-data`, `/rpc/import-userdata-beta`, `/rpc/logs`, `/rpc/open-log-folder`, `/rpc/open-url-in-browser`, `/rpc/open-userdata-backup-folder`, `/rpc/respond-to-quit-event`, `/rpc/restore-userdata-backup`, `/rpc/send-flash-keymap-request`, `/rpc/send-nayacore-zmq-message`, `/rpc/trigger-userdata-backup`, `/rpc/use-template` |

- Route strings in flow-bg-server 1.25.1: `/naya-core-zmq`, `/naya-core-device-info`,
  `/naya-core-naya-devices`, `/export-user-data`, `/import-user-data`, `/import-userdata-beta`,
  `/list-userdata-backups`, `/module-settings`, a `:symbol` route parameter (actions),
  `/open-log-folder`, `/factory-reset`, plus bg-server-only fragments
  `/components/start-naya-component-update`, `/diagnostics/serial-port-info`, `/rpc/debug`,
  `/rpc/server` <span class="tag static">STATIC</span>[^bg]; also listed by naya-create-kb[^kb-rpc].
- `/factory-reset` has no caller in the 1.25.1 renderer (0 hits for `factory-reset`,
  `factory_reset`, `factoryReset`); its string sits among the route strings. naya-create-kb found
  it answers 404 as a bare GET, POST or OPTIONS on a live server
  <span class="tag reported">REPORTED</span>[^kb-rpc]. How or whether it is registered is
  <span class="tag open">OPEN</span> ([details](../open-questions.md#oq-s01)).
- Server-sent events on `GET /sse`: the renderer listens for `sse:ui-state-change`,
  `sse:naya-devices-stream`, `sse:flash-keymap-state`, `sse:device-operation-options`,
  `sse:main-process-quit`; the bg-server also emits `sse:message-stream` and
  `sse:naya-component-update-progress`; its strings also contain `device_list`, `message-stream`,
  `flash-keymap-state`, `device-info-stream`, `naya-devices-stream`
  <span class="tag static">STATIC</span>[^rend][^bg].
- `GET /api/info/system` returns the versions bundled with the app (`createFWVersion` 3.41.0,
  `moduleFWVersion` 2.3.3, `naya_core_version` 6.11.0), not what a keyboard reports
  <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (owner's machine, 2026-09-01).
- **The action catalog** the UI offers lives in flow-bg-server (`data.ActionsJSON`): 652 records (698
  with 46 empty placeholders), 389 distinct action codes; front-end types key 314, shortcut_alias 211,
  LED 38, mouse 26, value 19, modifier 16, bluetooth 10, out 4, naya 2, trans 2, none 2, and 2 each of
  the four layer types; served by `GET /api/actions?t=<tab>&g=<group>&d=<context>`
  <span class="tag static">STATIC</span>[^bg].
- **Palette tabs**: Basic (Letters, Numbers, Modifiers, Control, Symbols), Extended (Empty, Mouse,
  Connection, Configuration Toggles, Lighting, System, Keypad, Navigation, International, Locks,
  Function Keys), Layers (Hold, Toggle, Force, Sticky Layer), Integrations (MacOS, Windows, VS Code
  Presets, VS Code Presets (Mac)), and a Modules tab for module editing. The JIS input source switches
  to Japanese labels: 219 `_JIS` action ids, 42 of them mapping to a different code
  <span class="tag static">STATIC</span>[^bg][^rend].
- **Templates**: Naya Default Windows, Naya Default MacOS, Naya Japanese Windows, Naya Japanese
  MacOS, each also as a "(07-18-2026)" variant; module templates Naya Touch Windows, Naya Touch MacOS,
  Naya Touch MacOS 2.0, Naya Track Left, Naya Track Right, Naya Track, Naya Tune Mac/Win, Naya Tune.
  The template library supports AES-GCM encrypted payloads (no key material examined)
  <span class="tag static">STATIC</span>[^bg].
- **Go packages** (`naya.tech/server/internal/...`): app, data (ActionsJSON, I18nFS,
  ModuleSettingUIsJSON, UiSettingsJSON), db (+gen, MigrationsFS), diagnostics, features (actions,
  diagnostics, external-component-manager, settings, template, ui, userdata), naya (ComponentRegistry,
  NayaComponentManager, NayaCoreProcessManager, NayaComponentUpdater: Idle, Initializing, Downloading,
  Completed, Failed), naya/nayacoreclient, naya/nayadevicemanager (BLEProfile, BLEStatus,
  FlashKeymapState, NayaCreateDevice, SplitLinkStatus, WarningCondition, WarningType,
  normalizeVersion), settings, state (UIState, ZoomLevel), tcp (Server, SSEConfig), templates
  <span class="tag static">STATIC</span>[^bg].
- The diagnostics report on Windows lists present USB devices with VID and PID through PowerShell
  `Get-PnpDevice -PresentOnly`; a one-click support report arrived in 1.21.0
  <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^bg][^rel].
- The bg-server has a field `oldBLELibDeprecatedCreateLeftFWVersion` (a version boundary for the old
  Bluetooth library); its value was not found <span class="tag static">STATIC</span>
  ([details](../open-questions.md#oq-s02)).

## The ZeroMQ link and the events NayaCore accepts

NayaCore's ZMQ link is publish/subscribe on runtime ports: it binds a publisher on
`tcp://localhost:0`, writes the chosen port to Qt shared memory `ZMQ_CORE_PUB_PORT_SHARED_MEM`,
reads the bg-server's publisher port from `ZMQ_FLOW_PUB_PORT_SHARED_MEM` and subscribes to
`tcp://localhost:<port>`. The Go side has `nayacoreclient.writePortToSharedMemory`,
`FreePortFinder` and `BoundPortFinder`. Topics: `command` (requests and their replies),
`stream:fw_update_status`, `stream:operation_status_normal`, `stream:operation_status_fwupdate`,
`stream:device_list` <span class="tag static">STATIC</span>[^nc][^nc-mac]. nayactl carries the same
shared-memory names and topics, found independently[^nx]. naya-create-kb describes a request/reply
socket on `127.0.0.1:56500`; that was one run's value and the wrong socket model.

- Messages are JSON. The renderer's only device-control path is
  `POST /rpc/send-nayacore-zmq-message` with the body `{"messages": [topic, event, ...frames]}`, topic
  always `command` <span class="tag static">STATIC</span>[^rend]; also reported by naya-create-kb[^kb-rpc].
- A `{"status": "message sent"}` answer from that route only means the bg-server forwarded the
  message (the literal is in the binary); the outcome is in NayaCore's log ("ZMQ Command response:
  Event=%1, ProcessID=%2, Status=..., Duration=...ms") <span class="tag static">STATIC</span>[^bg][^nc];
  also reported by naya-create-kb[^kb-rpc].
- The bridge logs every message it sends as "Sending ZMQ message to NayaCore: %+v"
  <span class="tag static">STATIC</span>[^bg].

NayaCore accepts exactly **16 events** (enum 1-16; 0 is `invalid_command_event`)
<span class="tag static">STATIC</span>[^nc-mac][^nc]:

| Event | Sent by (1.25.1) | Payload keys | What it starts |
|---|---|---|---|
| `quit` | not in the renderer (sender not identified) | none | NayaCore quits |
| `update_keymap` | bg-server, during a keymap flash | `db_path` | a SQL reader caches the "flow keymap" |
| `flash_keymap` | bg-server, during a keymap flash | none | the keymap flash (below) |
| `repair_flash` | renderer (Danger Zone) | `target_devices`, `target_partitions` | Test and Format SPI-Flash |
| `clear_data` | renderer (Danger Zone) | `targetDevices` | the ClearAllData operation, which sends `30/10ca` |
| `clear_ble_devices` | renderer (Danger Zone) | a target list | ClearBLEDevices |
| `start_device_manager` | none found | none | |
| `close_device_manager` | none found | none | |
| `force_touch_start`, `force_tune_start`, `force_track_start` | renderer (forced module update) | see the key list below | ModuleFwUpdate (forced) |
| `create_pairing_start` | renderer | `target_device_left`, `target_device_right` | Pairing |
| `update_module_fw` | renderer | see the key list below | ModuleFwUpdate |
| `update_create_fw` | renderer | two empty frames, or a firmware file path | FWUpdate |
| `update_fw_files` | none found | | |
| `set_handshake_frequency` | none found | `frequencyMs` | the periodic poll interval |

- Anything else logs "Unknown command event:"; naya-create-kb reports the reply as error 4
  <span class="tag reported">REPORTED</span>[^kb-rpc] (in the arm64 build the log entry itself
  carries error code 0; the reply status needs a running NayaFlow to check). naya-create-kb lists 15
  events; the 16th, `quit`, is missed by a `strings` pass because the compiler builds that 4-byte
  name from an immediate <span class="tag static">STATIC</span>[^nc-mac].
- `clear_all_data` is not an event: it is the process name the ClearAllData operation gives to the
  `30/10ca` it queues <span class="tag static">STATIC</span>[^nc-mac].
- **"Clear all keymap data" runs `30/10ca`.** The Danger Zone button sends `clear_data`; NayaCore's
  dispatcher maps `clear_data` (enum 5) to its `clearAllData` request, whose chain ends in
  `doClearAllDataOperations`, which queues category `0x30` subcommand `0x10ca`. Its step names are
  Clearing, ReadData, VerifyDataCleared, and it logs "Reconnected to device %1 after clear all data."
  <span class="tag static">STATIC</span>[^nc-mac][^nc]. naya-create-kb calls the ClearAllData chain
  dead code from the bridge's point of view[^kb-rpc]; it is not. The bytes the button sends are
  <span class="tag open">OPEN</span> until a USB capture ([details](../open-questions.md#oq-f16));
  NayaCore's own construction suggests params `00 00` (see [Disassembly](disassembly.md)).
- Payload keys NayaCore parses: `db_path`, `target_devices`, `target_partitions`, `target_device`,
  `firmware_file_path`, `target_device_left`, `target_device_right`, `targetIds`, `firmwareFilePath`,
  `frequencyMs`; the Go side uses a JSON tag `targetDevices`. Match the exact key per event
  <span class="tag static">STATIC</span>[^nc][^bg]. The renderer sends `clear_data` with the frames
  `["", "{\"targetDevices\":[]}"]` and `repair_flash` with `{"target_devices":[],"target_partitions":[]}`
  <span class="tag static">STATIC</span>[^rend]; naya-create-kb saw the same messages in the bridge log,
  `update_create_fw` with empty frames and `create_pairing_start` with the halves' USB serials[^kb-rpc].
- A target list must hold 0 or 2 hardware ids ("Invalid target device list (need 0 or 2 HWIDs)"). A
  hardware id is the half's USB serial string, which equals the `fe/1004` reply; NayaCore checks "HWID
  mismatch - provided port serial (%1) does not match device HWID (%2)"
  <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span> (owner's board, 3.41.0).
- `update_create_fw` with two empty frames flashes the bundled image for each half and flash
  generation; a `firmware_file_path` / `firmwareFilePath` flashes a given file instead
  <span class="tag static">STATIC</span>[^rend][^nc].
- A keymap flash is two events: `update_keymap` (with `db_path`) then `flash_keymap`; out of order
  NayaCore answers "Flow profile is missing. Please update the keymap first." The renderer triggers
  both through `POST /rpc/send-flash-keymap-request`; the exact bg-server sequence is
  <span class="tag inferred">INFERRED</span> <span class="tag static">STATIC</span>[^nc][^rend].
- `set_handshake_frequency` (`frequencyMs`, example "6000") sets NayaCore's periodic fact poll
  ("Periodic:Fact:%1:%2") <span class="tag static">STATIC</span>[^nc].

## Traffic while NayaFlow runs

- **Connect sequence** to the left half: `fe/1001`, `fe/1002`, `fa/1001`, then five Bluetooth reads
  (`be/1008`, `be/1002`, `be/1006`, `be/100f`, `be/100c`), `30/1001` (params `00 00`), `30/1003` per
  layer with the continue loop, `30/1009`, `30/100b` for slots 0-4, `30/100d` per layer, `fe/100b`. To
  the right half: `fe/1001`, `fe/1002`, `fa/1001`, `be/1008`, `be/1002`, `be/100f`
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, NayaFlow 1.25.1, capture of
  2026-09-01).
- **Steady poll every 6 s**: left `be/100c`, `de/1001`, `de/1008`, `de/100b`, `fe/1006`; right the same
  without `be/100c`. The keyboard never pushes battery values; the 6 s tick is NayaCore's handshake
  frequency <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-01). A
  third-party macOS capture shows the right-port polls as `fa/1001`, `fe/1001`, `fe/1002`, `fe/1006`,
  `be/1002`, `be/1008`, `be/100f`, `de/1001`, `de/1008`, `de/100b`
  <span class="tag reported">REPORTED</span> (raw data checked by us, 2026-09-23)[^kb-nayaflow].
- While NayaFlow runs, NayaCore holds every Create port: on Windows a second program gets "Access is
  denied" <span class="tag measured">MEASURED</span>; naya-create-kb reports "Resource busy" on macOS
  <span class="tag reported">REPORTED</span>[^kb-toolkit]. Quit NayaFlow (all three programs) before
  using another tool.
- **Port sorting.** Per half NayaCore keeps a Broker port, a ProtocolCDC port (binary protocol), a
  SystemCDC port (text protocol) and two MCUboot ports; it sorts ports with a broker that sends
  `aa 00 50 00 fe 03 10 01 00 11 04` (and the `0x51` form) and expects `aa 50 00 00 fe 03 10 01 00 11 04`
  from a left half <span class="tag static">STATIC</span>[^nc]. Details on [Disassembly](disassembly.md).

## What "Flash Create" sends

NayaCore reads the board first, then writes the layer list (changed entries only), each changed
layer as one sparse `30/1004` write (`00 <layer>` + only the changed records), a new layer in full (82
records `0x00`-`0x51`, unbound keys as `0e 00`, bays as `78 00`), the module config list and data, the
LED map, then verification reads, and `fe/100a` + `fe/100b` on every flash whether or not the timeouts
changed. Payloads over one frame are chunked with the byte-3 countdown
<span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board,
3.41.0: three NayaFlow flashes captured 2026-09-01 and one 2026-09-17; NayaCore's
`read_profile_before_write_profile` and step names[^nc]). naya-create-kb describes per-key `30/1004`
writes each verified by a full read-back[^kb-nayaflow]; that holds only for a flash that changes one
key.

Example (two keys on layer 1): params `00 01 24 01 04 04 00 07 00 34 01 04 1e 00 07 00`, and the ack
echoes layer `01` <span class="tag measured">MEASURED</span> (capture, 2026-09-01).

| Fact | Evidence |
|---|---|
| The order of NayaCore's write steps is `_remapWriteLayerList`, `_remapReadLayerData` / `_remapWriteLayerData`, `_remapWriteModuleConfigList`, `_remapReadModuleData` / `_remapWriteModuleData`, `_remapReadColorData` / `_remapWriteColorData`; the captured order matches. | <span class="tag static">STATIC</span>[^nc] <span class="tag measured">MEASURED</span>; also reported by naya-create-kb[^kb-nayaflow] |
| Every REMAP write NayaFlow sends goes to the left half (`dst 0x50`); zero REMAP frames went to `0x51` in any captured flash. The left half's LED map has 136 entries per layer and covers both halves (0-73 the keys of both halves, 74-80 and 81-87 the side bars, 88-111 the left bay, 112-135 the right bay), so there is no separate right-half color path. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, captures 2026-09-01; band painting 2026-09-08); answers an open question of naya-create-kb |
| A single-key color change goes out as one sparse `30/100e` write with params `00 <layer> <KK> <hue lo> <hue hi> <sat>`. | <span class="tag measured">MEASURED</span> (capture, 2026-09-01); also reported by naya-create-kb[^kb-nayaflow] |
| NayaFlow never imports a board's keymap into its UI: it shows its own profile and reads the board only to verify, so "Flash Create" pushes its profile over whatever another tool stored. | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's machine, 2026-09-01) |
| Only the profile marked active (`profiles.state = 'ON_BOARD'`) is flashed; the Flash button is disabled with unsaved changes and when the edited profile is not the active one. Labels since 1.19.x: "Active profile (flashes to Naya device)" / "Inactive profile (saves to NayaFlow only)". | <span class="tag static">STATIC</span>[^nc][^bg] <span class="tag doc">DOC</span>[^rel] |

## Features called dead or host-only, revisited

| Feature | What reaches the keyboard | Evidence |
|---|---|---|
| Scan mode, LED maximum brightness, LED action override | A keymap flash sends no `ED` frame, but the three settings are real device commands: `ed/1012` scan-mode PWM, `ed/1013` persistent maximum brightness, `ed/1014` LED action override (0 until keyboard restart, 1 until the next layer change). NayaCore names them SET SCANMODE PWM, SET LED MAX BRIGHTNESS, SET LED LAYER OVERRIDE and checks `scanmode_pwm` and `led_layer_override` in its settings verify; the 1.25.0 notes say NayaCore 6.11.0 "added protocol support" for them. When NayaCore sends them is <span class="tag open">OPEN</span>. naya-create-kb calls these controls dead. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-13/16) <span class="tag static">STATIC</span>[^nc] <span class="tag doc">DOC</span>[^rel] |
| Per-layer LED animations | Sent: byte 2 of each 20-byte layer-list entry `[idx][id][animation][10][uuid16]` holds the animation in ZMK underglow order (0 solid, 1 breathe, 2 spectrum, 3 swirl). Two NayaFlow flashes with known inputs read back 1, 3, 2 and 0, 1, 3. The `animation_id` column came with migration `20260421070750_add_animation_to_layers`; an unset animation reads NULL there. The registry names SOLID, SWIRL, BREATHE, SPECTRUM and the icons `LED_SOLID`, `LED_BREATHE`, `LED_SWIRL`, `LED_SPEC` exist. naya-create-kb says no call reaches the backend. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-08/09) <span class="tag static">STATIC</span> <span class="tag doc">DOC</span> (1.25.0 notes: "per-layer predefined animations"[^rel]) |
| Macros | Host-only. The bg-server has full macro CRUD and macro tables, the renderer ships macros switched off, and NayaCore has no macro read, write, SQL query or serializer; a key bound to a macro is flashed as NONE (`[KK] 07 00`, captured `2e 07 00`). The firmware keeps no macro table: `30/1005` returns one status byte, macro writes are acked and dropped (3.41.0), and 3.28.7 answers the macro opcodes with status `11` (unimplemented). | <span class="tag measured">MEASURED</span> (owner's board 3.41.0, 2026-09-07; donor board 3.28.7, 2026-09-19) <span class="tag static">STATIC</span>; agrees with naya-create-kb[^kb-nayaflow] |
| "naya" actions | The 1.25.1 catalog has one, MODULE_FORCE_CHARGING ("Activate Module Recovery Mode", group Configuration Toggles), and it reaches the board as record type `06` with id 401: `3e 06 04 91 01 00 00` at position 62 of the stock System layer. The MacOS, Windows and VS Code groups on the Integrations tab are chords flashed as ordinary `01` key presses, so plain HID is the intended result for them. naya-create-kb says the device gets DISABLE for these. | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, read-back of a NayaFlow flash, 2026-09-08) <span class="tag static">STATIC</span> |
| "Factory Reset" | No device factory-reset control exists in 1.25.1. The only "Factory Reset" string is an unused locale entry (`settings.general_tap.title.factory_reset`, described "Reset all changes to Naya Flow", beside Language, Theme and placeholder "example" blocks) that the renderer never references. The Danger Zone offers "Clear all keymap data" instead. | <span class="tag static">STATIC</span>[^rend]; also reported by naya-create-kb (as an app-settings reset)[^kb-nayaflow] |

## The UI

- **Destinations** on the icon rail: Keymap (Bindings), Module Configuration, Hardware Manager (Create
  firmware update, Create pairing, module firmware update, Danger Zone force update), Help, Settings
  (tabs Behavior, UI, Connection, Software Update, Backup (Adv.), Troubleshooting (Adv.), Logging
  (Adv.), Software Info). Color mapping is a mode of the key view; there is no macro editor.
  "Hardware Manager" was called DeviceManager until 1.17.2 <span class="tag static">STATIC</span>
  (observed in the running app, 2026-09-01) <span class="tag doc">DOC</span>[^rel].
- **Feature flags** (1.25.1): on colorMapping, keyMapping, moduleConfigurations, settings, help,
  basicActions, extendedActions, layersActions, moduleBindingSlots, basicLayers; off macros,
  layerManagement, bugReport, modulesActions, integrationsActions, customActions, ledToggle,
  behaviorToggle, dynamicLayers, viewToggle, signIn, backwardAndForward, undoAndRedo,
  advancedBehaviors. Only 13 flags are ever read <span class="tag static">STATIC</span>[^rend].
- **Key behavior slots**: Tap (`press`), Hold (needs a tap), Double Tap (needs tap and hold), Tap +
  Hold (label "Tap & Hold", needs the other three); `value` actions are not allowed on keys. Double Tap
  and Tap and Hold arrived with 1.25.0 / NayaCore 6.11.0; a 2026-09-03 capture shows NayaFlow 1.25.1
  writing both banks of a key <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>
  <span class="tag measured">MEASURED</span> (owner's board, 3.41.0).
- **Shortcuts** (1.25.0 and later): Ctrl/Cmd+S saves; Ctrl/Cmd+D runs "Flash Create", and on the
  Hardware Manager page runs the hardware operation (a firmware update of both halves) immediately
  when no warnings are present (the confirmation dialog opens only when there are warnings)
  <span class="tag static">STATIC</span>[^rend] <span class="tag doc">DOC</span>[^rel].
- **Update warnings**: `CREATE_LEFT_BLE_V1_DETECTED`, `CREATE_RIGHT_BLE_V1_DETECTED`, `PAIR_MISMATCH`,
  `MULTIPLE_CREATE_LEFT_CONNECTED`, `MULTIPLE_CREATE_RIGHT_CONNECTED`,
  `FOUR_OR_MORE_CREATE_HALVES_CONNECTED` ("update at most 2 halves at a time"). Updating a BLE v1 left
  half to v2 erases its saved hosts; the split link fails until both halves run BLE v2
  <span class="tag static">STATIC</span> <span class="tag doc">DOC</span>[^rend][^bg].
- **Vendor rules for a keyboard update**: no modules on either half, both halves on direct USB-C cables
  (Y-cables "known to cause issues"), halves switched on, up to 3 minutes, wait for the LEDs to come
  back. The same cabling applies to half-to-half pairing, which NayaCore refuses when the halves run
  different firmware ("Devices have different firmware versions")
  <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^bg][^nc]. The halves still
  type while mismatched, so the refusal is a policy of the pairing flow
  <span class="tag measured">MEASURED</span>[^nh-hw].
- **Vendor rules for a module update**: a single up-to-date Create Left with the module docked; the
  module on; up to 7 s for the module to appear (a minute the first time for a Tune). "Force update"
  (Danger Zone) is for a module that does not answer after Battery Recovery was tried: pick the module
  type physically docked; keyboard and module restart several times; up to 4 minutes
  <span class="tag doc">DOC</span>[^bg].
- **Troubleshooting buttons**: "Test and Format SPI-Flash" (`repair_flash`) tests the halves' flash and
  reformats only partitions with errors, warning that keymaps may be overwritten; "Clear all keymap
  data" (`clear_data`), which the vendor recommends when Flash Create keeps failing; "Clear BLE
  Devices" makes the keyboard forget every Bluetooth host (the host may need to forget it too)
  <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^bg][^nc].
- The tray setting "Module battery in tray" shows each docked module's type, side and level, polled
  every 5 s <span class="tag static">STATIC</span>[^main]. NayaFlow relaunches itself whenever a module
  is docked again (docking re-enumerates that half's USB) <span class="tag measured">MEASURED</span>
  (owner's machine, 3.41.0).
- NayaFlow and the NayaFlow-Beta app cannot run at the same time; the beta imports user data from the
  stable app (`/rpc/import-userdata-beta`, beta 1.17.0 "User Data Import System")
  <span class="tag doc">DOC</span> <span class="tag static">STATIC</span>[^beta][^rend].

## Hazards in stock NayaFlow

| Hazard | Severity | Evidence |
|---|---|---|
| Ctrl/Cmd+D on the Hardware Manager page updates both halves' firmware without a dialog when no warning is present. | high | <span class="tag static">STATIC</span>[^rend] |
| Danger Zone actions (`repair_flash`, `clear_data`, `clear_ble_devices`) ran without a confirmation dialog when observed. | high | <span class="tag static">STATIC</span> (observed once, 2026-09-01; re-check open, [details](../open-questions.md#oq-s16)) |
| A NayaFlow flash overwrites whatever another tool stored. | medium | <span class="tag measured">MEASURED</span> (2026-09-01) |
| "Failed to verify written data" after a flash: the board holds second-bank records (position `KK+0x52`, double tap or tap + hold) that the profile does not describe, for example written by another tool; NayaFlow's sparse diff never clears them and its reader folds a key and its second bank together. The flash itself landed. Writing `[KK+0x52] 07 00` once clears it. | medium | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-09 and 2026-09-17) |
| NayaFlow's verify read-back shows every hold-tap record at tapping term 200 and flavor 1 whatever the board holds (for example 180 / 0), so any key with a hold mismatches once the term is not 200. The keyboard is not affected. | low | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-17) |
| NayaCore has no `ENTER`, `PAGE_UP`, `PAGE_DOWN` or `CLICK` token (it uses `RETURN`, `PG_UP`, `PG_DN`), so catalog chords using them flash wrongly: `LALT + ENTER` (WIN_DISPLAY_PROPERTIES) went out as `00 00 00 04`, the modifier alone. | medium | <span class="tag measured">MEASURED</span> (NayaFlow flash capture) <span class="tag static">STATIC</span> |
| The renderer drops the base layer from Toggle Layer targets because `&tog 0` from a higher layer leaves the keyboard stuck there until a power cycle. | (guarded) | <span class="tag static">STATIC</span> <span class="tag measured">MEASURED</span> (owner's board, 3.41.0) |
| NayaFlow cannot write pinch and spread (the category-8 zoom axis on Tune and Touch): its combined control accepts only `value` actions and its catalog has no zoom; of three pinch bindings in its database the profile NayaCore built carried only spread. | low | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-18) |
| NayaFlow accepts a hold on a Track button that the device cannot store: the hold silently replaces the tap. | medium | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-03) |
| In one flash NayaFlow removes module profiles no layer references (bays set to 0, list entry deleted, slot blanked with 40 empty records), writes its own profile UUIDs back to slots, and once cleared Track Right button 1 during an "enable all modules" flash (params `00 01 0b 07 00`: slot 1, field `0x0b` set to NONE). | medium | <span class="tag measured">MEASURED</span> (owner's board, 3.41.0, 2026-09-03) |
| The stock Tune three-finger swipes labeled "LED Brightness Up/Down" are flashed as an empty key press (`01 04 00 00 00 00`): no HID output and no LED change was seen. What the keyboard does with it is <span class="tag open">OPEN</span>. | low | <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span> (owner's board, 3.41.0, module 2.3.3) |
| The chord recorder writes codes that differ from the catalog (`CAPS_LOCK` vs `CAPSLOCK`, `SCROLL_LOCK` vs `SCROLLLOCK`, `ESCAPE` vs `ESC`, `PAGE_UP`/`PAGE_DOWN` vs `PG_UP`/`PG_DN`), accepts `LSHFT`/`RSHFT` and bare `CTRL`; PrintScreen cannot be recorded; NumpadEnter and NumpadDecimal are unmapped. | low | <span class="tag static">STATIC</span>[^rend] |
| Chord presets carry one name per chord regardless of OS (for example Ctrl+Up named "Mission Control" in the Windows presets). | low | <span class="tag static">STATIC</span>[^bg] |

!!! warning "Local programs can drive the keyboard through the bridge"
    `set_handshake_frequency`, `repair_flash`, `clear_data` and `clear_ble_devices` can be sent by any
    local program through `/rpc/send-nayacore-zmq-message`; do not script them against a
    daily-driver board.

## Runs without any vendor server

- No API base URL, account, credential, license check, cloud sync or telemetry was found, nor a kernel
  driver, background service, autostart entry or per-device calibration file; every route is on
  localhost, and the keyboard and module firmware ship inside NayaCore, so updates work offline
  <span class="tag static">STATIC</span> (searches of all four bundles).
- The only outbound calls found are update checks: electron-updater against
  `NayaTech/NayaFlow-releases` (channel `latest`, publisher "Naya B.V.", auto-download and
  install-on-quit on, downgrade off) and the bg-server's component manager (repositories
  `NayaFlow-`, `NayaCore-`, `NayaTouch-`, `NayaTrack-`, `NayaTune-`, `NayaFloat-releases`). The token they
  send is an unsubstituted build placeholder, so GitHub answers 401 even for the public repository and
  every "latest tag" lookup comes back empty <span class="tag static">STATIC</span>
  <span class="tag measured">MEASURED</span> (`app-update.yml`; proxy capture on the owner's machine,
  2026-09-01).

## Unpacking the app

An `app.asar` file starts with u32 4 and a u32 header size, then a pickled string: its u32 JSON length
sits at file offset 12 and the JSON at offset 16; file data starts at offset 16 + the JSON length
rounded up to 4, and each entry's offset counts from there. `npx @electron/asar extract` does the same
<span class="tag static">STATIC</span>; also described by naya-create-kb[^kb-nayaflow].

Useful trees in the 1.25.1 asar: `dist/main/index.js`, `dist/renderer/assets/` (renderer bundle
`index-mihUmo_8.js`), `assets/icons/action/` with 860 action icons. The firmware is not in the asar:
it is embedded as Qt resources in the NayaCore binary <span class="tag static">STATIC</span>; also
reported by naya-create-kb, whose author reused the icon set for a web client
<span class="tag reported">REPORTED</span>[^kb-nayaflow]. Carving the images is covered on
[Firmware images](../firmware/images.md).

## Open questions

- <span class="tag open">OPEN</span> The bytes the "Clear all keymap data" button sends ([details](../open-questions.md#oq-f16)).
- <span class="tag open">OPEN</span> When NayaCore sends `ed/1012`, `ed/1013`, `ed/1014` (capture a settings change without flashing).
- <span class="tag open">OPEN</span> How `/factory-reset` is registered and what it answers ([details](../open-questions.md#oq-s01)).
- <span class="tag open">OPEN</span> The value of `oldBLELibDeprecatedCreateLeftFWVersion` ([details](../open-questions.md#oq-s02)).
- <span class="tag open">OPEN</span> What the keyboard does with an empty key press record.
- <span class="tag open">OPEN</span> Whether the Danger Zone buttons really act without a dialog ([details](../open-questions.md#oq-s16)).

## Sources

[^main]: NayaFlow 1.25.1, `resources/app.asar`: `dist/main/index.js`, `dist/main/preload.mjs`, `preload.update-window.mjs`, and `app-update.yml` in the installed tree.
[^rend]: NayaFlow 1.25.1, `resources/app.asar`: renderer bundle `dist/renderer/assets/index-mihUmo_8.js` and `dist/renderer/locales/`.
[^bg]: NayaFlow 1.25.1, `flow/flow-bg-server.exe` (Windows) and `Contents/flow/flow-bg-server` (macOS): strings and embedded data (catalog, templates, settings, i18n).
[^nc]: NayaFlow 1.25.1 for Windows, `core/NayaCore/NayaCore.exe` (NayaCore 6.11.0): strings (event names, step names, log formats, build paths, the port-detector frames).
[^nc-mac]: NayaFlow 1.25.1 for macOS, `NayaFlow.app/Contents/core/NayaCore.app/Contents/MacOS/NayaCore` (NayaCore 6.11.0; the arm64 build's MD5 is `84ded78022b6d312483aae0192584168`): symbols and code (the event table, the dispatcher, `doClearAllDataOperations`). See [Disassembly](disassembly.md).
[^rel]: Vendor release notes, [NayaTech/NayaFlow-releases](https://github.com/NayaTech/NayaFlow-releases/releases), mirrored in create-legacy-firmware [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases).
[^nh-hw]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#measured-on-hardware-both-halves-2026-09-20).
[^nx]: nayactl, [`constants.py`](https://github.com/Qonfused/nayactl) (shared-memory names and topics).
[^kb-nayaflow]: naya-create-kb, [software/nayaflow](https://nemezzizz.github.io/naya-create-kb/software/nayaflow/).
[^kb-rpc]: naya-create-kb, [software/rpc-zmq](https://nemezzizz.github.io/naya-create-kb/software/rpc-zmq/).
[^kb-toolkit]: naya-create-kb, [toolkit](https://nemezzizz.github.io/naya-create-kb/toolkit/).

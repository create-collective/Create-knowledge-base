# Recovery

This page is a cookbook: find the symptom, then follow the recipe. Every recipe states its safety
level and whether it has been tested on hardware (by us, by the owner of the boards we measured, by a
third party) or not at all, with the firmware it was tested on. The thing to know first: most "dead"
halves are not dead. A half parked in its bootloader, halves on different firmware, and a broken
link between the halves all look alike to a user, and each has a different, mostly low-risk cure.
The list of commands never to send is on [Troubleshooting](troubleshooting.md#the-never-send-list).

!!! danger "You can damage a half. Read the safety notes first."
    Recipes marked HIGH write firmware, wipe data or drop Bluetooth bonds. Make first attempts on a
    donor board. Recipes marked UNTESTED have never been run on hardware by anyone we know of.

## How to read a recipe

Safety levels:

- **SAFE**: read-only.
- **LOW**: nothing stored changes, or the change is fully reversible.
- **MEDIUM**: writes stored configuration, recoverable from a backup.
- **HIGH**: writes firmware, wipes data or drops bonds; can brick a half or lose data.

Tested markers: **TESTED (us)** with firmware and date, meaning measured on the owner's boards;
**TESTED (third party)**, meaning reported by someone else and not repeated by us; **UNTESTED**.

| Recipe | Symptom | Safety | Tested |
|---|---|---|---|
| [R1](#r1-half-dark-and-not-typing-shows-up-as-a-bootloader-device) | half dark, not typing, bootloader PID | LOW | TESTED (us), 3.35.4 and 3.41.0 |
| [R2](#r2-bootloader-device-only-primary-image-not-valid-untested) | bootloader PID only, "primary image not valid" | HIGH | UNTESTED |
| [R3](#r3-halves-on-different-firmware) | peripheral dark but typing, empty replies | HIGH | TESTED (us), 3.35.4 and 3.41.0 |
| [R4](#r4-right-half-scans-but-its-keys-never-arrive) | right half's keys never arrive | SAFE (diagnosis), HIGH (repair) | TESTED (us), 3.35.4 |
| [R5](#r5-lights-wrong-after-a-flash-or-a-bootloader-pass) | white, amber or dim after a flash | MEDIUM | TESTED (us), 3.35.4 and 3.41.0 |
| [R6](#r6-board-dark-but-typing) | whole board dark, typing works | LOW to MEDIUM | our steps TESTED (us) one by one, 3.41.0; the ceiling re-send TESTED (third party) |
| [R7](#r7-right-half-dark-after-led-commands-sent-to-it) | right half and its module dark after LED writes | MEDIUM | hazard TESTED (third party); fixes UNTESTED |
| [R8](#r8-a-3287-half-stops-answering-after-a-write) | 3.28.7 half frozen after a write | LOW | TESTED (us), 3.28.7 |
| [R9](#r9-module-dead) | module not recognized, no light | LOW | TESTED (us), 3.28.7 with modules on 2.1.2 |
| [R10](#r10-every-key-stopped-after-a-keymap-write) | every key stopped after a write | LOW | TESTED (us), 3.41.0 |
| [R11](#r11-keyboard-frozen-after-switching-output-to-wireless) | frozen after the wireless-output key | LOW | TESTED (us), 3.41.0 |
| [R12](#r12-stuck-on-an-upper-layer) | stuck on an upper layer | LOW | TESTED (us), 3.41.0 |
| [R13](#r13-reads-answer-16-00) | reads answer `16 00` | MEDIUM | meaning TESTED (us); restore TESTED (third party) only |
| [R14](#r14-nayaflow-says-failed-to-verify-written-data) | NayaFlow "Failed to verify written data" | LOW to MEDIUM | TESTED (us), 3.41.0 |
| [R15](#r15-bluetooth-hosts-forgotten-after-an-update) | computers forgotten after an update | LOW | vendor documentation |
| [R16](#r16-module-will-not-charge) | module will not charge | LOW | vendor documentation |

## First checks

!!! note "Read-only; do these before any recipe"
    Safety SAFE. TESTED (us) on every firmware we have.

Before any recipe <span class="tag measured">MEASURED</span>:

1. Quit NayaFlow and any other tool. One program per port: on Windows a held port gives "Access is
   denied", and a killed script's Python process can still hold it.
2. Read `fe/1002` (firmware version) on each half's own port, and on the left port at `dst 0x51`: a
   half can silently miss an update ([Versions](firmware/versions.md#firmware-in-the-field)).
3. Look for a half at a bootloader PID (`0x006F` left, `0x00D3` right), twice, 3 s apart
   ([Bootloader](firmware/bootloader.md#passing-through-versus-parked)).

Then, for a dark half: a bootloader PID on the second look is R1 or R2; different firmware versions
are R3; a right half whose keyscan events arrive but whose keys do not reach the computer is R4;
lighting that is only wrong is R5, R6 or R7.

## R1 Half dark and not typing, shows up as a bootloader device

!!! note "Safety LOW. TESTED (us) on 3.35.4 and 3.41.0, 2026-09-16 to 2026-09-22."
    It sends one SMP reset; nothing stored changes.

The half shows no lights and does not type. It enumerates as `0x006F` (left) or `0x00D3`
(right) with two serial ports, and it is still there on a second look 3 s later <span class="tag measured">MEASURED</span>.

1. Find the port that answers SMP `os echo` (the other port only logs).
2. Send SMP `os reset` (group 0, id 5, version-1 header) to that port. The half returns to its
   application in about 8 s; a transport error on the reset means it worked.
3. If it does not come back, re-send every 30 s; right after an upload, allow minutes.
4. A power cycle also works when the primary image is valid.

Frames and details: [Bootloader](firmware/bootloader.md#getting-in-and-getting-out).

The first SMP answer after entering the bootloader can take a minute: in the logged flash runs it
came 60.8 to 69.0 s after entry on the left half and 24.4 to 26.1 s on the right (once only 3.8 s),
while OpenFlow re-probed about every 2 s, without any idle period (owner's board, 2026-09-20 and
2026-09-22) <span class="tag measured">MEASURED</span>. Part of that wait was the host's: OpenFlow then
reopened the answering port for every request and never read the half's second (log) port. Holding
both ports open for the whole visit and reading the log port, as NayaCore does, cut identifying the
running image from 63 s to 26 s in a module update (owner's board, left half, 3.41.0, 2026-09-23)
<span class="tag measured">MEASURED</span> ([open question](open-questions.md#oq-f05)).

## R2 Bootloader device only, primary image not valid (untested)

!!! danger "Safety HIGH. UNTESTED: nobody we know of has done this on a Create."
    It writes firmware to a half that already fails to boot. Make the first attempt on a donor half.

The half enumerates only as a bootloader device, and its log port says "Image in the
primary slot is not valid". MCUboot's standard answer is to put a good image in the secondary slot
and let it swap in <span class="tag inferred">INFERRED</span>[^mcuboot]:

1. Record the console output first.
2. Identify side and generation from the PID ([Bootloader](firmware/bootloader.md#usb-identity)).
3. Read `image state`. Stop if the PID and the slot hashes disagree on side or generation.
4. Upload the matching stock resource, whole, to `image: 2` (never 0 or 1).
5. Send `os reset` and wait minutes (swap and decrypt), re-sending as needed.

A swap onto an already-invalid primary has never been tried on this hardware. OpenFlow's planner
currently refuses a half whose running image it cannot identify, so it would need a PID-only path
first. The scenario comes from a third party's report of a half stuck in its bootloader, which we do
not cite <span class="tag reported">REPORTED</span> ([open question](open-questions.md#oq-f14)).

## R3 Halves on different firmware

!!! danger "Safety HIGH (the fix writes firmware). TESTED (us): halves put on different firmware and matched again, 3.35.4 and 3.41.0, 2026-09-20 to 2026-09-22."

Both halves type, but the peripheral's LEDs are dark, and the peripheral's own port
answers the handshake and then returns empty payloads. Its version stays readable through the
central's port at `dst 0x51`: the left port read the right half's version 3.35.4 while the right's
own port was hollow <span class="tag measured">MEASURED</span>[^fp-measured]. Bluetooth identity reads sent to `0x51` on the left port
answer for the left half, not the right ([Transport](protocol/transport.md)). OpenFlow has no
automatic retry through that route. NayaFlow refuses its pairing flow ("Devices have different
firmware versions").

Fix: flash both halves to the same version, the central (left) first
([Flashing](firmware/flashing.md#two-halves)). Everything recovers once they match.

## R4 Right half scans but its keys never arrive

**Diagnosis.**

!!! note "Safety SAFE (reads only). TESTED (us), 2026-09-20."

Turn on keyscan on the right half (`fe/1008`): if events arrive, the right half is alive.
Then compare, on both halves, the own address (`be/1008`), the pair address (`be/1002`) and the bond
table (`be/1005`). Healthy is mutual: each half's pair address is the other half's own address. The
measured failure: the right half held a bond to the left, but the left's bond table held one host
address twice and no bond to the right <span class="tag measured">MEASURED</span> (owner's board, 2026-09-20; addresses not published).
See [Split link](connectivity/split-link.md).

Clearing Bluetooth bonds on the computer does not fix this. The link between the halves
lives in each half's own pair address and bond table, and the 2026-09-20 repair needed commands to
the halves only <span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>.

**Repair.**

!!! danger "Safety HIGH: drops every Bluetooth host bond. TESTED once by hand (us), 3.35.4, 2026-09-20; the owner reports a repair on 3.41.0 as well. No tool has automated it on hardware."
    Put both halves on the same firmware first (R3). Save both halves' own and pair addresses
    before sending anything.

In NayaCore's pairing order <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>[^nc]:

1. `be/1001` SET_PAIR_ADDRESS on each half, with the other half's own address;
2. wait 300 ms;
3. `be/1010` CLEAR_ALL_SPLIT_LINKS on each half;
4. `be/1004` UNPAIR_ALL on each half;
5. wait 1 000 ms and wait for the peer;
6. `ee/10ce` NORMAL_RESET (on 2026-09-20 it was sent to the left half);
7. check that the pair addresses are mutual.

The result was a clean mutual bond and both halves typing. UNPAIR_ALL also drops every host bond, so
pair the computers again afterwards. The power cycle used that night to leave the bootloader was
unnecessary: `os reset` on the port that answers SMP does it (R1). The repair sequence ends with a
reset command (`ee/10ce` NORMAL_RESET); on 2026-09-20 a power cycle was also done afterwards. Whether
the reset alone is enough is untested; a test on the donor board settles it.

NayaCore refuses its own pairing operation with "Pairing failed: missing device(s)
(left=%1, right=%2)" or "Devices have different firmware versions". Its sibling ClearBLEDevices
operation runs CheckBLEFWVersion, WaitForPairAddress, StorePairedHalfAddressBeforeClear,
ClearConnections, VerifyConnectionsCleared, Respawn, RecheckBLEStatus, WaitForBLEStatus and
VerifyBLEFWVersion. The rule that matters: store the partner's address before clearing anything
<span class="tag static">STATIC</span>[^nc].

The vendor's guidance on pairing the halves: power the left half on before the right, and
"make sure your two halves are paired together using the device manager" <span class="tag doc">DOC</span>[^man-create].

## R5 Lights wrong after a flash or a bootloader pass

!!! warning "Safety MEDIUM: a layer-list write. TESTED (us and the owner): 2026-09-10 after a runtime effect; 2026-09-20 and 2026-09-22 after flashes (3.35.4 and 3.41.0)."
    Write back only the bytes you just read from the same board, and only to the left half. Other
    layer ids would replace the layer identities.

A half comes back from a flash or any bootloader pass white, a darker amber, or dim, while
its stored LED maps are byte-identical <span class="tag measured">MEASURED</span>:

1. Read the layer list with `30/1001` on the left half.
2. Write the same entries back with `30/1002` (wire params `00 00` followed by the entries). Both
   halves return to their stored lighting in one frame, and nothing stored changes.
3. If the board is dim, re-send the maximum brightness: `ed/1013` with value 100, params `00 00 64`.

A runtime LED effect (`ed/1011`) survives layer, LED-map and module writes; only a
layer-list rewrite or a power cycle clears it <span class="tag measured">MEASURED</span> (owner's board, 2026-09-10). Layer list format:
[Layers](protocol/layers.md).

## R6 Board dark but typing

!!! warning "Safety LOW to MEDIUM (settings writes). Each step TESTED (us) on its own, 3.41.0; re-sending the ceiling to a board dark for weeks TESTED (third party: the nayactl PR #6 author, 3.41.0)."

The keys stay dark while both halves type. Work through these steps in order
<span class="tag measured">MEASURED</span> <span class="tag inferred">INFERRED</span>:

1. Check `fe/1002` on both halves: a firmware mismatch darkens the peripheral (R3).
2. Re-send the brightness ceiling `ed/1013` with value 100, params `00 00 64`. The ceiling scales the
   whole key array and is stored: on the owner's board a ceiling of 30 dimmed every key and 100
   restored them (3.41.0, 2026-09-13) <span class="tag measured">MEASURED</span>. A stored ceiling of 0 would therefore be a board that
   stays dark across reboots <span class="tag inferred">INFERRED</span>, which is what the nayactl PR #6 author reports <span class="tag reported">REPORTED</span>[^nx-pr6].
   Module LEDs are outside the ceiling, per the same author <span class="tag reported">REPORTED</span>.
3. Rewrite the layer list as in R5; it clears runtime LED effects.

**If the keys stay dark.** Scan mode is not a likely cause: switching `ed/1012` off and on changed only
a flicker that shows on camera <span class="tag measured">MEASURED</span> (owner's board, 3.41.0,
2026-09-13), so a zeroed scan mode should not darken the keys <span class="tag inferred">INFERRED</span>.
A cold boot ([Resets and power](#resets-and-power)) clears runtime lighting states but cannot
clear a stored ceiling <span class="tag inferred">INFERRED</span>. Nothing beyond these steps has been
tested by us, and `30/10ca`, which wipes the stored configuration, is on the
[never-send list](troubleshooting.md#the-never-send-list). This differs from naya-create-kb, whose
dark-board recipe goes on to that wipe (with params `01`, where NayaCore sends `00 00`) and a snapshot
restore[^kb-recovery].

## R7 Right half dark after LED commands sent to it

!!! warning "Safety MEDIUM. The hazard is TESTED (third party), 3.41.0; the suggested fixes are UNTESTED by anyone."

One third-party run of a nine-write LED recovery sequence sent to the right half's own port
(`dst 0x51`), including RESUME (`ed/1010`) and an RGB override (`ed/1050`), left the right half's LEDs
and its docked module dark while it still typed; eight of the nine writes were acknowledged (3.41.0,
2026-09-22), and whether a stock NayaFlow flash relit it was left unconfirmed
<span class="tag reported">REPORTED</span>[^kb-recovery]. Which write did it is unknown. A single
ceiling write (`ed/1013` `00 00 64`) to the right half's own port was acknowledged and did not park it
(owner's board, 3.35.4 and 3.41.0, 2026-09-20 and 2026-09-22) <span class="tag measured">MEASURED</span>.
Commands sent to the left half do reach the right half's lighting: one layer-list rewrite on the left
restores both halves (R5) <span class="tag measured">MEASURED</span>.

Why the left port can relight the right: the central (left) drives both halves' LEDs from
its own 136-entry map over the split link <span class="tag inferred">INFERRED</span> (from measured bay blocks and the layer-list restore of
both halves, 2026-09-08 to 2026-09-10).

The right half is not deaf by design: on its own port it answers the handshake
(`fe/1001`, `fe/1002`) and system, Bluetooth, module and `fa/1001` reads <span class="tag measured">MEASURED</span>, and it acknowledges the ceiling
write above. What it lacks is the configuration stores: keymap, LED maps, layer list and module
configurations are all on the left ([Flash layout](storage/flash-layout.md#what-each-half-stores)).

Untested candidates for a right half parked this way, least invasive first <span class="tag inferred">INFERRED</span>: the R5
layer-list rewrite sent to the left half, which restores both halves' stored lighting; the ceiling
re-sent to the right half's own port (`ed/1013` `00 00 64`), which relit a dim right half after a
flash; and the keyboard's own LED keys, which are firmware `&rgb_ug` records and need no host. In the
stock profile they sit on the System layer (Layer 2, held at position 73), mostly on the right half:
positions 9 to 12 select effects, 24 and 40 raise and lower brightness, 25 and 41 change speed, and 39
turns the LEDs on and off <span class="tag measured">MEASURED</span> (NayaFlow's stock profile read back, 2026-09-08).

## R8 A 3.28.7 half stops answering after a write

!!! note "Safety LOW (unplug and replug). TESTED (us), 3.28.7, 2026-09-19."

Right after a keymap or LED write, a 3.28.7 half stops answering and typing while its LEDs
keep the old map. The write needed three CDC frames (byte 3 counting `02 01 00`), which 3.28.7 cannot
receive. Unplug and replug the half: no damage (it came back at 4.21 V). From then on, split large
writes on record boundaries into writes of at most two frames, each starting `00 <layer>` again (at
most 482 record bytes per write) <span class="tag measured">MEASURED</span>. 3.41.0 takes NayaFlow's own three-frame writes, and single
`30/100e` frames of up to 253 bytes were accepted on 3.41.0 (owner's boards, 2026-09-16 and
2026-09-21) <span class="tag measured">MEASURED</span>. The nayactl PR #6 author reports that `30/100e` writes of 241 and of 41 bytes wedged the parser until a power cycle (3.41.0) <span class="tag reported">REPORTED</span>[^nx-pr6]; since 253-byte frames were accepted, that is a different limit, not defined by size <span class="tag inferred">INFERRED</span>.

## R9 Module dead

!!! note "Safety LOW (a key press). TESTED (us), 3.28.7 with modules on 2.1.2, 2026-09-19; untested on 3.41.0."

A module is not recognized when docked and shows no light. Measured on 3.28.7 with
modules on 2.1.2: hours of charging did not help, and the module recovery key did (a Tune and a
Touch came back) <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span>. Press the key (System layer `LA5`, record type `06` with parameter 401) on
the half whose bay holds the module. It puts that half's LEDs out and disables the module while
active, times out by itself (repeat when it does), and a restart ends it. The vendor's cure for this
firmware pair was a later firmware plus Force Module Update. Details: [Module firmware](firmware/modules.md#module-recovery-mode).

## R10 Every key stopped after a keymap write

!!! note "Safety LOW (after the fact). TESTED (us), 3.41.0, 2026-09-03."

A hold-tap flavor value of 4 was accepted and stored and stopped every key; rewriting the
record did not help; unplugging the board (a power cycle) did, and nothing on flash was damaged.
Rewrite the record with a flavor of 0 to 3 <span class="tag measured">MEASURED</span>. See [Settings and timing](protocol/settings.md).

## R11 Keyboard frozen after switching output to wireless

!!! note "Safety LOW (a power cycle). TESTED (us), 3.41.0, 2026-09-10 and 2026-09-11."

On battery, pressing the wireless-output key with no reachable wireless host froze the
keyboard: nothing typed and layer switching stopped. A power cycle recovers. Pressing the USB-output
key after selecting a Bluetooth device with no host also made the board look crashed (its USB ports
stayed up); a power cycle cleared it <span class="tag measured">MEASURED</span>.

## R12 Stuck on an upper layer

!!! note "Safety LOW (a power cycle). TESTED (us), 3.41.0."

A toggle-layer binding to layer 0 (`&tog 0`) pressed from a higher layer strands the board
there until a power cycle. NayaFlow does not allow that binding <span class="tag measured">MEASURED</span>.

## R13 Reads answer `16 00`

!!! warning "Safety MEDIUM (the restore writes the keymap). Meaning TESTED (us, 3.28.7; third party, 3.41.0); the restore after a format TESTED (third party) only."

`30/1001` or `30/1003` answering `16 00`: status `0x16` means nothing is stored for that
read. Right after `30/10ca` that is expected; restore from the snapshot as described on
[Factory reset](storage/factory-reset.md#restoring-afterwards) <span class="tag measured">MEASURED</span> <span class="tag reported">REPORTED</span>.

## R14 NayaFlow says "Failed to verify written data"

!!! warning "Safety LOW to MEDIUM. TESTED (us), 3.41.0, 2026-09-09 and 2026-09-17."

Known causes: second-bank records that NayaFlow's profile does not describe, a tapping
term other than 200, and a NayaFlow flash right after `30/10ca`. None affects typing. Fixes and
details: [Factory reset](storage/factory-reset.md#failed-to-verify-written-data) <span class="tag measured">MEASURED</span>.

## R15 Bluetooth hosts forgotten after an update

!!! note "Safety LOW. From the vendor's documentation; not reproduced by us."

Updating from Bluetooth v1 firmware (3.31.1 or older) to v2 (3.35.4 or newer) erases the
saved hosts, and the link between the halves fails until both halves are on v2. Update both halves
and pair the computers again <span class="tag doc">DOC</span>[^cl-222] ([Versions](firmware/versions.md#what-changed-by-version)).

## R16 Module will not charge

!!! note "Safety LOW. From the vendor's manuals."

Check the cable and the computer, and seat the module flat. If it stays unresponsive, use
the manual's Recovery Mode keybinding (R9). Undock modules for long storage (battery protection), and
charge from a computer, not a wall outlet <span class="tag doc">DOC</span>[^man-modules][^man-create].

## Resets and power

**Reset commands** <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>:

- `ee/10ce` NORMAL_RESET reboots the half through its bootloader. Its port drops at once (a transport
  error after 7.7 ms on 3.35.4, 2026-09-20); on 3.41.0 the bootloader identity (`0x006F`) showed 0.65
  to 0.84 s after the command for about 1.3 s, and the application was back after about 3 s (owner's
  board, left half, 2026-09-23) <span class="tag measured">MEASURED</span>
  ([closed question](open-questions.md#oq-f03)). On Windows 11 the half came back by itself only after the first two
  restarts in a row; from the third it stayed off USB until its cable was replugged
  <span class="tag measured">MEASURED</span> ([open question](open-questions.md#oq-f27)).
- `ee/10ae` MCU_BOOT_RESET parks the half in its bootloader until `os reset` (R1).
- `ee/10be` DFU_RESET has never been observed by anyone we know of; do not send it.

**Power cycles and the power switch.** Every power-on passes through the bootloader for 1
to 1.7 s, and powering one half reboots the other when the link comes back, so a one-half power cycle
is a two-half reboot <span class="tag measured">MEASURED</span>. With USB plugged in, switching a half OFF shuts it off, and switching it
back ON works as a reset (owner, 2026-09-23) <span class="tag measured">MEASURED</span>. That agrees with the manual, which says the Create
respects the ON/OFF state even while connected over USB <span class="tag doc">DOC</span>[^man-create]. So the switch is a usable reset for
one half without unplugging. Safety SAFE. TESTED (owner, 2026-09-23).

A **cold boot** removes every power source: USB out, modules undocked (a docked module can
power the keyboard) and both switches off <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span>.

| Action | What it does | Evidence |
|---|---|---|
| `os reset` (SMP, data port) | leaves the bootloader; about 8 s to the application | <span class="tag measured">MEASURED</span> |
| `ee/10ce` NORMAL_RESET | reboots the half through its bootloader (about 1.3 s); its port drops at once and the application is back in about 3 s | <span class="tag measured">MEASURED</span> |
| `ee/10ae` MCU_BOOT_RESET | parks the half in its bootloader until `os reset` | <span class="tag measured">MEASURED</span> |
| `ee/10be` DFU_RESET | unknown; never observed | <span class="tag static">STATIC</span> |
| Unplug and replug USB (battery half) | reboots through the bootloader (1 to 1.7 s) and reboots the other half at re-link | <span class="tag measured">MEASURED</span> |
| Power switch OFF then ON, USB plugged in | shuts the half off, then resets it | <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span> |
| Cold boot | removes every power source | <span class="tag measured">MEASURED</span> <span class="tag doc">DOC</span> |

## Brightness 0 and the brightness keys

`ed/1008` with level 0 leaves the keys dark, and the next `ed/1008` with a level above 0 relights
them: a two-byte write (params `00 00 64`) restored a half that a one-byte write had set to 0
<span class="tag measured">MEASURED</span> (owner's board, left half, 3.41.0, 2026-09-09). The stock
brightness keys are firmware records (`&rgb_ug` with its brightness up and down commands and argument
0), so the firmware computes each step and the host puts no step value on the wire; NayaCore's 15 ZMQ
events include no LED command, and none of our NayaFlow captures contains an ED frame
<span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>. How the keys behave
at either end of the range has not been measured.

## The vendor's own recovery tools

Clear BLE Devices and Test and Format SPI Flash (NayaCore 6.4.0; NayaFlow beta 1.18.0 and
stable 1.19.1), module recovery for "battery Zero" (NayaFlow 1.3.8), Force Module Update (1.15.0) and
a one-click diagnostics report (1.21.0) <span class="tag doc">DOC</span>[^cl][^beta]. What the flash test does:
[Flash layout](storage/flash-layout.md#the-vendors-repair-and-clear-buttons).

A firmware flash does not fix a stored-state problem, because the stores survive flashes,
and NayaFlow's "Test and Format SPI Flash" does nothing on a healthy flash: it formats only the
partitions that fail its self-test <span class="tag measured">MEASURED</span> <span class="tag static">STATIC</span>.
Its Danger Zone button "Clear all keymap data" (`clear_data`) does wipe the stored configuration:
it sends `30/10ca` itself, with no confirmation dialog <span class="tag static">STATIC</span>[^nc]
([Factory reset](storage/factory-reset.md)). This differs from naya-create-kb, which says nothing in
the stock interface formats the data partition[^kb-recovery].

## "My right half stopped working"

A half that does not power on or enumerate and a pair that is no longer bonded look the
same to a user, and NayaFlow has no per-half diagnosis for it (NayaCore carries Japanese-only
"one half connected" warnings that are not wired in) <span class="tag static">STATIC</span> <span class="tag inferred">INFERRED</span>[^nc]. Use the first checks and the R4
diagnosis to tell them apart.

## Tested and untested

Done on the owner's hardware (status 2026-09-23): R1; R3 (different firmware, then
matched); R4 (3.35.4, and 3.41.0 per the owner); R5 (restoring layers and lighting after a flash);
R6's steps, each on its own; R8; R9; R10; R11; the power switch as a reset on USB; `ee/10ce` through
the bootloader. R12, the meaning of `16` in R13, and R14 are measured too. Not done: R2; the
`30/10ca` restore (R13); and the other recipes that wait for a donor board. R15 and R16 are vendor
documentation only <span class="tag measured">MEASURED</span>.

## Open questions

- <span class="tag open">OPEN</span> R2 on real hardware: a swap onto an invalid primary ([details](open-questions.md#oq-f14)).
- <span class="tag open">OPEN</span> Whether anything but re-sending the ceiling clears a board left dark by a stored ceiling of 0 (the R5 layer-list rewrite, a cold boot), and what relights a right half parked as in R7 ([details](open-questions.md#oq-f15)).
- <span class="tag open">OPEN</span> Why a half stays off USB from the third `ee/10ce` restart in a row until its cable is replugged ([details](open-questions.md#oq-f27)).
- <span class="tag open">OPEN</span> What `ee/10be` DFU_RESET does ([details](open-questions.md#oq-c01)).
- <span class="tag open">OPEN</span> Recovery-mode behavior on 3.41.0 with modules on 2.3.3 ([details](open-questions.md#oq-f22)).
- <span class="tag open">OPEN</span> Whether the reset command alone completes the pairing repair (on 2026-09-20 a power cycle was also done afterwards); a donor-board test settles it ([details](open-questions.md#oq-c17)).
- <span class="tag open">OPEN</span> What wedged the parser in the nayactl PR #6 author's `30/100e` writes of 241 and 41 bytes, given that single frames up to 253 bytes are accepted on 3.41.0 ([details](open-questions.md#oq-f21)).

## Sources

[^kb-recovery]: naya-create-kb, [recovery](https://nemezzizz.github.io/naya-create-kb/recovery/).
[^fp-measured]: create-legacy-firmware, [`FLASHING-PROCEDURE.md`, "Measured on hardware, both halves (2026-09-20)"](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/FLASHING-PROCEDURE.md#L317-L384).
[^nc]: NayaFlow 1.25.1, NayaCore 6.11.0 strings (pairing and ClearBLEDevices steps and messages, the flash repair and ClearAllData steps, ZMQ events, "one half connected" warnings) and NayaFlow's Danger Zone texts.
[^man-create]: Naya Create User Manual v1.1.0, pp. 4, 5, 11 and 25; see [Manuals](product/manuals.md).
[^man-modules]: Naya Touch, Tune and Track User Manuals v1.1.0, pp. 5 and 7; see [Manuals](product/manuals.md).
[^nx-pr6]: nayactl, [pull request #6](https://github.com/Qonfused/nayactl/pull/6), description by its author.
[^cl]: create-legacy-firmware, [`CHANGELOG.md`](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md) (vendor release notes).
[^cl-222]: create-legacy-firmware, [`CHANGELOG.md` L222](https://github.com/create-collective/create-legacy-firmware/blob/79eeefb/CHANGELOG.md#L222).
[^beta]: Vendor release notes of the beta channel, [NayaTech/NayaFlow-beta-releases](https://github.com/NayaTech/NayaFlow-beta-releases/releases), v1.18.0.

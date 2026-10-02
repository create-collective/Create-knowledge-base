# Open source modules

Homemade modules for the Create's module bays, built in the open: each with its repository, its
build guide, its parts and its firmware. This section is a placeholder for now. The first modules
are in progress, and each gets its own page here when its repository is published. The one thing
to know: nothing is published yet; the links at the end are where the keyboard's side of the
interface is documented today.

!!! note "At a glance"
    - No open source module is published yet (2026-10-02).
    - Each module will get a page with its repository and license, a build guide, and what has been
      tested on which keyboard firmware.
    - What a module has to match on the keyboard's side is already on this site; see
      [the interface a module has to meet](#the-interface-a-module-has-to-meet).

## Modules

None yet. As each module's repository goes public, it is listed here and gets its own page.

## What each module page covers

1. **What it does**: its controls and what it sends to the keyboard.
2. **Repository and license**: where its design files, firmware and source live.
3. **Build guide**: the parts list, printed or machined parts, assembly, and flashing its firmware.
4. **How it fits**: the bay it docks in, how the keyboard identifies it, and its battery and charging.
5. **What was tested**: on which keyboard and module firmware, and what is still open.

## The interface a module has to meet

The stock modules define what the keyboard expects. These pages document it:

- [Module dock](../hardware/dock.md): the bay's mechanics, its contact blocks, and what the dock
  carries.
- [Tune](../hardware/tune.md), [Touch](../hardware/touch.md) and [Track](../hardware/track.md): the
  stock modules' boards and parts.
- [Modules](../protocol/modules.md) and [Module fields](../protocol/module-fields.md): how the
  keyboard identifies a docked module and what it stores for each gesture.
- [Module firmware](../firmware/modules.md): how the stock modules are updated through the keyboard.
- [Power and batteries](../hardware/power.md) and [Battery replacement](../hardware/batteries.md):
  module cells, charging and readings.
- [Parts list](../hardware/parts.md): the stock modules' parts, from the FCC photos.

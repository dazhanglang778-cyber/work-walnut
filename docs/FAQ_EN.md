# Work Walnut FAQ

[中文常见问题](FAQ.md)

## The EXE does nothing when double-clicked

Extract the entire ZIP first and keep `_internal` beside `启动工作坚果.exe`. Do not run it from inside an archive preview or send the EXE by itself.

## Why does the source version report missing `tkinter` or `PIL`?

Use an official Python installation that includes Tcl/Tk, then run `python -m pip install -r requirements.txt`. The Windows Release already bundles these dependencies.

## Why does Windows SmartScreen show a warning?

An unsigned new open-source executable may lack reputation. Download only from the official Release and verify its SHA-256. Do not disable antivirus or system security features.

## Why does macOS say the developer cannot be verified?

The beta is not Apple Developer signed or notarized. Keep Gatekeeper enabled. Verify the Release source and SHA-256, then allow only `工作坚果.app` through Privacy & Security. Include your Mac model, macOS version, and a screenshot when reporting a launch problem.

## Does it track real working time?

No. It only counts time while the pet is running and the computer is awake. It does not inspect keyboard input, mouse input, documents, browsers, or other apps.

## Is the timer saved after closing?

No. Each launch starts healthy. A running instance also resets when the calendar day changes.

## How do I reset immediately?

Right-click the pet and select the reset item. Clicking the final green overlay also resets the cycle.

## Does it support Linux?

Not in v1.0.0. Transparent floating-window behavior differs across X11, Wayland, and desktop environments.

## Can I modify and redistribute it?

Code may be modified and redistributed under GPL-3.0-only. The visual assets are not covered by that GPL grant. You must separately verify artwork rights; replacing them with original or explicitly licensed artwork is safest. See [ASSET_NOTICE.md](../ASSET_NOTICE.md).

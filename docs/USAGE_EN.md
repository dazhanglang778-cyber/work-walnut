# Work Walnut Usage Guide

[中文使用指南](USAGE.md)

## 1. Start

### Windows portable build

1. Download `工作坚果-Windows-x64-v1.0.0.zip` from GitHub Releases.
2. Extract the complete ZIP to a normal folder.
3. Double-click `启动工作坚果.exe`.

Keep the `_internal` folder beside the EXE. Sending or copying the EXE alone will prevent the app from starting.

### macOS beta

Download `工作坚果-macOS-arm64-v1.0.0.zip` for Apple Silicon or `工作坚果-macOS-x64-v1.0.0.zip` for Intel. Extract and open `工作坚果.app`.

The beta is unsigned and unnotarized. Keep Gatekeeper enabled. Only allow this individual app after verifying the official Release source and SHA-256.

### Source version

1. Install Python 3.10 or later with Tkinter.
2. Run `python -m pip install -r requirements.txt`.
3. Run `python app/wallnut_pet.py`.

## 2. Controls

| Input | Action |
|---|---|
| Left click | Play a small bounce |
| Left-button drag | Move the pet to a screen edge |
| Left double-click | Roll twice toward the screen interior |
| Right click | Open the menu |
| Right double-click | Launch diagonally and bounce off usable screen edges |
| Click a speech bubble | Dismiss the bubble |
| Click the final green overlay | Return to healthy and restart the timer |

On a Mac trackpad, use a two-finger secondary click or Control-click for right-click actions.

## 3. State cycle

| Start time | State |
|---:|---|
| 0 minutes | Healthy |
| 45 minutes | Lightly hurt |
| 90 minutes | Hurt |
| 135 minutes | Pirate Tall-nut |
| 180 minutes | Critical Tall-nut |
| 225 minutes | Crazy |
| 270 minutes | Red-hot |
| 315 minutes | Random green overlay; click to reset |

The timer only measures time while the app is running and the computer is awake. It does not inspect keyboard input, mouse activity, or applications. Closing the app or crossing into a new calendar day resets the cycle.

## 4. Configuration

Settings are stored in `app/config.json`. They control pet size, wobble intervals, roll distance, launch physics, fatigue thresholds, and macOS safe margins. Keep valid JSON syntax and make a backup before editing.

## 5. Exit and uninstall

Right-click the pet and choose the exit item. The portable build installs no service or uninstaller; after exiting, delete the extracted folder to remove it.

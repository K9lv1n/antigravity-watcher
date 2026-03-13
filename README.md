# Antigravity Watcher

**Automatically brings Antigravity IDE back into focus — maximised and front and centre — the moment your prompt finishes. Browse freely while you wait.**

---

## What it does

1. You type a prompt in Antigravity IDE and hit submit
2. You press Enter in the terminal to start watching
3. You switch to your browser and do whatever you want
4. The moment Antigravity finishes — your screen snaps back to it, full screen

No more tab-switching to check if it's done. It comes to you.

---

## How it works

Uses Windows' `PrintWindow` API to capture Antigravity's pixels **even when it is hidden behind your browser**. It compares those pixels against a template image you capture once (the "done" state of Antigravity). When they match, it uses `AttachThreadInput` + `SetForegroundWindow` to force-focus the window — bypassing Windows' foreground lock that normally blocks background apps from stealing focus.

---

## Requirements

- Windows 10 or 11
- Python 3.10 or higher
- Antigravity IDE installed and open

---

## Installation

### Step 1 — Install Python

1. Go to **https://www.python.org/downloads/**
2. Click the big Download button
3. ⚠️ On the first install screen, tick **"Add Python to PATH"** before clicking anything else
4. Click Install Now

### Step 2 — Download this repo

Click the green **Code** button on this GitHub page → **Download ZIP** → unzip it somewhere easy like your Desktop.

Or if you have Git installed:
```bash
git clone https://github.com/YOUR_USERNAME/antigravity-watcher.git
cd antigravity-watcher
```

### Step 3 — Install dependencies

Open Command Prompt (press Windows key, type `cmd`, press Enter) and run:

```bash
pip install Pillow pygetwindow pyautogui opencv-python
```

---

## Setup (one time only)

**Make sure Antigravity IDE is open and showing its "done" state** (a finished prompt, not mid-generation).

Run:
```bash
python antigravity_watcher.py --capture-done
```

What happens:
1. Press Enter in the terminal
2. You get 5 seconds to switch to Antigravity — do it now
3. A darkened overlay appears over your screen showing a crosshair
4. Drag a box around the element that only appears when Antigravity is **truly done** — good choices are:
   - The send/submit button reappearing
   - A checkmark or tick icon
   - The input box becoming active again
   - Any UI element that is absent during generation
5. Release — the template saves automatically as `done_template.png`

> **Tip:** Capture something small and distinctive. Avoid the output text area since it changes every run.

---

## Usage (every time)

```bash
python antigravity_watcher.py
```

**The flow:**
```
Step 1 → Type your prompt in Antigravity and hit submit
Step 2 → Come back to the terminal and press Enter
Step 3 → Switch to your browser and do whatever you want
Step 4 → Antigravity pops back up full screen when done
Step 5 → Press Enter in terminal again for your next prompt
```

---

## All commands

```bash
# Normal use
python antigravity_watcher.py

# With a sound alert when done
python antigravity_watcher.py --sound

# One-time setup — capture your done template
python antigravity_watcher.py --capture-done

# See all open window titles (to find the right --window name)
python antigravity_watcher.py --list-windows

# If your Antigravity window has a different title
python antigravity_watcher.py --window "Antigravity IDE"

# Adjust match sensitivity (default 0.85, lower = easier to match)
python antigravity_watcher.py --confidence 0.75
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python is not recognized` | Reinstall Python and tick **"Add Python to PATH"** on the first screen |
| `No template found` | Run `--capture-done` first |
| Template never matches | Run `--capture-done` again, capture a larger or more distinctive element. Try `--confidence 0.75` |
| Window not found at startup | Make sure Antigravity is open before running the script |
| Doesn't switch back to Antigravity | The window handle was lost — restart the script with Antigravity already open |

---

## How the focus switch works (technical)

Windows normally blocks background processes from calling `SetForegroundWindow` — this is why most focus scripts silently fail. This script uses the known workaround:

1. `AttachThreadInput` — attaches Python's thread to the browser's input queue, making Windows treat Python as part of the active app
2. A simulated `Alt` keypress — grants foreground permission
3. `ShowWindow(SW_MAXIMIZE)` — restores and maximises Antigravity
4. `SetForegroundWindow` + `BringWindowToTop` + `SetFocus` — brings it to front

The window is identified by its HWND (a unique Windows handle) locked at startup — not by title — so VS Code or any other window with "antigravity" in its title bar never gets matched by accident.

---

## License

MIT — free to use, modify, and share.
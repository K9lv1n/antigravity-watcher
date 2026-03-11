# 🚀 Antigravity Watcher

**Automatically brings Antigravity IDE back into focus the moment your prompt finishes — so you can freely browse the web while you wait.**

---

## What does this do?

You type a prompt in Antigravity IDE and hit submit.  
You switch to your browser and do other things.  
The moment Antigravity finishes generating — your screen snaps back to it automatically.  

No more switching back and forth to check if it's done. No more missing when a response finishes. Just work, and it comes back to you.

---

## How it works

The script takes a screenshot of your Antigravity window every second and generates a pixel fingerprint (MD5 hash). When you submit a prompt, the screen starts changing — that's the signal that Antigravity is working. When the screen stops changing for several seconds in a row, the script knows the response is done. It then uses OS-level commands to bring the Antigravity window to the front of your screen, even if your browser is covering it.

**No browser extension needed. Works with any browser. Works on Windows, Mac, and Linux.**

---

## Requirements

- Python 3.10 or higher
- Antigravity IDE installed and open
- 5 minutes to set up

---

## Installation

### Step 1 — Clone or download this repo

```bash
git clone https://github.com/YOUR_USERNAME/antigravity-watcher.git
cd antigravity-watcher
```

Or click the green **Code** button on GitHub → **Download ZIP** → unzip it.

---

### Step 2 — Install Python libraries

**Windows:**
```bash
pip install Pillow pygetwindow pyautogui
```

**Mac:**
```bash
pip3 install Pillow pygetwindow pyautogui
```

**Linux:**
```bash
pip3 install Pillow pyautogui
sudo apt install wmctrl xdotool
```

---

### Step 3 — Find your Antigravity window name

Run this to see all open windows on your computer:

```bash
python antigravity_watcher.py --list-windows
```

Look for your Antigravity IDE in the list. The script automatically searches for any window containing the word `Antigravity`, so in most cases you don't need to change anything.

---

### Step 4 — Run the watcher

Make sure Antigravity IDE is open first, then:

```bash
python antigravity_watcher.py
```

That's it. Now type your prompt in Antigravity, switch to your browser, and wait.

---

## Usage

```bash
# Basic usage
python antigravity_watcher.py

# With a sound alert when done
python antigravity_watcher.py --sound

# If your window title is different from "Antigravity"
python antigravity_watcher.py --window "Antigravity IDE"

# See all open windows to find the right name
python antigravity_watcher.py --list-windows

# Wait longer before switching (for slower machines or longer responses)
python antigravity_watcher.py --stable 6
```

---

## Auto-start on login (run it once, forget about it)

### Windows — Task Scheduler

1. Press Windows key → search **Task Scheduler** → open it
2. Click **Create Basic Task** on the right
3. Name: `Antigravity Watcher` → click Next
4. Trigger: **When I log on** → Next
5. Action: **Start a program** → Next
6. Program/script: `python`
7. Add arguments: `C:\Users\YOUR_USERNAME\Documents\antigravity-watcher\antigravity_watcher.py`
8. Finish

### Mac — Login Items

1. Apple menu → System Settings → General → Login Items
2. Create a file called `start_watcher.command` with:
   ```bash
   #!/bin/bash
   cd /Users/YOUR_USERNAME/Documents/antigravity-watcher
   python3 antigravity_watcher.py
   ```
3. Make it executable: `chmod +x start_watcher.command`
4. Add it to Login Items

### Linux — Startup Applications

1. Open Startup Applications
2. Click Add
3. Command: `python3 /home/YOUR_USERNAME/Documents/antigravity-watcher/antigravity_watcher.py`
4. Save

---

## What you'll see when it runs

```
🚀 Antigravity Watcher Started
   Looking for window : 'Antigravity'
   Platform           : Windows

✅ Found window at rect: (0, 0, 1920, 1080)

⏳ Watching for you to submit a prompt...
   (Type your prompt in Antigravity and hit Enter/Submit)

🟡 Activity detected — Antigravity is working...

   ✈  You can switch to your browser now.

   Still... (1/4)
   Still... (2/4)
   Still... (3/4)
   Still... (4/4)

✅ Response complete! Switching back to Antigravity...

🎉 Done! Antigravity is now in focus.
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python is not recognized` | Reinstall Python and tick **"Add Python to PATH"** on the first screen |
| `Window not found` | Make sure Antigravity is open, then run `--list-windows` to find the exact title |
| Switches too fast | Use `--stable 6` to wait 6 seconds of stability before switching |
| Window doesn't come to front on Mac | System Settings → Privacy & Security → Accessibility → enable Terminal |
| Window doesn't come to front on Linux | Run `sudo apt install wmctrl xdotool` |
| Script crashes | Make sure Antigravity stays open while the script runs |

---

## How the detection works (technical)

The script uses **pixel fingerprinting** — it takes a cropped screenshot of just the Antigravity window, resizes it to a 200×150 thumbnail (to ignore tiny cursor blinks), and computes an MD5 hash. If the hash changes, the screen is changing. If the hash stays the same for `N` consecutive polls (default: 4, meaning 4 seconds), the response is declared done. This approach works universally across any IDE or app without needing API access or browser plugins.

---

## Contributing

Pull requests are welcome. If your version of Antigravity uses a different window title or has a feature like a visible loading spinner, open an issue and share the details — the script can be extended to use DOM-level detection if needed.

---

## License

MIT — free to use, modify, and share.

---

## Author

Built to scratch a personal itch — never stare at a loading screen again.

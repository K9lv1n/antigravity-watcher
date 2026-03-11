# FULL SETUP GUIDE — Antigravity Watcher
### Written for complete beginners. Every single step is explained.

---

## WHAT THIS DOES

You type a prompt in Antigravity IDE and hit submit.  
You switch to your browser and do other things.  
When Antigravity finishes — your screen automatically jumps back to Antigravity.  
You don't have to keep checking. It tells you when it's done.

---

## BEFORE YOU START — What you need

- A computer running Windows, Mac, or Linux
- Antigravity IDE installed and working
- An internet connection (just for the setup steps)
- About 15 minutes

---

## PART 1 — INSTALL PYTHON

Python is the language the script is written in. You need it installed first.

### Windows:
1. Open your browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Open the downloaded file
4. ⚠️ **IMPORTANT** — On the very first screen, tick the box that says **"Add Python to PATH"** at the bottom before clicking anything else
5. Click **"Install Now"**
6. Wait for it to finish, then click **Close**

### Mac:
1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Open the downloaded `.pkg` file
4. Click **Continue** through all the steps, then **Install**
5. Type your Mac password if it asks

### Linux:
Open Terminal and type this, then press Enter:
```
sudo apt install python3 python3-pip
```
Type your password and press Enter when asked.

---

## PART 2 — CHECK PYTHON IS WORKING

1. On **Windows**: Press the Windows key, type `cmd`, press Enter. This opens a black window called Command Prompt.
   On **Mac**: Press `Cmd + Space`, type `Terminal`, press Enter.
   On **Linux**: Press `Ctrl + Alt + T`.

2. In that black/white window, type exactly this and press Enter:
```
python --version
```

3. You should see something like: `Python 3.12.0`
   If you see that — ✅ Python is working. Move to Part 3.
   If you see an error — try typing `python3 --version` instead.

---

## PART 3 — INSTALL THE REQUIRED LIBRARIES

Libraries are extra tools Python needs to run the script.

In the same Command Prompt / Terminal window, type this and press Enter:

**Windows:**
```
pip install Pillow pygetwindow pyautogui
```

**Mac:**
```
pip3 install Pillow pygetwindow pyautogui
```

**Linux:**
```
pip3 install Pillow pyautogui
sudo apt install wmctrl xdotool
```

You will see a lot of text scrolling — that is normal. Wait until it stops and you see a `>` cursor again.

---

## PART 4 — CREATE A FOLDER FOR THE PROJECT

This keeps everything organised in one place.

### Windows:
1. Open **File Explorer** (the folder icon on your taskbar)
2. Click on your **Documents** folder on the left
3. Right-click in the empty space → **New** → **Folder**
4. Name it: `antigravity-watcher`

### Mac:
1. Open **Finder**
2. Click **Documents** on the left
3. Right-click in the empty space → **New Folder**
4. Name it: `antigravity-watcher`

### Linux:
In Terminal, type:
```
mkdir ~/Documents/antigravity-watcher
```

---

## PART 5 — INSTALL VS CODE (if you don't have it)

VS Code is where you will put the script file. It is free.

1. Go to: **https://code.visualstudio.com/**
2. Click the big **Download** button for your OS
3. Open the downloaded file and install it (click Next/Continue through everything)
4. Open VS Code when done

---

## PART 6 — OPEN YOUR FOLDER IN VS CODE

1. Open VS Code
2. Click **File** in the top menu → **Open Folder**
3. Navigate to your **Documents** folder → click `antigravity-watcher` → click **Select Folder** (Windows) or **Open** (Mac)
4. You will see your empty folder appear in the left panel of VS Code

---

## PART 7 — CREATE THE SCRIPT FILE IN VS CODE

1. In VS Code, look at the left panel — you will see `ANTIGRAVITY-WATCHER` at the top
2. Click the **New File** icon (it looks like a page with a + sign) next to that folder name
3. Name the file: `antigravity_watcher.py` (make sure you include the `.py` at the end)
4. Press Enter

5. Now paste the script code into that empty file
   - Click inside the file area (the big empty white/dark space on the right)
   - Press `Ctrl+A` to select all (in case there's anything there)
   - Then paste the code with `Ctrl+V`

6. Press `Ctrl+S` to save

The file should now show `antigravity_watcher.py` in the left panel.

---

## PART 8 — OPEN THE TERMINAL INSIDE VS CODE

You don't need to leave VS Code to run the script. VS Code has a built-in terminal.

1. Press `` Ctrl+` `` (that's the backtick key, to the left of the 1 key on your keyboard)
   Or click **Terminal** in the top menu → **New Terminal**

2. A panel will appear at the bottom of VS Code. This is your terminal.

3. Type this and press Enter to go to your folder:
   **Windows:** `cd Documents\antigravity-watcher`
   **Mac/Linux:** `cd ~/Documents/antigravity-watcher`

---

## PART 9 — FIND YOUR ANTIGRAVITY WINDOW NAME

The script needs to know the exact name of your Antigravity IDE window.

In the VS Code terminal, type this and press Enter:

**Windows/Linux:**
```
python antigravity_watcher.py --list-windows
```
**Mac:**
```
python3 antigravity_watcher.py --list-windows
```

You will see a list like:
```
── Open Windows ──────────────────────────────────
  'Antigravity - my-project'
  'Google Chrome'
  'Visual Studio Code'
──────────────────────────────────────────────────
```

Look for anything that says **Antigravity** in the list. Write down exactly what it says.

If it says `Antigravity` or `Antigravity IDE` — you don't need to change anything.
If it says something different like `AG Studio` — you will need to use `--window "AG Studio"` when you run the script (see Part 10).

---

## PART 10 — RUN THE SCRIPT

Make sure Antigravity IDE is open first.

In the VS Code terminal, type:

**Windows:**
```
python antigravity_watcher.py
```

**Mac/Linux:**
```
python3 antigravity_watcher.py
```

You will see:
```
🚀 Antigravity Watcher Started
   Looking for window : 'Antigravity'

✅ Found window at rect: (0, 0, 1920, 1080)

⏳ Watching for you to submit a prompt...
   (Type your prompt in Antigravity and hit Enter/Submit)
```

**The script is now running and watching.**

---

## PART 11 — USE IT

1. Switch to Antigravity IDE
2. Type your prompt and hit submit
3. Immediately switch to your browser — do whatever you want
4. When the script detects the response is done, it will:
   - Snap your screen back to Antigravity
   - Play a sound (if you used `--sound`)
   - Show a notification

5. To run again for your next prompt, go back to the terminal and press the **Up arrow** key to get the last command, then press Enter.

---

## PART 12 — MAKE IT START AUTOMATICALLY (so you never have to think about it)

---

### WINDOWS — Task Scheduler

This makes the script run automatically every time you turn on your computer.

1. Press the **Windows key** on your keyboard
2. Type `Task Scheduler` and press Enter
3. On the right side, click **"Create Basic Task..."**
4. **Name:** Type `Antigravity Watcher` → click **Next**
5. **Trigger:** Select `When I log on` → click **Next**
6. **Action:** Select `Start a program` → click **Next**
7. **Program/script:** Type `python`
8. **Add arguments:** Type the full path to your script. Replace YOUR_USERNAME with your actual Windows username:
   ```
   C:\Users\YOUR_USERNAME\Documents\antigravity-watcher\antigravity_watcher.py
   ```
   To find your username: open Command Prompt and type `whoami`
9. Click **Next** → click **Finish**
10. ✅ Done. It will now start automatically every time you log in.

To test it worked: restart your computer, and once logged in, open Antigravity IDE — the watcher should already be running in the background.

---

### MAC — Login Items

1. Click the **Apple menu** (🍎) in the top left → **System Settings** (or System Preferences on older Macs)
2. Click **General** → **Login Items**
3. Click the **+** button under "Open at Login"
4. You need to add a small helper file. First, create it:
   - Open VS Code
   - Create a new file called `start_watcher.command` in your `antigravity-watcher` folder
   - Paste this into it (replace YOUR_USERNAME with your actual Mac username):
   ```bash
   #!/bin/bash
   cd /Users/YOUR_USERNAME/Documents/antigravity-watcher
   python3 antigravity_watcher.py
   ```
   - Save it
5. In Terminal, make it executable:
   ```
   chmod +x ~/Documents/antigravity-watcher/start_watcher.command
   ```
6. Go back to Login Items and click **+** → navigate to your `antigravity-watcher` folder → select `start_watcher.command` → click **Open**
7. ✅ Done. It will now start automatically when you log into your Mac.

---

### LINUX — Startup Applications

1. Open **Startup Applications** from your apps menu (or search for it)
2. Click **Add**
3. Fill in:
   - **Name:** `Antigravity Watcher`
   - **Command:** `python3 /home/YOUR_USERNAME/Documents/antigravity-watcher/antigravity_watcher.py`
   - **Comment:** `Auto-focus Antigravity when prompt is done`
4. Click **Add** / **Save**
5. ✅ Done.

---

## TROUBLESHOOTING

**"python is not recognized" error on Windows:**
→ Python was not added to PATH during install.
→ Uninstall Python and reinstall it — this time tick "Add Python to PATH" on the first screen.

**Script says "window not found":**
→ Make sure Antigravity IDE is open before running the script.
→ Run `python antigravity_watcher.py --list-windows` and find the exact window name.
→ Use `--window "exact name here"` when running the script.

**Script detects "done" too quickly / too slowly:**
→ Use `--stable 6` to wait longer (6 stable seconds), or `--stable 2` to wait less.

**Window doesn't come to front (stays behind browser):**
→ Windows: Make sure you didn't deny the focus permission. Try right-clicking the script in Task Scheduler → Run.
→ Mac: Go to System Settings → Privacy & Security → Accessibility → enable Terminal or VS Code.
→ Linux: Install wmctrl: `sudo apt install wmctrl xdotool`

**Script crashes when I'm not at my computer:**
→ Add `--stable 8` to give it more time to stabilize before declaring done.

---

## QUICK REFERENCE — Commands

```bash
# Basic run
python antigravity_watcher.py

# Run with sound alert
python antigravity_watcher.py --sound

# If your window has a different name
python antigravity_watcher.py --window "Antigravity IDE"

# See all open windows (to find the right name)
python antigravity_watcher.py --list-windows

# Wait longer before switching (useful for slow responses)
python antigravity_watcher.py --stable 6
```

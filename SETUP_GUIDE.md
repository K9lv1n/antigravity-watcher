# FULL SETUP GUIDE — Antigravity Watcher
### Written for complete beginners. Every single step is explained.

---

## WHAT THIS DOES

You type a prompt in Antigravity IDE and hit submit.
You switch to your browser and do other things.
When Antigravity finishes — your screen automatically jumps back to Antigravity, full screen.
You don't have to keep checking. It comes to you.

---

## BEFORE YOU START — What you need

- A computer running Windows 10 or 11
- Antigravity IDE installed and working
- An internet connection (just for the setup steps)
- About 15 minutes

---

## PART 1 — INSTALL PYTHON

Python is the language the script is written in. You need it installed first.

1. Open your browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Open the downloaded file
4. ⚠️ **IMPORTANT** — On the very first screen, tick the box that says **"Add Python to PATH"** at the bottom before clicking anything else
5. Click **"Install Now"**
6. Wait for it to finish, then click **Close**

---

## PART 2 — CHECK PYTHON IS WORKING

1. Press the Windows key, type `cmd`, press Enter — this opens Command Prompt (a black window)
2. Type exactly this and press Enter:
```
python --version
```
3. You should see something like: `Python 3.12.0`
   If you see that — ✅ Python is working. Move to Part 3.
   If you see an error — uninstall Python and reinstall it, making sure to tick "Add Python to PATH"

---

## PART 3 — INSTALL THE REQUIRED LIBRARIES

Libraries are extra tools Python needs to run the script.

In Command Prompt, type this and press Enter:
```
pip install Pillow pygetwindow pyautogui opencv-python
```

You will see a lot of text scrolling — that is normal. Wait until it stops and you see a `>` cursor again.

---

## PART 4 — CREATE A FOLDER FOR THE PROJECT

1. Open **File Explorer** (the folder icon on your taskbar)
2. Click on your **Desktop** or **Documents** folder on the left
3. Right-click in the empty space → **New** → **Folder**
4. Name it: `antigravity-watcher`

---

## PART 5 — INSTALL VS CODE (if you don't have it)

VS Code is a free code editor where you will keep the script.

1. Go to: **https://code.visualstudio.com/**
2. Click the big **Download** button
3. Open the downloaded file and install it (click Next through everything)
4. Open VS Code when done

---

## PART 6 — OPEN YOUR FOLDER IN VS CODE

1. Open VS Code
2. Click **File** in the top menu → **Open Folder**
3. Navigate to where you made `antigravity-watcher` → click it → click **Select Folder**
4. You will see your empty folder appear in the left panel

---

## PART 7 — CREATE THE SCRIPT FILE IN VS CODE

1. In VS Code, look at the left panel — you will see `ANTIGRAVITY-WATCHER` at the top
2. Click the **New File** icon (page with a + sign) next to that folder name
3. Name the file: `antigravity_watcher.py` (include the `.py` at the end)
4. Press Enter
5. Paste the script code into that empty file:
   - Click inside the big empty space on the right
   - Press `Ctrl+A` to select all
   - Paste the code with `Ctrl+V`
6. Press `Ctrl+S` to save

---

## PART 8 — OPEN THE TERMINAL INSIDE VS CODE

1. Press `` Ctrl+` `` (the backtick key, left of the 1 key)
   Or click **Terminal** in the top menu → **New Terminal**
2. A panel appears at the bottom — this is your terminal
3. Navigate to your folder by typing and pressing Enter:
```
cd Desktop\antigravity-watcher
```
(or `cd Documents\antigravity-watcher` if you put it there)

---

## PART 9 — ONE-TIME SETUP: CAPTURE YOUR "DONE" TEMPLATE

This is the most important step. You are teaching the script what Antigravity looks like when it has **truly finished** a prompt.

**Before doing this:**
- Open Antigravity IDE
- Run a prompt and wait for it to fully finish
- Leave it showing the completed/done state — do NOT start a new prompt

In the VS Code terminal, type:
```
python antigravity_watcher.py --capture-done
```

**What happens next:**
1. Read the instructions in the terminal
2. Press Enter
3. You have **5 seconds** to click on Antigravity in your taskbar — do it quickly
4. Your screen goes dark with a crosshair cursor
5. Drag a box around the element that shows Antigravity is done

**What to drag around (pick ONE small thing):**
- The send/submit button (it disappears while generating, reappears when done)
- A checkmark or tick icon that appears when done
- The text input box becoming active/usable again
- Any small UI element that is ABSENT while generating and APPEARS when done

**Do NOT drag around:**
- The whole screen
- The output/response text (it changes every time)
- Anything that moves or changes during generation

6. Release the mouse — the overlay closes and saves `done_template.png` automatically
7. The terminal will say if the template was verified successfully

---

## PART 10 — CHECK YOUR WINDOW NAME

In the VS Code terminal, type:
```
python antigravity_watcher.py --list-windows
```

You will see something like:
```
-- All Open Windows ------------------------------------------
  'Antigravity - my-project'
  'Google Chrome'
  'Visual Studio Code - antigravity_watcher.py'
--------------------------------------------------------------
```

Look for the Antigravity window. If it contains the word `Antigravity` you don't need to change anything. If it shows a completely different name like `AG Studio`, note it down — you'll need `--window "AG Studio"` when running.

---

## PART 11 — RUN THE SCRIPT

Make sure Antigravity IDE is already open before running.

```
python antigravity_watcher.py
```

You will see:
```
+------------------------------------------+
|   ANTIGRAVITY WATCHER  v4                |
|   Template Matching Edition              |
+------------------------------------------+

  Antigravity window handle locked: 12345678

==================================================
  STEP 1 → Type your prompt in Antigravity IDE
  STEP 2 → Hit submit
  STEP 3 → Come back here and press Enter
==================================================
```

---

## PART 12 — USE IT (every time)

```
1. Type your prompt in Antigravity and hit submit
2. Come back to the VS Code terminal and press Enter
3. Switch to your browser — do whatever you want
4. Antigravity pops back up full screen when the prompt finishes
5. Press Enter in the terminal again for your next prompt
```

---

## PART 13 — MAKE IT START AUTOMATICALLY

This makes the script start every time you log into Windows so you never have to run it manually.

1. Press the **Windows key** on your keyboard
2. Type `Task Scheduler` and press Enter
3. On the right side, click **"Create Basic Task..."**
4. **Name:** Type `Antigravity Watcher` → click **Next**
5. **Trigger:** Select `When I log on` → click **Next**
6. **Action:** Select `Start a program` → click **Next**
7. **Program/script box:** type exactly:
   ```
   python
   ```
8. **Add arguments box:** type the full path to your script:
   ```
   C:\Users\YOUR_USERNAME\Desktop\antigravity-watcher\antigravity_watcher.py
   ```
   To find your username: open Command Prompt and type `whoami` — it shows `COMPUTER\username`, use the part after the backslash.

   Easiest way to get the exact path: right-click `antigravity_watcher.py` in VS Code's left panel → **Copy Path** → paste it here.

9. Click **Next** → click **Finish**
10. ✅ Done. It will now start automatically every time you log in.

---

## TROUBLESHOOTING

**"python is not recognized"**
→ Python was not added to PATH. Uninstall and reinstall it — tick "Add Python to PATH" on the first screen.

**"No template found"**
→ You haven't run `--capture-done` yet. Do Part 9 first.

**Template never matches / script watches forever**
→ Run `--capture-done` again and pick a more distinctive element — something small and unique that only appears when truly done.
→ Try lowering confidence: `python antigravity_watcher.py --confidence 0.75`

**"Window not found" at startup**
→ Antigravity must be open before you run the script. Open it first, then run the script.

**Script says it found a match but wrong window comes up**
→ Restart both Antigravity and the script. The window handle is locked at startup so Antigravity must be open first.

**Window comes up but is not full screen**
→ This is fixed in the latest version. Make sure you have the newest `antigravity_watcher.py`.

---

## QUICK REFERENCE — All commands

```bash
# Normal use
python antigravity_watcher.py

# With a sound alert when done
python antigravity_watcher.py --sound

# One-time setup — capture your done template (redo if Antigravity UI changes)
python antigravity_watcher.py --capture-done

# See all open window titles
python antigravity_watcher.py --list-windows

# If your Antigravity window has a different title
python antigravity_watcher.py --window "Antigravity IDE"

# Lower the match sensitivity if template never triggers
python antigravity_watcher.py --confidence 0.75
```

---

## UPDATING ON GITHUB

After making any changes to your files, open the VS Code terminal and run:

```bash
git add .
git commit -m "describe what you changed"
git push
```

Your GitHub page will update instantly.

If this is your first time pushing to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/antigravity-watcher.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. You can find this by logging into github.com and looking at the top right corner.
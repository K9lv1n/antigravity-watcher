"""
antigravity_watcher.py  v3 — Region Picker Edition
====================================================
Instead of watching the whole screen (which causes false "still generating"
forever), you drag a small box around just the spinner/stop-button area in
Antigravity. That tiny region has almost zero noise, so done-detection is
instant and reliable.

INSTALL (run once in terminal):
  pip install Pillow pygetwindow pyautogui

Linux extra:
  sudo apt install wmctrl xdotool python3-tk

USAGE:
  python antigravity_watcher.py          <- normal use
  python antigravity_watcher.py --sound  <- with sound alert
  python antigravity_watcher.py --list-windows
"""

import sys, time, subprocess, platform, hashlib, io, argparse, threading
import tkinter as tk
from PIL import ImageGrab, Image, ImageTk

WINDOW_NAME   = "Antigravity"
POLL_INTERVAL = 0.8
STABLE_COUNT  = 6    # 6 x 0.8s = ~5 stable seconds = done
SWITCH_DELAY  = 0.3


# ──────────────────────────────────────────────────────────────────
# REGION PICKER
# A fullscreen semi-transparent overlay. Click and drag to select
# the small area you want to watch (e.g. the stop button / spinner).
# ──────────────────────────────────────────────────────────────────

class RegionPicker:
    """Shows a fullscreen overlay. User drags a rectangle. Returns (x1,y1,x2,y2)."""

    def __init__(self):
        self.result = None
        self._start = None

    def pick(self):
        # Take a screenshot to use as background
        screen = ImageGrab.grab()

        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-alpha", 0.35)
        root.configure(bg="black")
        root.attributes("-topmost", True)
        root.title("Select region")

        # Show the screenshot as background
        screen_tk = ImageTk.PhotoImage(screen)
        bg_label = tk.Label(root, image=screen_tk, bd=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Canvas for the selection rectangle
        canvas = tk.Canvas(root, cursor="cross", highlightthickness=0, bg="black")
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

        rect_id = [None]
        start   = [0, 0]

        # Instruction label
        lbl = tk.Label(
            root,
            text="  Click and drag around the spinner / stop button in Antigravity,\n"
                 "  then release. Press Escape to cancel.  ",
            font=("Arial", 14, "bold"),
            fg="white", bg="#1a1a2e",
            pady=10, padx=20
        )
        lbl.place(relx=0.5, rely=0.04, anchor="center")

        def on_press(e):
            start[0], start[1] = e.x, e.y
            if rect_id[0]:
                canvas.delete(rect_id[0])

        def on_drag(e):
            if rect_id[0]:
                canvas.delete(rect_id[0])
            rect_id[0] = canvas.create_rectangle(
                start[0], start[1], e.x, e.y,
                outline="#00ff88", width=3,
                fill="#00ff88", stipple="gray25"
            )

        def on_release(e):
            x1, y1 = min(start[0], e.x), min(start[1], e.y)
            x2, y2 = max(start[0], e.x), max(start[1], e.y)
            if (x2 - x1) > 10 and (y2 - y1) > 10:
                self.result = (x1, y1, x2, y2)
            root.destroy()

        def on_escape(e):
            root.destroy()

        canvas.bind("<ButtonPress-1>",   on_press)
        canvas.bind("<B1-Motion>",       on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        root.bind("<Escape>",            on_escape)

        root.mainloop()
        return self.result


# ──────────────────────────────────────────────────────────────────
# WINDOW UTILITIES
# ──────────────────────────────────────────────────────────────────

def list_all_windows():
    os_name = platform.system()
    print("\n-- All Open Windows ------------------------------------------")
    if os_name == "Windows":
        try:
            import pygetwindow as gw
            for w in gw.getAllWindows():
                if w.title.strip():
                    print(f"  '{w.title}'")
        except Exception as e:
            print(f"  Error: {e}")
    elif os_name == "Darwin":
        script = '''
        tell application "System Events"
            set out to {}
            repeat with p in (every process whose background only is false)
                try
                    repeat with w in (every window of p)
                        set end of out to (name of p) & " -> " & (name of w)
                    end repeat
                end try
            end repeat
            return out
        end tell
        '''
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        for line in r.stdout.strip().split(", "):
            print(f"  {line.strip()}")
    elif os_name == "Linux":
        r = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
        for line in r.stdout.strip().split("\n"):
            print(f"  {line}")
    print("--------------------------------------------------------------\n")


# ──────────────────────────────────────────────────────────────────
# WINDOW FOCUS  (3-method fallback chain)
# ──────────────────────────────────────────────────────────────────

def bring_to_front(name: str):
    os_name = platform.system()
    print(f"\n  [focus] Bringing '{name}' to front...")

    if os_name == "Windows":
        # Method 1 — pygetwindow minimize+restore+activate
        try:
            import pygetwindow as gw
            matches = [w for w in gw.getAllWindows() if name.lower() in w.title.lower()]
            if matches:
                w = matches[0]
                w.minimize(); time.sleep(0.15); w.restore(); time.sleep(0.1); w.activate()
                print("  [focus] pygetwindow: OK"); return
        except Exception as e:
            print(f"  [focus] pygetwindow failed: {e}")

        # Method 2 — PowerShell AppActivate
        try:
            ps = f"(New-Object -ComObject WScript.Shell).AppActivate('{name}')"
            subprocess.run(["powershell", "-Command", ps],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("  [focus] PowerShell: fired")
        except Exception as e:
            print(f"  [focus] PowerShell failed: {e}")

        # Method 3 — click the centre of the window
        try:
            import pygetwindow as gw
            matches = [w for w in gw.getAllWindows() if name.lower() in w.title.lower()]
            if matches:
                import pyautogui
                w = matches[0]
                pyautogui.click((w.left + w.right)//2, (w.top + w.bottom)//2)
                print("  [focus] pyautogui click: OK")
        except Exception as e:
            print(f"  [focus] pyautogui failed: {e}")

    elif os_name == "Darwin":
        script = f'''
        tell application "System Events"
            repeat with p in (every process whose background only is false)
                if (name of p) contains "{name}" then
                    set frontmost of p to true
                    return "ok"
                end if
            end repeat
        end tell
        '''
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if "ok" in r.stdout:
            print("  [focus] AppleScript: OK"); return
        subprocess.run(["osascript", "-e", f'tell application "{name}" to activate'],
                       capture_output=True)
        print("  [focus] AppleScript activate: fired")

    elif os_name == "Linux":
        subprocess.run(["wmctrl", "-a", name], capture_output=True)
        subprocess.run(["xdotool", "search", "--name", name,
                        "windowactivate", "--sync"], capture_output=True)
        r = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
        for line in r.stdout.strip().split("\n"):
            if name.lower() in line.lower():
                subprocess.run(["wmctrl", "-i", "-a", line.split()[0]], check=False)
                break
        print("  [focus] wmctrl + xdotool: fired")


# ──────────────────────────────────────────────────────────────────
# SCREENSHOT HASH
# ──────────────────────────────────────────────────────────────────

def region_hash(rect) -> str:
    """Hash only the selected rectangle — fast and noise-free."""
    img = ImageGrab.grab(bbox=rect)
    img = img.resize((80, 60), Image.LANCZOS)   # tiny thumbnail
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()


# ──────────────────────────────────────────────────────────────────
# ALERTS
# ──────────────────────────────────────────────────────────────────

def play_alert():
    try:
        if platform.system() == "Darwin":
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif platform.system() == "Windows":
            import winsound; winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            subprocess.run(["paplay",
                "/usr/share/sounds/freedesktop/stereo/complete.oga"], capture_output=True)
    except Exception:
        print("\a", end="", flush=True)


def send_notification(msg: str):
    try:
        if platform.system() == "Darwin":
            subprocess.run(["osascript", "-e",
                f'display notification "{msg}" with title "Antigravity Done"'])
        elif platform.system() == "Linux":
            subprocess.run(["notify-send", "Antigravity Done", msg])
        elif platform.system() == "Windows":
            ps = (
                "[Windows.UI.Notifications.ToastNotificationManager,"
                "Windows.UI.Notifications,ContentType=WindowsRuntime]|Out-Null;"
                "$t=[Windows.UI.Notifications.ToastNotificationManager]::"
                "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText01);"
                f"$t.GetElementsByTagName('text')[0].AppendChild($t.CreateTextNode('{msg}'))|Out-Null;"
                "$n=[Windows.UI.Notifications.ToastNotification]::new($t);"
                "[Windows.UI.Notifications.ToastNotificationManager]::"
                "CreateToastNotifier('Antigravity').Show($n);"
            )
            subprocess.run(["powershell","-Command",ps], capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────
# MAIN WATCH LOOP
# ──────────────────────────────────────────────────────────────────

def watch_region(rect, stable: int) -> bool:
    """
    Watch `rect` until it is stable for `stable` consecutive frames.
    Returns True when done.
    """
    stable_count = 0
    last_hash = region_hash(rect)

    while stable_count < stable:
        time.sleep(POLL_INTERVAL)
        new_hash = region_hash(rect)
        if new_hash == last_hash:
            stable_count += 1
            bar = ("=" * stable_count) + ("-" * (stable - stable_count))
            print(f"   Stable [{bar}] {stable_count}/{stable}      ", end="\r", flush=True)
        else:
            stable_count = 0
            print("   Still generating...                        ", end="\r", flush=True)
        last_hash = new_hash

    print("\n")
    return True


def run(window_name: str, play_sound: bool, stable: int):
    print(f"""
+------------------------------------------+
|   ANTIGRAVITY WATCHER  v3 (region pick)  |
+------------------------------------------+
  Window  : '{window_name}'
  Platform: {platform.system()}
""")

    # Keep a saved region between prompts so user only picks once
    saved_rect = None

    while True:
        print("=" * 52)
        print("  STEP 1 → Type your prompt in Antigravity IDE")
        print("  STEP 2 → Hit submit")
        print("  STEP 3 → Come back here and press Enter")
        print("=" * 52)

        try:
            input("\n  Press Enter AFTER submitting your prompt: ")
        except KeyboardInterrupt:
            print("\n\nStopped."); break

        # ── Pick region (only needed once, then reused) ──────────────
        if saved_rect is None:
            print("""
  ┌─────────────────────────────────────────────────────┐
  │  A selection screen will appear over your display.  │
  │  Drag a box around JUST the small area where        │
  │  Antigravity shows it is generating                 │
  │  (spinner, stop button, "generating..." text, etc.) │
  │                                                     │
  │  That tiny region is what the script will watch.    │
  └─────────────────────────────────────────────────────┘
  Press Enter to open the selector...
""")
            try:
                input("  > ")
            except KeyboardInterrupt:
                print("\n\nStopped."); break

            picker = RegionPicker()
            rect   = picker.pick()

            if rect is None:
                print("\n  No region selected (you pressed Escape or drew too small a box).")
                print("  Try again — run the script once more.\n")
                break

            saved_rect = rect
            print(f"\n  Region saved: {rect}")
            print(f"  Size: {rect[2]-rect[0]}px wide x {rect[3]-rect[1]}px tall\n")
        else:
            print(f"  Using saved region: {saved_rect}\n")

        # ── Watch the region ─────────────────────────────────────────
        print("  Watching region. Go to your browser now!\n")
        watch_region(saved_rect, stable)

        # ── Done — snap focus ────────────────────────────────────────
        time.sleep(SWITCH_DELAY)
        bring_to_front(window_name)
        if play_sound:
            play_alert()
        send_notification("Prompt finished — switching back to Antigravity.")

        print("  Done! Antigravity should now be in focus.\n")
        print("  (To pick a different region next time, restart the script.)\n")


# ──────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window",  default=WINDOW_NAME)
    parser.add_argument("--sound",   action="store_true")
    parser.add_argument("--stable",  type=int, default=STABLE_COUNT)
    parser.add_argument("--list-windows", action="store_true")
    args = parser.parse_args()

    if args.list_windows:
        list_all_windows(); sys.exit(0)

    try:
        run(args.window, args.sound, args.stable)
    except KeyboardInterrupt:
        print("\n\nStopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
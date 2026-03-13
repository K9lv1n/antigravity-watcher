"""
antigravity_watcher.py  v4 — Template Matching
================================================
Instead of watching for pixel changes (unreliable), you capture a small
screenshot of what Antigravity looks like when it is DONE. The script
then watches the screen until that exact image appears — and only then
switches focus back to you.

This is accurate because:
- It looks for a specific visual state, not just "stopped moving"
- It won't trigger mid-task pauses or re-runs
- You define exactly what "done" means by capturing it yourself

INSTALL (run once):
  pip install Pillow pygetwindow pyautogui opencv-python

FIRST TIME SETUP:
  python antigravity_watcher.py --capture-done
  (follow the prompts to screenshot your "done" state)

NORMAL USE:
  python antigravity_watcher.py
"""

import sys, time, subprocess, platform, hashlib, io, argparse, os
import tkinter as tk
from PIL import ImageGrab, Image, ImageTk
import pyautogui
import cv2
import numpy as np

WINDOW_NAME     = "Antigravity"
TEMPLATE_FILE   = "done_template.png"   # saved next to the script
POLL_INTERVAL   = 0.8
CONFIDENCE      = 0.85   # 0.0 - 1.0, how closely it must match (0.85 = 85%)
SWITCH_DELAY    = 0.3


# ──────────────────────────────────────────────────────────────────
# TEMPLATE CAPTURE
# A crosshair overlay lets you drag a box to capture the "done" state.
# ──────────────────────────────────────────────────────────────────

class RegionCapture:
    """Fullscreen crosshair overlay. Drag to select. Returns cropped PIL image."""

    def __init__(self):
        self.result_image = None
        self.result_rect  = None

    def capture(self):
        # Take screenshot BEFORE opening the overlay window
        screen = ImageGrab.grab()
        sw, sh = screen.size

        # Darken the screenshot slightly so the selection box stands out
        darkened = screen.point(lambda p: int(p * 0.55))

        root = tk.Tk()
        root.overrideredirect(True)          # no title bar
        root.geometry(f"{sw}x{sh}+0+0")     # exact screen size, top-left corner
        root.attributes("-topmost", True)
        root.configure(bg="black")

        # Single canvas — screenshot drawn on it, selection box drawn on top
        canvas = tk.Canvas(root, width=sw, height=sh,
                           highlightthickness=0, cursor="cross", bg="black")
        canvas.pack(fill="both", expand=True)

        # Draw the darkened screenshot as the canvas background
        screen_tk = ImageTk.PhotoImage(darkened)
        canvas.create_image(0, 0, anchor="nw", image=screen_tk)
        canvas._bg_image = screen_tk   # keep reference so Python doesn't GC it

        # Instruction banner drawn on the canvas itself
        canvas.create_rectangle(
            sw//2 - 400, 18, sw//2 + 400, 68,
            fill="#0d0d0d", outline="#00ff88", width=1
        )
        canvas.create_text(
            sw//2, 43,
            text="Drag a box around the DONE indicator in Antigravity  |  Escape = cancel",
            font=("Consolas", 13, "bold"),
            fill="#00ff88"
        )

        rect_id = [None]
        start   = [0, 0]

        def on_press(e):
            start[0], start[1] = e.x, e.y
            if rect_id[0]:
                canvas.delete(rect_id[0])

        def on_drag(e):
            if rect_id[0]:
                canvas.delete(rect_id[0])
            rect_id[0] = canvas.create_rectangle(
                start[0], start[1], e.x, e.y,
                outline="#00ff88", width=2,
                fill="#00ff88", stipple="gray25"
            )

        def on_release(e):
            x1 = min(start[0], e.x); y1 = min(start[1], e.y)
            x2 = max(start[0], e.x); y2 = max(start[1], e.y)
            if (x2 - x1) > 8 and (y2 - y1) > 8:
                self.result_rect  = (x1, y1, x2, y2)
                # Crop from the ORIGINAL (undarkened) screenshot
                self.result_image = screen.crop((x1, y1, x2, y2))
            root.destroy()

        def on_escape(e):
            root.destroy()

        def on_escape(e):
            root.destroy()

        canvas.bind("<ButtonPress-1>",   on_press)
        canvas.bind("<B1-Motion>",       on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        root.bind("<Escape>",            on_escape)
        root.mainloop()

        return self.result_image, self.result_rect


# ──────────────────────────────────────────────────────────────────
# TEMPLATE MATCHING  (opencv)
# ──────────────────────────────────────────────────────────────────

def capture_window_pixels(hwnd) -> np.ndarray:
    """
    Capture the pixels of a window by its HWND using PrintWindow —
    works even when the window is hidden behind other windows.
    Returns a BGR numpy array, or None on failure.
    """
    import ctypes
    import ctypes.wintypes

    # Get window dimensions
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right  - rect.left
    h = rect.bottom - rect.top
    if w <= 0 or h <= 0:
        return None

    # Create a device context and bitmap to draw into
    hwnd_dc  = ctypes.windll.user32.GetWindowDC(hwnd)
    mem_dc   = ctypes.windll.gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap   = ctypes.windll.gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    ctypes.windll.gdi32.SelectObject(mem_dc, bitmap)

    # PW_RENDERFULLCONTENT (2) — captures even hardware-accelerated windows
    ctypes.windll.user32.PrintWindow(hwnd, mem_dc, 2)

    # Read bitmap bits into a numpy array
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize",          ctypes.c_uint32),
            ("biWidth",         ctypes.c_int32),
            ("biHeight",        ctypes.c_int32),
            ("biPlanes",        ctypes.c_uint16),
            ("biBitCount",      ctypes.c_uint16),
            ("biCompression",   ctypes.c_uint32),
            ("biSizeImage",     ctypes.c_uint32),
            ("biXPelsPerMeter", ctypes.c_int32),
            ("biYPelsPerMeter", ctypes.c_int32),
            ("biClrUsed",       ctypes.c_uint32),
            ("biClrImportant",  ctypes.c_uint32),
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize      = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth     = w
    bmi.biHeight    = -h   # negative = top-down
    bmi.biPlanes    = 1
    bmi.biBitCount  = 32
    bmi.biCompression = 0  # BI_RGB

    buf = (ctypes.c_char * (w * h * 4))()
    ctypes.windll.gdi32.GetDIBits(mem_dc, bitmap, 0, h, buf, ctypes.byref(bmi), 0)

    # Cleanup GDI objects
    ctypes.windll.gdi32.DeleteObject(bitmap)
    ctypes.windll.gdi32.DeleteDC(mem_dc)
    ctypes.windll.user32.ReleaseDC(hwnd, hwnd_dc)

    img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def find_template_in_window(template_path: str, hwnd, confidence: float) -> bool:
    """
    Capture the Antigravity window directly (even if hidden behind browser)
    and check if the done-template appears inside it.
    """
    try:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"  [error] Could not load template: {template_path}")
            return False

        window_img = capture_window_pixels(hwnd)
        if window_img is None:
            print("  [warn] Could not capture window pixels")
            return False

        result = cv2.matchTemplate(window_img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        return max_val >= confidence

    except Exception as e:
        print(f"  [match error] {e}")
        return False


# ──────────────────────────────────────────────────────────────────
# WINDOW FOCUS
# ──────────────────────────────────────────────────────────────────

def list_all_windows():
    os_name = platform.system()
    print("\n-- All Open Windows ------------------------------------------")
    if os_name == "Windows":
        import ctypes, ctypes.wintypes
        titles = []
        def cb(hwnd, _):
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    titles.append(buf.value)
            return True
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        ctypes.windll.user32.EnumWindows(WNDENUMPROC(cb), 0)
        for t in sorted(titles):
            print(f"  '{t}'")
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


def get_antigravity_hwnd(name: str):
    """
    On Windows, find the exact HWND (window handle) of Antigravity.
    We exclude any window whose title contains 'antigravity_watcher'
    so VS Code never gets picked by accident.
    """
    import ctypes
    import ctypes.wintypes

    found = []

    def enum_callback(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                tl = title.lower()
                # Must contain the name AND must NOT be the watcher script itself
                if name.lower() in tl and "antigravity_watcher" not in tl:
                    found.append((hwnd, title))
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return found[0][0] if found else None


def bring_to_front_by_hwnd(hwnd):
    """
    Force a window to the foreground on Windows.
    SetForegroundWindow() silently fails from a background process.
    Fix: attach to the foreground thread's input queue first, then call it.
    """
    import ctypes
    import ctypes.wintypes

    user32   = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    SW_MAXIMIZE     = 3
    KEYEVENTF_KEYUP = 0x0002
    VK_MENU         = 0x12  # Alt key

    # Maximise the window when bringing it back
    user32.ShowWindow(hwnd, SW_MAXIMIZE)
    time.sleep(0.05)

    # Get the thread that owns the current foreground window
    fg_hwnd   = user32.GetForegroundWindow()
    fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None)
    my_thread = kernel32.GetCurrentThreadId()

    # Attach our thread to the foreground window's input queue
    # This makes Windows allow SetForegroundWindow from our process
    attached = False
    if fg_thread and fg_thread != my_thread:
        user32.AttachThreadInput(fg_thread, my_thread, True)
        attached = True

    # Simulate Alt key press — extra nudge for Windows foreground permission
    user32.keybd_event(VK_MENU, 0, 0, 0)
    user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)

    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    user32.SetFocus(hwnd)

    # Detach input queues
    if attached:
        user32.AttachThreadInput(fg_thread, my_thread, False)

    print("  [focus] Forced foreground: OK")


def bring_to_front(name: str, hwnd=None):
    os_name = platform.system()
    print(f"\n  [focus] Bringing '{name}' to front...")

    if os_name == "Windows":
        # Use saved hwnd if available — bypasses all name-matching ambiguity
        if hwnd:
            try:
                bring_to_front_by_hwnd(hwnd)
                return
            except Exception as e:
                print(f"  [focus] hwnd focus failed: {e}, falling back...")

        # Fallback: find hwnd now (excluding the watcher script)
        try:
            h = get_antigravity_hwnd(name)
            if h:
                bring_to_front_by_hwnd(h)
                return
        except Exception as e:
            print(f"  [focus] hwnd lookup failed: {e}")

        # Last resort: PowerShell with exact title match
        try:
            ps = f"(New-Object -ComObject WScript.Shell).AppActivate('{name}')"
            subprocess.run(["powershell", "-Command", ps],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("  [focus] PowerShell: fired")
        except Exception as e:
            print(f"  [focus] PowerShell: {e}")

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
        if "ok" not in r.stdout:
            subprocess.run(["osascript", "-e", f'tell application "{name}" to activate'],
                           capture_output=True)

    elif os_name == "Linux":
        subprocess.run(["wmctrl", "-a", name], capture_output=True)
        subprocess.run(["xdotool", "search", "--name", name,
                        "windowactivate", "--sync"], capture_output=True)


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
# CAPTURE DONE TEMPLATE  (first-time setup)
# ──────────────────────────────────────────────────────────────────

def capture_done_template(script_dir: str):
    """
    Walk the user through capturing a screenshot of the 'done' state.
    Saves it as done_template.png next to the script.
    """
    save_path = os.path.join(script_dir, TEMPLATE_FILE)

    print("""
+──────────────────────────────────────────────────+
│        CAPTURE YOUR "DONE" TEMPLATE              │
+──────────────────────────────────────────────────+

You need to capture what Antigravity looks like when
it has TRULY finished — not mid-task.

GOOD things to capture (pick ONE small area):
  - The send/submit button reappearing
  - A checkmark or "Done" icon
  - The prompt input box becoming active again
  - Any UI element that ONLY appears when fully done

DO NOT capture:
  - The whole screen (too much noise)
  - The output text area (changes every run)
  - Anything that appears during generation

HOW:
  1. Press Enter below
  2. You have 5 seconds to switch to Antigravity
     and make sure it is showing the DONE state
  3. The selector overlay appears
  4. Drag a tight box around your chosen indicator
  5. Release — it saves automatically
""")

    input("  Press Enter, then switch to Antigravity (show the DONE state)... ")

    for i in range(5, 0, -1):
        print(f"  Overlay opens in {i}...  (switch to Antigravity now!)", end="\r", flush=True)
        time.sleep(1)
    print("  Opening selector...                                       ")

    capturer = RegionCapture()
    img, rect = capturer.capture()

    if img is None:
        print("\n  Cancelled — no template saved.\n")
        return False

    img.save(save_path)
    print(f"\n  Template saved to: {save_path}")
    print(f"  Size: {rect[2]-rect[0]}px x {rect[3]-rect[1]}px\n")

    # Verify the template is detectable in the Antigravity window right now
    print("  Verifying template is detectable in Antigravity window...")
    hwnd = get_antigravity_hwnd(WINDOW_NAME) if platform.system() == "Windows" else None
    if hwnd:
        found = find_template_in_window(save_path, hwnd, CONFIDENCE)
    else:
        found = False
    if found:
        print("  Verification passed — template found on screen.\n")
    else:
        print(f"""
  WARNING: Template NOT found on screen right now.
  This could mean:
    - The 'done' state is no longer visible (Antigravity changed state)
    - Your capture was too small or blurry
    - The confidence threshold ({CONFIDENCE}) is too strict

  Suggestion: Run --capture-done again and try capturing
  a slightly larger area, or a more distinctive element.

  You can also lower confidence: --confidence 0.75
""")

    return True


# ──────────────────────────────────────────────────────────────────
# MAIN WATCH LOOP
# ──────────────────────────────────────────────────────────────────

def run(window_name: str, play_sound: bool, confidence: float, script_dir: str):
    template_path = os.path.join(script_dir, TEMPLATE_FILE)

    print(f"""
+------------------------------------------+
|   ANTIGRAVITY WATCHER  v4                |
|   Template Matching Edition              |
+------------------------------------------+
  Window    : '{window_name}'
  Template  : {template_path}
  Confidence: {int(confidence*100)}%
  Platform  : {platform.system()}
""")

    # Check template exists
    if not os.path.exists(template_path):
        print(f"""
  ERROR: No template found at:
  {template_path}

  Run this first to create it:
    python antigravity_watcher.py --capture-done
""")
        sys.exit(1)

    # Grab Antigravity's exact window handle NOW, before the user switches away.
    # This guarantees we focus the right window later, not VS Code.
    antigravity_hwnd = None
    if platform.system() == "Windows":
        antigravity_hwnd = get_antigravity_hwnd(window_name)
        if antigravity_hwnd:
            print(f"  Antigravity window handle locked: {antigravity_hwnd}")
        else:
            print(f"  WARNING: Could not find '{window_name}' window.")
            print(f"  Make sure Antigravity is open before running this script.\n")

    while True:
        print("=" * 52)
        print("  STEP 1 → Type your prompt in Antigravity")
        print("  STEP 2 → Hit submit in Antigravity")
        print("  STEP 3 → Come back here and press Enter")
        print("=" * 52)

        try:
            input("\n  Press Enter AFTER submitting your prompt: ")
        except KeyboardInterrupt:
            print("\n\nStopped."); break

        print("\n  Watching for 'done' state...")
        print("  Go to your browser now — I will bring you back.\n")

        # Guard: need hwnd to capture the window in background
        if not antigravity_hwnd:
            print("  ERROR: No Antigravity window handle. Is Antigravity open?")
            print("  Restart the script with Antigravity already open.\n")
            break

        # Poll the Antigravity window directly — works even when hidden behind browser
        checks = 0
        while True:
            time.sleep(POLL_INTERVAL)
            checks += 1
            found = find_template_in_window(template_path, antigravity_hwnd, confidence)

            mins = (checks * POLL_INTERVAL) // 60
            secs = (checks * POLL_INTERVAL) % 60
            print(f"   Watching window... {int(mins)}m {int(secs)}s  "
                  f"({'FOUND!' if found else 'not yet'})", end="\r", flush=True)

            if found:
                break

        print("\n\n  Template matched — Antigravity is done!")
        time.sleep(SWITCH_DELAY)

        bring_to_front(window_name, hwnd=antigravity_hwnd)
        if play_sound:
            play_alert()
        send_notification("Prompt finished — switching back to Antigravity.")

        print("  Done! Antigravity should now be in focus.\n")


# ──────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument("--window",       default=WINDOW_NAME)
    parser.add_argument("--sound",        action="store_true")
    parser.add_argument("--confidence",   type=float, default=CONFIDENCE,
                        help=f"Match confidence 0-1 (default: {CONFIDENCE})")
    parser.add_argument("--capture-done", action="store_true",
                        help="Run the one-time setup to capture your 'done' template")
    parser.add_argument("--list-windows", action="store_true",
                        help="Print all open window titles and exit")
    args = parser.parse_args()

    if args.list_windows:
        list_all_windows()
        sys.exit(0)

    if args.capture_done:
        capture_done_template(script_dir)
        sys.exit(0)

    try:
        run(args.window, args.sound, args.confidence, script_dir)
    except KeyboardInterrupt:
        print("\n\nStopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
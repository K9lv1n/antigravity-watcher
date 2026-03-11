"""
antigravity_watcher.py
======================
Watches Antigravity IDE in the background.
When it detects the IDE has finished generating a response (screen stops changing),
it automatically brings the Antigravity window back to the front — even if you're
on a different browser or app.

HOW TO USE:
  1. Install dependencies (see SETUP below)
  2. Run this script:  python antigravity_watcher.py
  3. Type your prompt in Antigravity IDE
  4. Switch to your browser and do whatever you want
  5. Script watches the IDE — when done, it yanks focus back to Antigravity

SETUP (run these once in your terminal):
  pip install Pillow pygetwindow pyautogui

  Linux extra:
    sudo apt install wmctrl xdotool

  macOS: no extras needed
  Windows: no extras needed
"""

import sys
import time
import subprocess
import platform
import hashlib
import io
import argparse
from PIL import ImageGrab, Image

# ─────────────────────────────────────────────────────────
# CONFIGURATION — adjust these to fit your setup
# ─────────────────────────────────────────────────────────

# The name (or part of the name) of the Antigravity IDE window.
# The script will search for a window whose title CONTAINS this string.
# Run: python antigravity_watcher.py --list-windows
# to see all open window titles on your machine.
WINDOW_NAME = "Antigravity"

# How often (in seconds) to take a screenshot and compare
POLL_INTERVAL = 1.0

# How many consecutive unchanged screenshots = "done"
# At POLL_INTERVAL=1s, STABLE_COUNT=4 means "stable for 4 seconds"
STABLE_COUNT = 4

# After detecting "done", wait this many extra seconds before switching focus
# (gives the IDE time to finish any final rendering)
SWITCH_DELAY = 0.5

# Play a sound when done? True/False
PLAY_SOUND = True


# ─────────────────────────────────────────────────────────
# WINDOW UTILITIES — finding and focusing the IDE window
# ─────────────────────────────────────────────────────────

def list_all_windows():
    """Print every open window title so you can find the right WINDOW_NAME."""
    os_name = platform.system()
    print("\n── Open Windows ──────────────────────────────────")
    if os_name == "Windows":
        import pygetwindow as gw
        for w in gw.getAllWindows():
            if w.title.strip():
                print(f"  {w.title!r}")
    elif os_name == "Darwin":
        script = '''
        tell application "System Events"
            set appList to {}
            repeat with p in (every process whose background only is false)
                repeat with w in (every window of p)
                    set end of appList to (name of p) & " | " & (name of w)
                end repeat
            end repeat
            return appList
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        for line in result.stdout.strip().split(", "):
            print(f"  {line.strip()}")
    elif os_name == "Linux":
        result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    print("──────────────────────────────────────────────────\n")


def find_window(name: str):
    """
    Find a window whose title contains `name` (case-insensitive).
    Returns a platform-specific window object, or None if not found.
    """
    os_name = platform.system()
    name_lower = name.lower()

    if os_name == "Windows":
        import pygetwindow as gw
        matches = [w for w in gw.getAllWindows() if name_lower in w.title.lower()]
        return matches[0] if matches else None

    elif os_name == "Darwin":
        # On macOS we return just the app name string; focusing uses AppleScript
        script = f'''
        tell application "System Events"
            set found to ""
            repeat with p in (every process whose background only is false)
                if (name of p) contains "{name}" then
                    set found to name of p
                end if
            end repeat
            return found
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        app_name = result.stdout.strip()
        return app_name if app_name else None

    elif os_name == "Linux":
        result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
        for line in result.stdout.strip().split("\n"):
            if name_lower in line.lower():
                # Return the window ID (first field)
                return line.split()[0]
        return None

    return None


def get_window_rect(name: str):
    """
    Returns (left, top, right, bottom) bounding box of the window,
    or None if not found. Used to take a cropped screenshot.
    """
    os_name = platform.system()
    name_lower = name.lower()

    if os_name == "Windows":
        import pygetwindow as gw
        matches = [w for w in gw.getAllWindows() if name_lower in w.title.lower()]
        if not matches:
            return None
        w = matches[0]
        return (w.left, w.top, w.right, w.bottom)

    elif os_name == "Darwin":
        script = f'''
        tell application "System Events"
            repeat with p in (every process whose background only is false)
                if (name of p) contains "{name}" then
                    tell p
                        set w to first window
                        set pos to position of w
                        set sz to size of w
                        return (item 1 of pos) & "," & (item 2 of pos) & "," & (item 1 of sz) & "," & (item 2 of sz)
                    end tell
                end if
            end repeat
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        parts = result.stdout.strip().split(",")
        if len(parts) == 4:
            x, y, w, h = [int(p.strip()) for p in parts]
            return (x, y, x + w, y + h)
        return None

    elif os_name == "Linux":
        result = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
        for line in result.stdout.strip().split("\n"):
            if name_lower in line.lower():
                parts = line.split()
                # Format: id desktop x y w h machine title
                x, y, w, h = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                return (x, y, x + w, y + h)
        return None

    return None


def bring_to_front(name: str):
    """
    Bring the window matching `name` to the foreground.
    Uses OS-specific methods to work even when the browser is in front.
    """
    os_name = platform.system()

    if os_name == "Windows":
        import pygetwindow as gw
        matches = [w for w in gw.getAllWindows() if name.lower() in w.title.lower()]
        if matches:
            w = matches[0]
            try:
                w.minimize()
                time.sleep(0.1)
                w.restore()
                w.activate()
            except Exception:
                pass

    elif os_name == "Darwin":
        script = f'''
        tell application "System Events"
            repeat with p in (every process whose background only is false)
                if (name of p) contains "{name}" then
                    set frontmost of p to true
                end if
            end repeat
        end tell
        '''
        subprocess.run(["osascript", "-e", script], check=False)

    elif os_name == "Linux":
        # Try wmctrl first
        subprocess.run(["wmctrl", "-a", name], check=False)
        # Also try xdotool as backup
        result = subprocess.run(
            ["xdotool", "search", "--name", name, "windowactivate", "--sync"],
            check=False, capture_output=True
        )


# ─────────────────────────────────────────────────────────
# SCREENSHOT COMPARISON — detecting when the IDE is "done"
# ─────────────────────────────────────────────────────────

def screenshot_hash(rect=None) -> str:
    """
    Take a screenshot (optionally cropped to `rect`) and return its MD5 hash.
    Two identical screenshots = same hash = screen hasn't changed.
    """
    img = ImageGrab.grab(bbox=rect)  # bbox=None means full screen
    # Resize to a small thumbnail before hashing — faster and ignores tiny cursor blinks
    img = img.resize((200, 150), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()


def play_alert():
    """Play a system sound to alert the user."""
    os_name = platform.system()
    try:
        if os_name == "Darwin":
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
        elif os_name == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif os_name == "Linux":
            # Try multiple common sound files
            for sound in [
                "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "/usr/share/sounds/ubuntu/stereo/system-ready.ogg",
            ]:
                result = subprocess.run(["paplay", sound], check=False, capture_output=True)
                if result.returncode == 0:
                    break
    except Exception:
        print("\a", end="", flush=True)  # terminal bell as fallback


def send_notification(message: str):
    """Show a desktop notification."""
    os_name = platform.system()
    try:
        if os_name == "Darwin":
            script = f'display notification "{message}" with title "Antigravity Done ✓"'
            subprocess.run(["osascript", "-e", script], check=False)
        elif os_name == "Linux":
            subprocess.run(["notify-send", "Antigravity Done ✓", message], check=False)
        elif os_name == "Windows":
            # Works without extra install on Windows 10/11
            ps = (
                f"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
                f"ContentType = WindowsRuntime] | Out-Null; "
                f"$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
                f"[Windows.UI.Notifications.ToastTemplateType]::ToastText01); "
                f"$textNode = $template.GetElementsByTagName('text')[0]; "
                f"$textNode.AppendChild($template.CreateTextNode('{message}')) | Out-Null; "
                f"$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
                f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Antigravity').Show($toast);"
            )
            subprocess.run(["powershell", "-Command", ps],
                           check=False, capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────
# MAIN WATCHER LOOP
# ─────────────────────────────────────────────────────────

def watch(window_name: str, play_sound: bool):
    print(f"\n🚀 Antigravity Watcher Started")
    print(f"   Looking for window : '{window_name}'")
    print(f"   Platform           : {platform.system()}")
    print(f"   Poll interval      : {POLL_INTERVAL}s")
    print(f"   Stable threshold   : {STABLE_COUNT} unchanged frames = done\n")

    # ── Step 1: Find the Antigravity window ──────────────────────────────
    rect = None
    print("🔍 Searching for Antigravity window...")
    while True:
        rect = get_window_rect(window_name)
        if rect:
            print(f"✅ Found window at rect: {rect}\n")
            break
        print(f"   Not found yet — is Antigravity open? Retrying in 3s...")
        time.sleep(3)

    # ── Step 2: Wait for activity to START ───────────────────────────────
    print("⏳ Watching for you to submit a prompt...")
    print("   (Type your prompt in Antigravity and hit Enter/Submit)\n")

    baseline_hash = screenshot_hash(rect)
    while True:
        time.sleep(POLL_INTERVAL)
        current_hash = screenshot_hash(rect)
        if current_hash != baseline_hash:
            print("🟡 Activity detected — Antigravity is working...\n")
            print("   ✈  You can switch to your browser now.\n")
            break
        baseline_hash = current_hash  # keep updating baseline while idle

    # ── Step 3: Wait for activity to STOP (response finished) ────────────
    stable_count = 0
    last_hash = screenshot_hash(rect)

    while stable_count < STABLE_COUNT:
        time.sleep(POLL_INTERVAL)
        new_hash = screenshot_hash(rect)

        if new_hash == last_hash:
            stable_count += 1
            print(f"   Still... ({stable_count}/{STABLE_COUNT})", end="\r")
        else:
            stable_count = 0  # reset if something changed
            print("   Still generating...         ", end="\r")

        last_hash = new_hash

    # ── Step 4: Done! Bring Antigravity back to front ────────────────────
    print("\n\n✅ Response complete! Switching back to Antigravity...\n")
    time.sleep(SWITCH_DELAY)

    bring_to_front(window_name)

    if play_sound:
        play_alert()

    send_notification("Your prompt has finished! Switching back to Antigravity.")

    print("🎉 Done! Antigravity is now in focus.")
    print("   Run the script again for your next prompt.\n")


# ─────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Automatically refocus Antigravity IDE when a prompt finishes."
    )
    parser.add_argument(
        "--window", default=WINDOW_NAME,
        help=f"Window title to search for (default: '{WINDOW_NAME}')"
    )
    parser.add_argument(
        "--sound", action="store_true", default=PLAY_SOUND,
        help="Play a sound when the response finishes"
    )
    parser.add_argument(
        "--list-windows", action="store_true",
        help="Print all open window titles and exit (useful for finding the right --window name)"
    )
    parser.add_argument(
        "--stable", type=int, default=STABLE_COUNT,
        help=f"Consecutive stable frames needed to declare 'done' (default: {STABLE_COUNT})"
    )
    args = parser.parse_args()

    if args.list_windows:
        list_all_windows()
        sys.exit(0)

    global STABLE_COUNT
    STABLE_COUNT = args.stable

    try:
        watch(args.window, args.sound)
    except KeyboardInterrupt:
        print("\n\n👋 Watcher stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
"""
System tray icon for Jarvis.
Gives the user a visible "Jarvis is running" indicator and an Exit option,
since the assistant runs with no console window once auto-started.
"""
import threading
import pystray
from PIL import Image, ImageDraw


def _make_icon_image():
    img = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(img)
    draw.ellipse((12, 12, 52, 52), fill="deepskyblue")
    return img


def run_tray(on_exit):
    """
    Runs the tray icon on its own thread.
    on_exit: callback invoked when the user clicks Exit.
    """
    def _exit_action(icon, item):
        icon.stop()
        on_exit()

    menu = pystray.Menu(
        pystray.MenuItem("Jarvis is running", None, enabled=False),
        pystray.MenuItem("Exit", _exit_action),
    )
    icon = pystray.Icon("jarvis", _make_icon_image(), "Jarvis", menu)
    icon.run()


def start_tray_thread(on_exit):
    t = threading.Thread(target=run_tray, args=(on_exit,), daemon=True)
    t.start()
    return t

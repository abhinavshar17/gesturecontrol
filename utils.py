# utils.py

from PIL import ImageGrab
import win32clipboard
from io import BytesIO

def copy_screenshot_to_clipboard(x1, y1, x2, y2):
    image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

    print("📸 Screenshot copied to clipboard.")

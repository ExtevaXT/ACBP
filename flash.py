import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

FLASHW_STOP = 0
FLASHW_CAPTION = 0x00000001
FLASHW_TRAY = 0x00000002
FLASHW_ALL = 0x00000003
FLASHW_TIMER = 0x00000004
FLASHW_TIMERNOFG = 0x0000000C

class FLASHWINFO(ctypes.Structure):
    _fields_ = (('cbSize', wintypes.UINT),
                ('hwnd', wintypes.HWND),
                ('dwFlags', wintypes.DWORD),
                ('uCount', wintypes.UINT),
                ('dwTimeout', wintypes.DWORD))
    def __init__(self, hwnd, flags=FLASHW_TRAY, count=5, timeout_ms=0):
        self.cbSize = ctypes.sizeof(self)
        self.hwnd = hwnd
        self.dwFlags = flags
        self.uCount = count
        self.dwTimeout = timeout_ms

kernel32.GetConsoleWindow.restype = wintypes.HWND
user32.FlashWindowEx.argtypes = (ctypes.POINTER(FLASHWINFO),)

def flash_console_icon(count=5):
    hwnd = kernel32.GetConsoleWindow()
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())
    winfo = FLASHWINFO(hwnd, count=count)
    previous_state = user32.FlashWindowEx(ctypes.byref(winfo))
    return previous_state
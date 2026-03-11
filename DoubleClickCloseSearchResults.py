# -*- coding: utf-8 -*-
# Close (hide) the docked "Search results" panel when you double-click anywhere in the editor.
#
# This uses a Win32 subclass (WndProc hook) to catch WM_LBUTTONDBLCLK directly,
# avoiding Scintilla notification differences across PythonScript builds.

from Npp import notepad, editor1, editor2, console
import ctypes
from ctypes import windll, create_unicode_buffer, WINFUNCTYPE
from ctypes.wintypes import BOOL, HWND, LPARAM, WPARAM, UINT

console.show()
console.write("DoubleClickCloseSearchResults_WinMsg loaded\n")

user32 = windll.user32

# --- Win32 APIs we need ---
SendMessageW = user32.SendMessageW
SendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
SendMessageW.restype = LPARAM

EnumChildWindows = user32.EnumChildWindows
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextW = user32.GetWindowTextW
GetClassNameW = user32.GetClassNameW

# 32/64-bit safe SetWindowLongPtr / CallWindowProc
if ctypes.sizeof(ctypes.c_void_p) == 8:
    SetWindowLongPtrW = user32.SetWindowLongPtrW
    GetWindowLongPtrW = user32.GetWindowLongPtrW
    CallWindowProcW = user32.CallWindowProcW
else:
    SetWindowLongPtrW = user32.SetWindowLongW
    GetWindowLongPtrW = user32.GetWindowLongW
    CallWindowProcW = user32.CallWindowProcW

SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, ctypes.c_void_p]
SetWindowLongPtrW.restype = ctypes.c_void_p

GetWindowLongPtrW.argtypes = [HWND, ctypes.c_int]
GetWindowLongPtrW.restype = ctypes.c_void_p

CallWindowProcW.argtypes = [ctypes.c_void_p, HWND, UINT, WPARAM, LPARAM]
CallWindowProcW.restype = LPARAM

# --- Constants ---
WM_USER = 0x0400
NPPMSG = WM_USER + 1000
NPPM_DMMHIDE = NPPMSG + 31

WM_LBUTTONDBLCLK = 0x0203
GWL_WNDPROC = -4

SEARCH_RESULTS_TITLE = u"Search results"
CLASS_DIALOG = u"#32770"
bufClass = create_unicode_buffer(256)

# Ensure notepad.hwnd exists (older builds sometimes need it)
if not hasattr(notepad, "hwnd"):
    FindWindowW = user32.FindWindowW
    FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
    FindWindowW.restype = HWND
    notepad.hwnd = FindWindowW(u"Notepad++", None)

notepadMainHwnd = notepad.hwnd


def hideSearchResultsIfOpen():
    """Hide the docked Search results panel if present."""
    foundHwnd = {"value": None}
    enumProcType = WINFUNCTYPE(BOOL, HWND, LPARAM)

    def enumProc(hwnd, lParam):
        classLen = GetClassNameW(hwnd, bufClass, 256)
        className = bufClass.value[:classLen]

        if className == CLASS_DIALOG:
            titleLen = GetWindowTextLengthW(hwnd)
            if titleLen > 0:
                titleBuf = create_unicode_buffer(titleLen + 1)
                GetWindowTextW(hwnd, titleBuf, titleLen + 1)
                if titleBuf.value == SEARCH_RESULTS_TITLE:
                    foundHwnd["value"] = hwnd
                    return False  # stop
        return True

    EnumChildWindows(notepadMainHwnd, enumProcType(enumProc), 0)

    if foundHwnd["value"]:
        SendMessageW(notepadMainHwnd, NPPM_DMMHIDE, 0, foundHwnd["value"])


# ---- Subclass WndProcs (keep globals so they don't get GC'd) ----
oldProcByHwnd = {}
newProcByHwnd = {}

WndProcType = WINFUNCTYPE(LPARAM, HWND, UINT, WPARAM, LPARAM)


def installDoubleClickHook(scintillaHwnd):
    if scintillaHwnd in oldProcByHwnd:
        return  # already hooked

    oldProc = GetWindowLongPtrW(scintillaHwnd, GWL_WNDPROC)
    oldProcByHwnd[scintillaHwnd] = oldProc

    def wndProc(hwnd, msg, wParam, lParam):
        if msg == WM_LBUTTONDBLCLK:
            hideSearchResultsIfOpen()
        return CallWindowProcW(oldProcByHwnd[hwnd], hwnd, msg, wParam, lParam)

    newProc = WndProcType(wndProc)
    newProcByHwnd[scintillaHwnd] = newProc  # keep alive

    SetWindowLongPtrW(scintillaHwnd, GWL_WNDPROC, ctypes.cast(newProc, ctypes.c_void_p))


# editor.hwnd exists in most PythonScript builds; if not, we can’t hook that view.
if hasattr(editor1, "hwnd"):
    installDoubleClickHook(editor1.hwnd)
else:
    console.write("editor1.hwnd not available on this build\n")

if hasattr(editor2, "hwnd"):
    installDoubleClickHook(editor2.hwnd)
else:
    console.write("editor2.hwnd not available on this build\n")

console.write("DoubleClickCloseSearchResults_WinMsg hooks installed\n")

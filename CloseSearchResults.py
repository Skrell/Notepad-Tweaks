# -*- coding: utf-8 -*-
# Close (hide) the docked "Search results" panel if it is present.
#
# Based on a Notepad++ Community script that finds the Search results HWND
# and sends NPPM_DMMHIDE to the Notepad++ main window. :contentReference[oaicite:1]{index=1}

from ctypes import windll, create_unicode_buffer, WINFUNCTYPE
from ctypes.wintypes import BOOL, HWND, LPARAM, WPARAM, UINT
from Npp import notepad

# Win32 functions
sendMessageW = windll.user32.SendMessageW
sendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
sendMessageW.restype = LPARAM

findWindowW = windll.user32.FindWindowW
getWindowTextW = windll.user32.GetWindowTextW
getWindowTextLengthW = windll.user32.GetWindowTextLengthW
enumChildWindows = windll.user32.EnumChildWindows
getClassNameW = windll.user32.GetClassNameW

# Constants
windowMessageUser = 0x0400  # WM_USER
nppMessageBase = windowMessageUser + 1000
nppMessageDockMgrHide = nppMessageBase + 31  # NPPM_DMMHIDE :contentReference[oaicite:2]{index=2}

searchResultsTitle = u"Search results"
bufferClass = create_unicode_buffer(256)

# PythonScript 3 usually has notepad.hwnd; PythonScript 2 may not. :contentReference[oaicite:3]{index=3}
if not hasattr(notepad, "hwnd"):
    notepad.hwnd = findWindowW(u"Notepad++", None)

notepadMainHwnd = notepad.hwnd
searchResultsHwnd = None

# Enumerate child windows under Notepad++ main window to find the docked dialog titled "Search results"
windowEnumProcType = WINFUNCTYPE(BOOL, HWND, LPARAM)

def foreachWindow(hwnd, lParam):
    global searchResultsHwnd

    classLength = getClassNameW(hwnd, bufferClass, 256)
    className = bufferClass.value[:classLength]

    # Docked panels in Notepad++ are commonly dialogs with class "#32770" :contentReference[oaicite:4]{index=4}
    if className == u"#32770":
        titleLength = getWindowTextLengthW(hwnd)
        if titleLength > 0:
            titleBuffer = create_unicode_buffer(titleLength + 1)
            getWindowTextW(hwnd, titleBuffer, titleLength + 1)
            if titleBuffer.value == searchResultsTitle:
                searchResultsHwnd = hwnd
                return False  # stop enumeration

    return True  # continue enumeration

enumChildWindows(notepadMainHwnd, windowEnumProcType(foreachWindow), 0)

# If found, hide it (if it isn't open/visible/docked, it won't be found and we do nothing)
if searchResultsHwnd:
    sendMessageW(notepadMainHwnd, nppMessageDockMgrHide, 0, searchResultsHwnd)

from Npp import notepad, MENUCOMMAND
import time
import ctypes


def sendAltO():
    user32 = ctypes.windll.user32

    keyAlt = 0x12  # VK_MENU
    keyOhh = 0x4F  # VK_O
    keyUp = 0x0002  # KEYEVENTF_KEYUP

    user32.keybd_event(keyAlt, 0, 0, 0)
    user32.keybd_event(keyOhh, 0, 0, 0)
    user32.keybd_event(keyOhh, 0, keyUp, 0)
    user32.keybd_event(keyAlt, 0, keyUp, 0)


# Open Find dialog.
# Notepad++ will typically pre-fill the Find field from selection/current word.
notepad.menuCommand(MENUCOMMAND.SEARCH_FIND)  # Ctrl+F equivalent
time.sleep(0.05)

# Trigger "Find All in All Opened Documents" via the dialog accelerator (Alt+O).
sendAltO()

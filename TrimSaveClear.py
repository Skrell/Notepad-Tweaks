# -*- coding: utf-8 -*-

from Npp import notepad, console, editor
import __main__

trimTrailingCommandId = 42024
clearChangeHistoryCommandId = 43069  # replace with your real ID

# TODO: set this to the command ID for:
# Window -> Sort by -> Modified Time Ascending
# Recommended: use NppUISpy to copy the menu command ID.
sortByModifiedTimeAscendingCommandId = 11010

if not hasattr(__main__, "sessionCountsByFile"):
    __main__.sessionCountsByFile = {}

sessionCountsByFile = __main__.sessionCountsByFile
currentFilename = notepad.getCurrentFilename()

if not currentFilename:
    notepad.messageBox(
        u"No active filename was found.",
        u"Trim + Save + Conditional Clear Change History",
        0
    )
else:
    isModified = editor.getModify()
    isReadOnly = editor.getReadOnly()

    console.clear()
    console.write("currentFilename = {0}\r\n".format(currentFilename))
    console.write("isModified = {0}\r\n".format(isModified))
    console.write("isReadOnly = {0}\r\n".format(isReadOnly))

    # Only execute when Save would be enabled
    if (not isModified) or isReadOnly:
        console.write("Skipped: Save not enabled for this file.\r\n")
    else:
        currentCount = sessionCountsByFile.get(currentFilename, 0) + 1
        console.write("currentCount = {0}\r\n".format(currentCount))

        notepad.menuCommand(trimTrailingCommandId)
        notepad.save()

        if currentCount >= 8:
            if clearChangeHistoryCommandId:
                notepad.menuCommand(clearChangeHistoryCommandId)
                sessionCountsByFile[currentFilename] = 0
                console.write("clearChangeHistoryCommandId executed\r\n")
            else:
                notepad.messageBox(
                    u'Set clearChangeHistoryCommandId to the numeric command ID for '
                    u'"Clear Change History" first.',
                    u"Trim + Save + Conditional Clear Change History",
                    0
                )
                sessionCountsByFile[currentFilename] = currentCount
        else:
            sessionCountsByFile[currentFilename] = currentCount

        # Final step: sort tabs by modified time ascending
        if sortByModifiedTimeAscendingCommandId:
            notepad.menuCommand(sortByModifiedTimeAscendingCommandId)
            console.write("sortByModifiedTimeAscendingCommandId executed\r\n")
        else:
            console.write(
                "NOTE: sortByModifiedTimeAscendingCommandId is not set; skipping sort.\r\n"
            )

        console.write("saved successfully\r\n")

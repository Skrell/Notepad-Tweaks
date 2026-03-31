# -*- coding: utf-8 -*-
# Select text that looks like a (partial) file path, then run this script.
# It will switch to the best-matching open tab by path/filename.

from Npp import notepad, editor, console
import os


def normalizePath(pathText):
    textVal = (pathText or "").strip()

    # Strip common wrappers
    if (len(textVal) >= 2) and ((textVal[0] == '"' and textVal[-1] == '"') or (textVal[0] == "'" and textVal[-1] == "'")):
        textVal = textVal[1:-1].strip()

    # Normalize slashes to Windows style
    textVal = textVal.replace("/", "\\")

    # Strip leading .\ or ./
    if textVal.startswith(".\\"):
        textVal = textVal[2:]
    elif textVal.startswith("./"):
        textVal = textVal[2:]

    # Collapse any .. and .
    try:
        textVal = os.path.normpath(textVal)
    except Exception:
        # If normpath chokes on something odd, just keep the raw normalized slashes
        pass

    return textVal


def buildOpenFileList():
    # getFiles() returns a list of tuples:
    # (fullPath, bufferID, index, view)
    fileList = []
    for fileItem in notepad.getFiles():
        fullPath, buffId, tabIndex, tabView = fileItem
        fileList.append({
            "fullPath": fullPath,
            "buffId": buffId,
            "tabIndex": tabIndex,
            "tabView": tabView,
        })
    return fileList


def scoreMatch(queryNorm, pathNorm):
    # Higher is better. Return 0 for no match.
    queryLow = queryNorm.lower()
    pathLow = pathNorm.lower()

    if not queryLow:
        return 0

    # Exact full path match
    if pathLow == queryLow:
        return 1000000 + len(queryLow)

    # Strong match: path ends with query (best for partial relative paths)
    if pathLow.endswith(queryLow):
        return 800000 + len(queryLow)

    # Filename-only match: if query has no slashes, compare basename
    if ("\\" not in queryLow) and ("/" not in queryLow):
        baseLow = os.path.basename(pathLow)
        if baseLow == queryLow:
            return 600000 + len(queryLow)

    # Weaker match: substring anywhere
    if queryLow in pathLow:
        return 200000 + len(queryLow)

    return 0


def findBestTabBySelection():
    selText = editor.getSelText()
    if not selText or not selText.strip():
        notepad.messageBox("Select a partial file path first, then run the script.", "Switch tab by selected path")
        return

    queryNorm = normalizePath(selText)
    if not queryNorm:
        notepad.messageBox("Selection became empty after normalization.", "Switch tab by selected path")
        return

    openFiles = buildOpenFileList()

    bestScore = 0
    bestItem = None
    tiesList = []

    for fileItem in openFiles:
        fullPath = fileItem["fullPath"] or ""
        pathNorm = normalizePath(fullPath)

        matchScore = scoreMatch(queryNorm, pathNorm)
        if matchScore > bestScore:
            bestScore = matchScore
            bestItem = fileItem
            tiesList = [fileItem]
        elif matchScore == bestScore and matchScore > 0:
            tiesList.append(fileItem)

    # console.show()
    console.write("queryNorm = {0}\r\n".format(queryNorm))

    if bestScore <= 0 or bestItem is None:
        console.write("No matching open tab found.\r\n")
        notepad.messageBox("No matching open tab found for:\n\n{0}".format(queryNorm), "Switch tab by selected path")
        return

    # Tie-break: pick the shortest full path (usually the “closest” match)
    if len(tiesList) > 1:
        tiesList.sort(key=lambda item: len(item["fullPath"] or ""))
        bestItem = tiesList[0]
        console.write("Multiple matches found ({0}); picking shortest path.\r\n".format(len(tiesList)))

    notepad.activateBufferID(bestItem["buffId"])
    console.write("Switched to: {0}\r\n".format(bestItem["fullPath"]))


findBestTabBySelection()

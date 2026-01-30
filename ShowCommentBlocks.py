from Npp import editor

def unfold_all():
    line_count = editor.getLineCount()
    if line_count <= 0:
        return

    editor.beginUndoAction()
    try:
        i = 0
        while i < line_count:
            # If this line is a fold header and it's collapsed, expand it
            if editor.getFoldLevel(i) & 0x2000:
                if not editor.getFoldExpanded(i):
                    editor.toggleFold(i)
            i += 1
    finally:
        editor.endUndoAction()

unfold_all()

from Npp import editor

COMMENT_PREFIXES = (
    "//",
    "#",
    "--",
    ";",
    "/*",
    "*",
    "<!--"
)

TRIPLE_DELIMS = ('"""', "'''")

# Scintilla fold flags
SC_FOLDLEVELHEADERFLAG = 0x2000

def is_comment_line(line_text):
    s = line_text.lstrip()
    if s == "":
        return False
    for p in COMMENT_PREFIXES:
        if s.startswith(p):
            return True
    return False

def triple_start_delim(line_text):
    s = line_text.lstrip()
    for d in TRIPLE_DELIMS:
        if s.startswith(d):
            return d
    return None

def triple_end_found(line_text, delim):
    # treat delimiter appearing anywhere (after stripping) as a close marker
    s = line_text.lstrip()
    return (delim in s)

def is_fold_header(line_no):
    level = editor.getFoldLevel(line_no)
    return (level & SC_FOLDLEVELHEADERFLAG) != 0

def collapse_fold_header(line_no, collapsed_headers):
    if line_no < 0:
        return
    if line_no in collapsed_headers:
        return

    if is_fold_header(line_no) and editor.getFoldExpanded(line_no):
        editor.toggleFold(line_no)
        collapsed_headers.add(line_no)

def collapse_comment_block_folds():
    line_count = editor.getLineCount()
    if line_count <= 0:
        return

    collapsed_headers = set()

    editor.beginUndoAction()
    try:
        i = 0
        while i < line_count:
            line = editor.getLine(i)

            # 1) Triple-quoted block
            delim = triple_start_delim(line)
            if delim is not None:
                start = i

                # If opener and closer are on the same line, skip
                s = line.lstrip()
                opener_idx = s.find(delim)
                closer_idx = s.find(delim, opener_idx + len(delim))
                if closer_idx != -1:
                    i += 1
                    continue

                i += 1
                while i < line_count and not triple_end_found(editor.getLine(i), delim):
                    i += 1

                end = min(i, line_count - 1)

                collapse_fold_header(start, collapsed_headers)

                i = end + 1
                continue

            # 2) Consecutive single-line comment block
            if is_comment_line(line):
                start = i
                i += 1
                while i < line_count and is_comment_line(editor.getLine(i)):
                    i += 1
                end = i - 1

                collapse_fold_header(start, collapsed_headers)

                continue

            i += 1
    finally:
        editor.endUndoAction()

collapse_comment_block_folds()

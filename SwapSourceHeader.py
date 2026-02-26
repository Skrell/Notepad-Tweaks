import os
import re
import time

currentFile = notepad.getCurrentFilename().rsplit('.', 1)
dir_path = os.path.dirname(os.path.realpath(notepad.getCurrentFilename()))
filename_noext = ((os.path.basename(notepad.getCurrentFilename())).rsplit('.', 1))[0]
ext = currentFile[1].lower()
org_depth = len(dir_path.split('\\'))
TOTAL_DEPTH_UP = 3
TOTAL_DEPTH_DOWN = 8 + TOTAL_DEPTH_UP
killme = False

wordSelected = editor.getSelText()
lineNumSelected = editor.lineFromPosition(editor.getCurrentPos())

functionDef = False
headerDef = False

def SearchForFileWithBaseClass(baseClass = "none"):
    if (baseClass == "none"):
        return
    print str(baseClass).strip()
    TOTAL_DEPTH_UP = 6
    TOTAL_DEPTH_DOWN = 8 + TOTAL_DEPTH_UP
    global dir_path
    global org_depth
    searchTerms  = r'^\s*((class\s+)|(struct\s+))' + r'\b' + str(baseClass).strip() + r'\b' + r'(?!.*;)'
    for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
        filenames = [ fi for fi in filenames if fi.endswith(".h") ]
        filenames.sort()
        for filename in filenames:  
            current_file = os.path.join(root, filename)
            current_file_depth = len(current_file.split('\\'))
            if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                continue
            else:
                if os.path.exists(current_file): 
                    with open(current_file, 'r') as read_obj:
                        # Read all lines in the file one by one
                        for idx, line in enumerate(read_obj):
                            if re.search(searchTerms, line):
                                print current_file
                                return current_file
                            
def FindBaseClassName():
    global lineNumSelected
    lineIndex = lineNumSelected
    searchTerms = r'^\s*(?!/)(\bclass\b|\bstruct\b)\s+\w+.*public\s+(virtual\s+)?(\w+::)?(\w+)'
    current_file = os.path.realpath(notepad.getCurrentFilename())
    
    fileArray = open(curren_file, 'r').readlines()
    
    while (lineIndex > 0):
        if re.search(searchTerms,fileArray[lineIndex]):
            baseClass = re.sub(searchTerms, r'\4', fileArray[lineIndex])
            if baseClass:
                return baseClass.rstrip()        
        lineIndex -= 1
    return ""
    
def ScrollToAttributeDef(stopLine = 0, isFunction = False, searchingHeader = False):
    searchTerms = r'^\s*(?!/)(?!return)(static\s+)?(const\s+)?((\w+::){1,3})?(\w+(<.*>)?\s+)?(\w+(<.*>)?\s+)(\*|&)?\s*\b' + wordSelected + r'\b.*;'
    if (wordSelected):
        current_file = os.path.realpath(notepad.getCurrentFilename())
        print (current_file, stopLine, isFunction, searchingHeader)
        if os.path.exists(current_file):
            with open(current_file, 'r') as read_obj:
                print "Read all lines in the file one by one"
                for idx, line in enumerate(read_obj):
                    if stopLine > 0 and idx+1 == stopLine:
                        print "hit stopline"
                        return False
                    elif headerDef and isFunction and wordSelected.replace(" ", "") in line.replace(" ", ""): #remove all spaces
                        time.sleep(.300)
                        editor.gotoLine(0)
                        editor.lineScroll(0,idx - (editor.linesOnScreen()/2))
                        editor.gotoLine(idx)
                        return True
                    elif isFunction and ("::" + wordSelected.replace(" ", "")) in line.replace(" ", ""): #remove all spaces
                        time.sleep(.300)
                        editor.gotoLine(0)
                        editor.lineScroll(0,idx - (editor.linesOnScreen()/2))
                        editor.gotoLine(idx)
                        return True
                    elif not isFunction and searchingHeader and re.search(r'\b' + wordSelected + r'\b', line):
                        time.sleep(.300)
                        editor.gotoLine(0)
                        editor.lineScroll(0,idx - (editor.linesOnScreen()/2))
                        editor.gotoLine(idx)
                        print "looking for word"
                        return True
    return False

def SearchForOtherFile():
    global dir_path
    global filename_noext
    global ext
    global org_depth
    global wordSelected
    killme = False
    print "Looking further..."
    if 'c' in ext:
        for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
            filenames.sort()
            for filename in filenames:  
                current_file = os.path.realpath(os.path.join(root, filename))
                current_file_depth = len(current_file.split('\\'))
                if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                    # print ("I give up! ")
                    # print (current_file_depth-org_depth)
                    continue
                else:
                    # print (os.path.join(root, filename))
                    if filename.lower() == (filename_noext.lower()+'.h'):
                        notepad.open(os.path.join(root, filename))
                        ScrollToAttributeDef()
                        killme = True
                        return killme
    else: #file is a header file and hence we're looking for its cpp
        for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
            for filename in filenames:  
                filenames.sort()
                current_filepath = os.path.realpath(os.path.join(root, filename))
                # print current_filepath
                current_file = filename.rsplit('.', 1)
                if (len(current_file) > 1):
                    current_ext = current_file[1].lower()
                    # print current_ext
                    current_file_depth = len(current_filepath.split('\\'))
                    if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                        # print ("I give up! ")
                        # print (current_file_depth-org_depth)
                        continue
                    else:
                        # print (os.path.join(root, filename))
                        if (current_file[0].lower() == filename_noext.lower() and current_ext in [ 'cpp', 'c', 'cc', 'h' ]):
                            notepad.open(os.path.join(root, filename))
                            killme = True
                            return killme
                        else:
                            continue
    return killme

console.clear()    
print (dir_path)
print (filename_noext)
print (ext)
print (org_depth)
if (wordSelected):
    if wordSelected.find("(") != -1: #found a function def
        functionDef = True
    wordSelected = wordSelected.rstrip(";")
    # wordSelected = wordSelected.replace("::", "")
    wordSelected = wordSelected.replace("override", "")
    print (wordSelected)

if (currentFile):
    if ext in [ 'cpp', 'c', 'cc', 'h' ]:
        all_except_ext = currentFile[0]
        if ('h' in ext and wordSelected and ScrollToAttributeDef(lineNumSelected, functionDef)):
            print "found it!"
            print "DONE!"
        else:
            if 'c' in ext:
                assoc_file = all_except_ext + '.h'
            else:
                assoc_file = all_except_ext + '.c'
                if not os.path.exists(assoc_file): 
                    assoc_file = all_except_ext + '.cpp'
                    if not os.path.exists(assoc_file): 
                        assoc_file = all_except_ext + '.cc'
            if os.path.exists(assoc_file): 
                notepad.open(assoc_file)
                print("Opened: ", assoc_file)
                if (wordSelected):
                    if (ScrollToAttributeDef(0, functionDef, ext != 'h')):
                        print "found it!"
                        print "DONE!2"
                    elif not functionDef and headerDef:
                        print "attribute not found, looking for base class def..."
                        base = FindBaseClassName()
                        print("Base class name is ", base)
                        if base:
                            foundFile = SearchForFileWithBaseClass(FindBaseClassName())
                            if (foundFile):
                                notepad.open(foundFile)
                                if (ScrollToAttributeDef()):
                                    print "found it!"
                                else:
                                    foundFile = SearchForFileWithBaseClass(FindBaseClassName())
                                    if (ScrollToAttributeDef(0, functionDef, ext != 'h')):
                                        print "found it 2 levels in!"
                                    else:
                                        console.show()
                                        console.writeError("Found the class but not the member...DONE")
                            else:
                                print "can't find a file with the base class definition!"
                        else:
                            notepad.open(currentFile[0] + "." + currentFile[1])
                            console.show()
                            console.writeError("FAILED to find base class to search")
                else:
                    print "found it!"
            else:
                if (SearchForOtherFile() == False):
                    console.show()
                    console.writeError("No accompanying file found")
                else:
                    ScrollToAttributeDef(0, functionDef, ext != 'h')
                    print "found it after searching!"
    else:
        console.show()
        console.writeError("UNSUPPORTED FILE TYPE")     
else:
    console.show()
    console.writeError("ERROR")     
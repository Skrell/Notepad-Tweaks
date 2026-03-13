# -*- coding: utf-8 -*-
# The lines up to and including sys.stderr should always come first
# Then any errors that occur later get reported to the console
# If you'd prefer to report errors to a file, you can do that instead here.
import sys
from Npp import *
import os
import time
import DoubleClickCloseSearchResults
import BracketHighlighterEdit
# Set the stderr to the normal console as early as possible, in case of early errors
sys.stderr = console

# Define a class for writing to the console in red
class ConsoleError:
	def __init__(self):
		global console
		self._console = console;

	def write(self, text):
		self._console.writeError(text);

# Set the stderr to write errors in red
sys.stderr = ConsoleError()

# This imports the "normal" functions, including "help"
import site

sys.stdout = console
current_directory = os.getcwd()
print(current_directory)



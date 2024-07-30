"""
================================================================================================================
Text Edit Redirector for PyQt6
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Copyright (C) 2024 George H. Allison
    Contact: ghallison1@sheffield.ac.uk or xinshan.li@sheffield.ac.uk
----------------------------------------------------------------------------------------------------------------

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

________________________________________________________________________________________________________________
"""

import queue
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import QTimer


class TextEditRedirector:
    # Redirects stdout and stderr to a QTextEdit widget.
    def __init__(self, log_text_edit, stream):
        """
        Redirects stdout and stderr to a QTextEdit widget.
        :param log_text_edit:  widget
        :param stream:  sys.stdout or sys.stderr
        """
        self.log_text_edit = log_text_edit
        self.stream = stream
        self.max_lines = 1000  # Maximum number of lines to keep in the text edit
        self.queue = queue.Queue()  # Queue to hold text before it is written to the text edit

        self.timer = QTimer()  # Timer to periodically check the queue
        self.timer.timeout.connect(self.update_text_edit)  # Call update_text_edit every 100 ms
        self.timer.start(100)  # Start the timer

    def write(self, text):
        """
        Write text to the text edit.
        :param text:  text to write
        """
        self.queue.put(text)  # Put the text into the queue
        self.stream.write(text)  # Write the text to the original stream

    def update_text_edit(self):
        # Update the text edit with the queued text.
        while not self.queue.empty():  # While there is text in the queue
            text = self.queue.get()  # Get the text from the queue

            cursor = self.log_text_edit.textCursor()  # Get the text cursor
            cursor.movePosition(QTextCursor.MoveOperation.End)  # Move the cursor to the end of the text edit
            cursor.insertText(text)  # Append a newline character

            # Remove lines at the beginning if we have too many lines
            while self.log_text_edit.document().blockCount() > self.max_lines:
                cursor.movePosition(QTextCursor.MoveOperation.Start)  # Move the cursor to the start of the text edit
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)  # Select the line under the cursor
                cursor.removeSelectedText()  # Remove the selected text

            self.log_text_edit.setTextCursor(cursor)  # Set the text
            self.log_text_edit.ensureCursorVisible()  # Ensure the cursor is visible

    def flush(self):
        self.stream.flush()  # Flush the stream

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IPython Qt Console

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier, Aranuvir

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.



Abstract
--------

Ipython qtconsole for embedding in MakeHuman
"""


from core import G
import getpath
import gui
import os
import traceback

# Import the console machinery from ipython
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.jupyter_widget import styles
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

from PyQt5 import QtWidgets, QtCore

# Import the utility script
try:
    from . import my_utility
    utility_functions = my_utility.utility_functions
except ImportError:
    utility_functions = {}
    print("Warning: Could not load utility script")

class _QIPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget.
    We can replace the standard banner using the customBanner argument"""
    def __init__(self, customBanner=None, *args, **kwargs):
        if customBanner!=None:
            self.banner=customBanner

        super(_QIPythonWidget, self).__init__(*args,**kwargs)

        # Embed the kernel within the event loop and expose the application
        # context
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()
        self.exit_requested.connect(stop)

    def pushVariables(self, variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()

    def printText(self, text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)

    def executeCommand(self, command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)


class IPythonConsoleWidget(QtWidgets.QWidget, gui.Widget):
    """ An interactive shell widget using the ipython qt console """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.ipyConsole = _QIPythonWidget(customBanner="Welcome to MakeHuman's embedded Jupyter console\n")

        self.set_theme(G.app.theme)

        layout.addWidget(self.ipyConsole)

        # Expose variables to the console
        exposed_variables = {
            'G': G,
            **utility_functions  # Add utility functions to the namespace
        }
        self.ipyConsole.pushVariables(exposed_variables)
        self.ipyConsole.printText("The variable 'G' allows access to the MakeHuman application. Use the 'whos' command for information.")
        if utility_functions:
            self.ipyConsole.printText("\nAvailable utility functions:")
            for func_name in utility_functions.keys():
                self.ipyConsole.printText(f"- {func_name}")
            self.ipyConsole.printText("\n") # Add newline

        # --- Schedule character_creator.py execution after a delay ---
        # Delay in milliseconds (e.g., 1000ms = 1 second)
        delay_ms = 1000 
        QtCore.QTimer.singleShot(delay_ms, self.execute_character_script)
        self.ipyConsole.printText(f"--- Scheduling character_creator.py execution in {delay_ms / 1000.0} seconds... ---\n")
        # ------------------------------------------------------------

    def execute_character_script(self):
        """Reads and executes the character_creator.py script in the console."""
        self.ipyConsole.printText(f"--- Executing character_creator.py now... ---\n")
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'character_creator.py')
            if os.path.exists(script_path):
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                # Prepare command: script content + main() call
                command_to_execute = script_content + "\n\nmain()"
                
                self.ipyConsole.executeCommand(command_to_execute)
            else:
                self.ipyConsole.printText(f"\n--- Warning: character_creator.py not found at {script_path} ---")
                
        except Exception as e:
            self.ipyConsole.printText(f"\n--- Error executing character_creator.py ---\n")
            self.ipyConsole.printText(traceback.format_exc())

    def onThemeChanged(self, event):
        self.set_theme(G.app.theme)

    def set_theme(self, theme):
        """ Set the theme of the terminal and syntax highlighting.
        """

        ipy_stylesheet_path = getpath.getSysDataPath('themes/%s_console.css' % theme)
        try:
            with open(ipy_stylesheet_path, 'r', encoding='utf-8') as css_file:
                stylesheet = css_file.read()
        except IOError:
            # No file to load, use default theme
            stylesheet = styles.default_light_style_sheet

        # TODO not working yet (causes a crash for some reason)

        self.ipyConsole.syntax_style = "default"

        self.ipyConsole.style_sheet = stylesheet

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.ipyConsole.pushVariables(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self.ipyConsole.clearTerminal()

    def printText(self, text):
        """ Prints some plain text to the console """
        self.ipyConsole.printText(text)

    def executeCommand(self, command):
        """ Execute a command in the frame of the console widget """
        self.ipyConsole.executeCommand(command)

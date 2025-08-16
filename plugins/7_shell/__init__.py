#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
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
----------

Plugin loader for the embedded Python Shell utility.
"""
from .shell import ShellTaskView
from PyQt5 import QtCore, QtGui
from core import G
import gui3d
import mh
import gui
import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ShellTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(ShellTaskView, self).__init__(category, 'Shell')
        
    def run_character_creator(self):
        try:
            # Add the current directory to Python path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.append(current_dir)
            
            # Now import and run character creator
            import character_creator
            character_creator.main()
            
            # After character creation is complete, hide the window
            hide_window()
            
        except Exception as e:
            print(f"Error running character creator: {str(e)}")

def hide_window():
    if hasattr(G.app, 'mainwin') and G.app.mainwin:
        win = G.app.mainwin
        # Disable window restoration
        win.setAttribute(Qt.WA_DontCreateNativeAncestors)
        win.setAttribute(Qt.WA_NativeWindow)
        
        # Set window flags to prevent showing in dock/taskbar
        win.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        # Set window opacity to 0
        win.setWindowOpacity(0)
        
        # Move off screen and make tiny
        screen = QApplication.primaryScreen()
        if screen:
            win.move(screen.geometry().width() + 10000, screen.geometry().height() + 10000)
        win.resize(1, 1)
        
        # Ensure it's hidden
        win.hide()
        
        # Force the application to quit after a short delay
        QtCore.QTimer.singleShot(1000, G.app.quit)

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(ShellTaskView(category))
    
    # Run character creator after a short delay to let the application initialize
    QtCore.QTimer.singleShot(2000, taskview.run_character_creator)

def unload(app):
    pass
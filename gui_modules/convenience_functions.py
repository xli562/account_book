import time, datetime, threading, importlib.util, random, pickle, os, logging, numpy

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from modules import constants




def toggle_visibility(item, visibility:bool):
    '''works for both widgets and layouts.'''
    widget = None
    layout = None

    # If the item is a direct QWidget or QLayout
    if isinstance(item, QWidget):
        widget = item
    elif isinstance(item, QLayout):
        layout = item

    # If the item is a QLayoutItem
    if isinstance(item, QLayoutItem):
        widget = item.widget()
        layout = item.layout()

    # Handle widget visibility
    if widget:
        if visibility:
            widget.show()
        else:
            widget.hide()

    # Recursively handle layout items
    if layout:
        for i in range(layout.count()):
            next_item = layout.itemAt(i)
            toggle_visibility(next_item, visibility)


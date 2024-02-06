# -*- coding: utf-8 -*-

# IMPORTS
from datetime import datetime as date

from logsConstants import *

def printError(type, message, lvl=ERROR):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    #TODO

def printWarn(type, message, lvl=WARN):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    #TODO

def printInfo(type, message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    #TODO

def printModifs(type, message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    #TODO

def printLogs(type, message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    #TODO

def printFormat(message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    #TODO

def erase():
    return

def getCurrentDate():
    return date.now().strftime("%d/%m %Hh%M")

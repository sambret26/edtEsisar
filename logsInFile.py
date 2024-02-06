# -*- coding: utf-8 -*-

# IMPORTS
from datetime import datetime as date
from dotenv import load_dotenv
import os

from logsConstants import *

load_dotenv()

def printError(type, message, lvl=ERROR):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    path = os.environ.get("PATH_ERROR")
    write(path, formattedMessage)
    printWarn(type, message, lvl)

def printWarn(type, message, lvl=WARN):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    path = os.environ.get("PATH_WARN")
    write(path, formattedMessage)
    printInfo(type, message, lvl)

def printInfo(type, message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    path = os.environ.get("PATH_INFO")
    write(path, formattedMessage)
    printLogs(type, message, lvl)

def printModifs(type, message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    path = os.environ.get("PATH_MODIFS")
    write(path, formattedMessage)
    printInfo(type, message, lvl)

def printLogs(type, message, lvl=INFO):
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    path = os.environ.get("PATH_LOGS")
    write(path, formattedMessage)

def printFormat(message, lvl=INFO):
    type = MAJ
    formattedMessage = f"{getCurrentDate()} {type} {lvl} {message}\n"
    path = os.environ.get("PATH_OUT")
    write(path, formattedMessage)
    printLogs(type, message, lvl)

def printDB(message):
    formattedMessage = f"{getCurrentDate()} {message}\n"
    path = os.environ.get("PATH_DB")
    write(path, formattedMessage)

def erase():
    open(os.environ.get('PATH_OUT'), "w").close()

def write(path, message):
    with open(path, 'a') as f:
        f.write(message)

def getCurrentDate():
    return date.now().strftime("%d/%m %Hh%M:%S")

# -*- coding: utf-8 -*-

# IMPORTS
from datetime import datetime as date
from datetime import timedelta
import pickle
import os


# Returns the value of the file associated with the given name
def load(name):
  with open('DB/' + name + '.pkl', 'rb') as f:
    return pickle.load(f)


# Print the date and the message on the files logs/out.txt and logs/logs.txt
def printFormat(message):
  printLogs(message)
  currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M : "))
  newMessage = f"{currentDate}{message}\n"
  with open("./logs/out.txt", 'a') as f:
    f.write(newMessage)


# Print the date and the message on the file logs/logs.txt
def printLogs(message):
  currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M : "))
  newMessage = f"{currentDate}{message}\n"
  with open("./logs/logs.txt", 'a') as f:
    f.write(newMessage)


# Erase the content of the file logs/out.txt
def erase():
  open("./logs/out.txt", "w").close()


# Returns the current date, with an offset if necessary (c.f. jetlag)
def getCurrentDate():
  offset = 0
  if "REPLIT" in os.environ:
    offset = 2
  return date.now() + timedelta(seconds=3600 * offset)

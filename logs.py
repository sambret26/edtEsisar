# -*- coding: utf-8 -*-

# IMPORTS
from functions import getCurrentDate

# CONST

MAJ = "[MAJ]"
DB = "[DB ]"
CAL = "[CAL]"

INFO = "[INFO ]"
WARN = "[WARN ]"
ERROR = "[ERROR]"


# Print the date and the message on the files logs/out.txt and logs/logs.txt
def printFormat(message):
  printLogs(MAJ, INFO, message)
  currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M"))
  formattedMessage = "{} : {}\n".format(currentDate, message)
  with open("./logs/out.txt", 'a') as f:
    f.write(formattedMessage)


# Print the date and the message on the file logs/logs.txt
def printLogs(type1, type2, message):
  currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M"))
  formattedMessage = "{} : {} {} {}\n".format(currentDate, type1, type2,
                                              message)
  with open("./logs/logs.txt", 'a') as f:
    f.write(formattedMessage)


# Erase the content of the file logs/out.txt
def erase():
  open("./logs/out.txt", "w").close()

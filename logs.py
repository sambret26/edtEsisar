# -*- coding: utf-8 -*-

# IMPORTS
from functions import getCurrentDate
from dotenv import load_dotenv
import os


load_dotenv()


# CONST

MAJ = os.environ.get('MAJ')
DB = os.environ.get('DB')
CAL = os.environ.get('CAL')

INFO = os.environ.get('INFO')
WARN = os.environ.get('WARN')
ERROR = os.environ.get('ERROR')


# Print the date and the message on the files logs/out.txt and logs/logs.txt
def printFormat(message):
  printLogs(MAJ, INFO, message)
  #currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M"))
  #formattedMessage = "{} : {}\n".format(currentDate, message)
  #with open(os.environ.get('PATH_OUT'), 'a') as f:
    #f.write(formattedMessage)


# Print the date and the message on the files logs/modifs.txt and logs/logs.txt
def printModifs(type1, type2, message):
  printLogs(type1, type2, message)
  currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M"))
  formattedMessage = "{} : {}\n".format(currentDate, message)
  #with open(os.environ.get('PATH_MODIFS'), 'a') as f:
    #f.write(formattedMessage)


# Print the date and the message on the file logs/logs.txt
def printLogs(type1, type2, message):
  currentDate = str(getCurrentDate().strftime("%d/%m %Hh%M"))
  formattedMessage = "{} : {} {} {}\n".format(currentDate, type1, type2,
                                              message)
  #with open(os.environ.get('PATH_LOGS'), 'a') as f:
    #f.write(formattedMessage)
  print(formattedMessage)

# Erase the content of the file logs/out.txt
def erase():
  open(os.environ.get('PATH_OUT'), "w").close()
  return

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


# Returns the current date, with an offset if necessary (c.f. jetlag)
def getCurrentDate():
  offset = 0
  if "REPLIT" in os.environ:
    offset = 1
  return date.now() + timedelta(seconds=3600 * offset)


# Returns the same date with one years less
def getLastYear(date):
  d = list(str(date))
  d[3] = str(int(d[3]) - 1)
  newDate = ''.join(d)
  return newDate

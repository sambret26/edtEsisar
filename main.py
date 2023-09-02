# -*- coding: utf-8 -*-

# IMPORTS
import sys

sys.path.append("modules")
from datetime import datetime as date
from logs import printFormat, erase
import timetable
import time
import os

# KEEPING ALIVE (en cas de deploiement sur replit)
if "REPLIT" in os.environ:
  import keep_alive
  keep_alive.keep_alive()


# RECURING TASKS
def recurring_task():
  erase()
  timetable.update()
  while 1:
    if int(date.now().strftime("%M")) % 15 == 0:
      printFormat("Mise à jour des agendas")
      timetable.update()
    time.sleep(60)


# START
recurring_task()

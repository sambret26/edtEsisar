# -*- coding: utf-8 -*-

# IMPORTS
import sys

sys.path.append("modules")
from logs import printFormat, erase
import timetable
import schedule
import time
import os

# KEEPING ALIVE (en cas de deploiement sur replit)
if "REPLIT" in os.environ:
  import keep_alive
  keep_alive.keep_alive()


# RECURING TASKS
def recurring_task():
  printFormat("Mise à jour des agendas")
  timetable.update()


# MAIN
def main():
  erase()
  timetable.update()
  schedule.every().hours.at(":00").do(recurring_task)
  schedule.every().hours.at(":15").do(recurring_task)
  schedule.every().hours.at(":30").do(recurring_task)
  schedule.every().hours.at(":45").do(recurring_task)
  while 1:
    schedule.run_pending()
    time.sleep(10)


# START
main()

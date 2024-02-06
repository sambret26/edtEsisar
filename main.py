# -*- coding: utf-8 -*-

# IMPORTS
import sys

sys.path.append("modules")

from dotenv import load_dotenv
import schedule
import time
import os

import timetable

load_dotenv()

logsTypes = os.environ.get("LOGS")
if (logsTypes and logsTypes == "FILES"):
    from logsInFile import printFormat, erase
elif (logsTypes and logsTypes == "DB"):
    from logsInDB import printFormat, erase
else :
    from noLogs import printFormat, erase

# RECURING TASKS
def recurring_task():
    printFormat("Mise à jour des agendas")
    timetable.update()

# MAIN
def main():
    erase()
    recurring_task()
    schedule.every().hours.at(":00").do(recurring_task)
    schedule.every().hours.at(":15").do(recurring_task)
    schedule.every().hours.at(":30").do(recurring_task)
    schedule.every().hours.at(":45").do(recurring_task)
    while 1:
        schedule.run_pending()
        time.sleep(10)

# START
main()

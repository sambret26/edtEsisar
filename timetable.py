# -*- coding: utf-8 -*-

# IMPORTS
from functions import getCurrentDate
from logs import printLogs
import threading
import logs
import cal
import DB


# Update start a thread for evry area
# Each thread call the run function to update the given area
def update():
  printLogs(logs.MAJ, logs.INFO, "Update")
  areaList = DB.getAreaList()
  threads = []
  for area in areaList:
    threads.append(threading.Thread(target=run, args=(area, )))
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()
  printLogs(logs.MAJ, logs.INFO, "End of update\n")


# Run update the calendar of a given area
# 4 steps :
# 1) Update the database from the events in the calendar (updateDatabaseFromCalendar)
# 2) Get the event on the ginp website (cal.getEvents)
# 3) Update the database with those events (updateDatabase)
# 4) Update the calendar with the database (updateCalendar)
def run(area):
  printLogs(logs.MAJ, logs.INFO, "Update {}".format(area))
  urlId = DB.getId(area)
  updateDatabaseFromCalendar(area)
  eventsList = cal.getEvents(urlId)
  if eventsList != [] and not "invalid" in eventsList[0]:
    updateDatabase(eventsList, area)
    updateCalendar(area)
  printLogs(logs.MAJ, logs.INFO, "End of update {}".format(area))


# This is the 3rd step of the "run" function
# There is 4 steps to update the db :
# 1) Set all events to Unfind ()
# 2) Browse all events and see if there are in database
# 3) Set flags Past = 1 for completed events
# 4) Add the number of events in database
def updateDatabase(eventsList, area):
  DB.setEventsToUnfind(area)
  browseEvents(eventsList, area)
  checkPastEvents(area)
  addNumber(area)


# This is the 4th step of the "run" function
# There is 3 steps to update the calendar :
# 1) Insert in the calendar all events with flag ToAdd = 1
# 2) Delete canceled events (in calendar AND database) (Flag ToRemove = 1)
# 3) Remove completed events (only in calendar) (flag Past = 1)
def updateCalendar(area):
  insertEvents(area)
  deleteEvents(area)
  removePastEvents(area)


# This function flaged Find = 1 to event already in calendar
# Every new event is add in database and flag with ToAdd = 1
def browseEvents(eventsList, area):
  printLogs(logs.MAJ, logs.INFO, "Browsing events for {}".format(area))
  for calEvent in eventsList:
    values = calEvent.split("\n")
    event = {
      "Start": "",
      "End": "",
      "SimplyEnd": 0,
      "Subject": "",
      "Type": "",
      "Room": "",
      "Teacher": "",
      "Description": "",
      "Color": "",
      "CalId": "None",
      "Number": 0,
      "Total": 0
    }
    ok = False
    for line in values:
      if ("DTSTART") in line: start = dtStart(line)
      elif ("DTEND") in line: end = dtEnd(line)
      elif ("SUMMARY") in line: event["Subject"] = summary(line)
      elif ("LOCATION") in line: event["Room"] = location(line)
      elif ("DESCRIPTION") in line:
        event["Description"], event["Type"], ok, event["Color"], event[
          "Teacher"] = description(line, event["Subject"], event["Room"])
    if not ok: continue
    event["Start"] = realDate(start)
    event["End"] = realDate(end)
    event["SimplyEnd"] = end
    (id, past, calId) = DB.searchEventInDatabase(area, event)
    if not id:
      DB.addEvent(area, event)
    else:
      DB.setEventToFind(id, calId)


# This function change the status of completed event always in the calendar
# If the "Past" flag is not set but the event is completed, this flag is set
# If this event is always in calendar, it is flag with ToRemove = 1
def checkPastEvents(area):
  printLogs(logs.MAJ, logs.INFO, "Checking past events for {}".format(area))
  currentDate = int(getCurrentDate().strftime("%y%m%d%H%M"))
  events = DB.getIdCalIdPastSimplyEnd(area)
  for event in events:
    if not (event[2]) and int(event[3]) <= currentDate:
      if event[1] == "None": toRemove = 0
      else: toRemove = 1
      DB.setPastToRemoveToAdd(toRemove, event[0], event[1])


# This function add the number and the total of every concerned event in database
# All type founds are selected (ex of type : "CM MA202"/"TP EE312")
# Every event of eah type are sorted, and a number is add
# It allows to put something like : "2/26" in the description of the event
def addNumber(area):
  printLogs(logs.MAJ, logs.INFO, "Adding number for {}".format(area))
  types = DB.getTypes(area)
  for type in types:
    values = (type[0], area)
    events = DB.getIdSimplyEndCalId(values)
    sortedEvents = sorted(events, key=lambda sub: (sub[1]))
    total = len(sortedEvents)
    number = 1
    for event in sortedEvents:
      values = (number, total, event[0])
      DB.setNumbers(values, event[2])
      number += 1


# This function retrieves all events to create within a specified area (indicated by 'ToAdd = 1')
# All thoses events are create in the calendar ans the new Id is store in database
def insertEvents(area):
  printLogs(logs.MAJ, logs.INFO, "Inserting events for {}".format(area))
  events = DB.getEventsToAdd(area)
  sortedEvents = sorted(events, key=lambda sub: (sub[5]))
  for event in sortedEvents:
    calEvent = {
      "Start": event[3],
      "End": event[4],
      "SimplyEnd": event[5],
      "Subject": event[6],
      "Type": event[7],
      "Room": event[8],
      "Teacher": event[9],
      "Description": event[10],
      "Color": event[11],
      "Number": event[12],
      "Total": event[13]
    }
    calId = cal.createEvent(area, calEvent)
    DB.setToAdd(calId, event[0])


# This function retrieves all canceled events within a specified area (indicated by 'Find = 0')
# All thoses events are removed from calendar (if they are in) AND database
def deleteEvents(area):
  printLogs(logs.MAJ, logs.INFO, "Deleting events for {}".format(area))
  events = DB.getCalIdUnfind(area)
  for calId in events:
    if calId == "None" or cal.deleteEvent(area, calId):
      DB.deleteEvent(area, calId)


# This function retrieves all pasts events within a specified area (indicated by 'ToRemove = 1')
# All thoses events are remove from calendar and Flaged with Past =  and CalId = "None" in database
def removePastEvents(area):
  printLogs(logs.MAJ, logs.INFO, "Removing pasts events for {}".format(area))
  events = DB.getIdCalIdToRemove(area)
  for event in events:
    if cal.deleteEvent(area, event[1]):
      DB.setPastToRemoveCalId(event[0])


# This function parse the date
# From DTEND:aaaammjjThhmmssZ
# To aammjjhhmm
# And add the GMT jetLag
def dtEnd(event):
  l = list(event)
  date = int(''.join(map(str, l[8:14])) + ''.join(map(str, l[15:19])))
  return jetLag(date)


# This function parse the date
# From DTSTART:aaaammjjThhmmssZ
# To aammjjhhmm
# And add the GMT jetLag
def dtStart(event):
  l = list(event)
  date = int(''.join(map(str, l[10:16])) + ''.join(map(str, l[17:21])))
  return jetLag(date)


# This function give an offset to the date depending of the date and the GMT
def jetLag(date):
  dateWithoutYear = int(str(date)[2:])
  if dateWithoutYear > 3310200 and dateWithoutYear < 10290300: date += 200
  else: date += 100
  return date


# This function extract the subject from the summary line
def summary(event):
  subject = (event.split(":"))[1]
  if '-' in subject and not 'Demi' in subject:
    subject = subject.split('-')[0]
  return subject


# This function extract the room from the location line
def location(event):
  room = (event.split(':'))[1]
  room = room.replace(" (V)", "")
  room = room.replace("_CM", "")
  room = room.replace("-optique", "")
  room = room.replace("\, ", " ou ")
  room = room.replace("\,", " ou ")
  return room


# This function extract the type and the teacher from the description line
def description(event, subject, room):
  ok = True
  if "rattrap" in subject or "1/3" in subject or "AC311" in subject: ok = False
  description = event.split("\\n")
  description[2] = description[2].replace("STD", "S1")
  if ("Examen") in subject: type = "Exam"
  elif ("CM") in description[2]: type = "CM"
  elif ("TDM") in description[2]: type = "TDM"
  elif ("TD") in description[2]: type = "TD"
  elif ("TP") in description[2]: type = "TP"
  elif ("HA") in description[2]: type = "HA"
  elif ("DS") in description[2]: type = "DS"
  else: type = ""
  teacher = description[3]
  if teacher == "* Surveillant": type, teacher = "CC", '('
  if teacher == "*": teacher = '('
  if type != "":
      description = "{} de {}".format(type, subject)
      returnType = "{} {}".format(type, subject)
  else:
      description = subject
      returnType = subject
  if not '(' in teacher: description += (" avec " + teacher)
  if room != '' and room != '*': description += (" en " + room)
  if type == "CM": color = 10  #Vert (Basilic)
  elif type == "TD": color = 9  #Bleu (Myrtille)
  elif type == "TDM": color = 6
  elif type == "TP": color = 11  #Rouge (Tomate)
  elif type == "": color = 3  #Violet (Raisin)
  elif type in ["Exam", "DS"]: color = 5  #Jaune (Banane)
  else: color = 8
  return description, returnType, ok, color, teacher


# This function parse the date
# From : aammjjhhmm
# To : 20aa-mm-jjThh:mm:00
def realDate(date):
  d = list(str(date))
  newDate = "20{}{}-{}{}-{}{}T{}{}:{}{}:00".format(d[0], d[1], d[2], d[3],
                                                   d[4], d[5], d[6], d[7],
                                                   d[8], d[9])
  return newDate


def changeDate(date):
  before = str(date[0:11])
  during = str(date[11:13])
  after = str(date[13:19])
  new = str(int(during) + 1)
  if len(new) == 1: new = '0' + new
  newDate = "{}{}{}".format(before, during, after)  # TODO
  return newDate


# This function have in param an event
# If this event is finish (the end date is passed) it returns True
# If not, it return False
def isOver(event):
  currentDate = int(getCurrentDate().strftime("%y%m%d%H%M"))
  d = event["End"]
  endDate = int(d[2] + d[3] + d[5] + d[6] + d[8] + d[9] + d[11] + d[12] +
                d[14] + d[15])
  return endDate <= currentDate


# This function is use in very special case
# For exemple, if someone move handly an event on the calendar
# This event has to be re-placed
# This function look every events in the calendar
# If this event is in the database :
# It check if every field is ok
# If no, the field of the database are used to re-placed this event
# If this  event is not in database
# If it's finish it's delete
# If not, nothing happend.
# Maybe a good idea to put it in db ? Let's thing about it ...
def updateDatabaseFromCalendar(area):
  printLogs(logs.MAJ, logs.INFO, "Updating in reverse for {}".format(area))
  DB.setCurrentEventsToUnfind(area)
  listEventsOnCalendar = cal.getCalendarEvents(area)
  listEventsOnDatabase = DB.getCalId(area)
  for calEvent in listEventsOnCalendar:
    if calEvent["id"] in listEventsOnDatabase:
      (id, sd2, ed2, s2, d, c2, n, t) = DB.getInfo(area, calEvent["id"])
      if s2.startswith("Exam "): s2 = s2[5:]
      c2 = str(c2)
      if t != 0:
        d2 = "{} ({}/{})".format(d, n, t)
      else:
        d2 = d
      sd1 = str(calEvent["start"]["dateTime"][0:19])
      if calEvent["start"]["dateTime"][19] == "Z":
        sd1 = changeDate(calEvent["start"]["dateTime"])
      ed1 = str(calEvent["end"]["dateTime"][0:19])
      if calEvent["end"]["dateTime"][19] == "Z":
        ed1 = changeDate(calEvent["end"]["dateTime"])
      s1 = str(calEvent["summary"]).replace("\n-LAST-", "")
      c1 = str(calEvent["colorId"])
      d1 = str(calEvent["description"])
      if (sd1 != sd2 or ed1 != ed2 or s1 != s2 or c1 != c2 or d1 != d2):
        calEvent["summary"] = s2
        calEvent["description"] = d2
        calEvent["colorId"] = c2
        calEvent["start"]["dateTime"] = sd2
        calEvent["end"]["dateTime"] = ed2
        cal.updateEvent(area, calEvent)
      DB.setEventToFind(id, calEvent["id"])
      continue
    ed = calEvent["end"]["dateTime"][0:19]
    id = calEvent["id"]
    newEvent = {"End": ed, "Id": id}
    if isOver(newEvent):
      cal.deleteEvent(area, newEvent["Id"])
  listCalId = DB.getMissingEvents(area)
  printLogs(logs.MAJ, logs.INFO,
            "Number of missing events : {}".format(len(listCalId)))
  for calId in listCalId:
    DB.deleteEvent(area, calId)

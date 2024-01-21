# -*- coding: utf-8 -*-

# IMPORTS
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime as date
from dotenv import load_dotenv
import urllib3
import pickle

from functions import load, load_crypted, getLastYear, code_credentials
from logs import printLogs, printModifs
import os.path as path
import logs

load_dotenv()

# Params :
# area : the area, to know the creds to load and the timetable to use
# calId : calId of an event to delete
# Return :
# A boolean, True if succeded, False if failed after 5 retry
# This function try 5 times to delete an event on google calendar
def deleteEvent(area, calId, retry=5):
  if retry == 0:
    printModifs(logs.CAL, logs.ERROR, "Error deleting {}".format(calId))
    return False
  calendarId = area['Address']
  service = build('calendar', 'v3', credentials=findCreds(area['Timetable']))
  try:
    service.events().delete(calendarId=calendarId, eventId=calId).execute()
    printModifs(logs.CAL, logs.INFO, "Deleted {}".format(calId))
    return True
  except:
    printModifs(logs.CAL, logs.WARN,
                "Retry delete ({}) ({})".format(retry, calId))
    return deleteEvent(area, calId, retry - 1)

# Params :
# area : The area
# Returns :
# A list of event read on ginp.
# Could be [] or "invalid" in case of fail (between 1am to 2am)
def getEvents(area):
  printLogs(logs.MAJ, logs.INFO, "[{}] Fetching event on id {}".format(area['Name'].center(5), area['CalId']))
  inpUrl = 'https://edt.grenoble-inp.fr/directCal/2023-2024/etudiant/esisar?resources=' + str(
    area['CalId']
  ) + '&startDay=28&startMonth=08&startYear=2023&endDay=30&endMonth=07&endYear=2024'
  headers = load("tokenAgalan")
  r = urllib3.PoolManager().request('GET', inpUrl, headers=headers)
  result = r.data.decode('utf-8', errors='ignore').splitlines()
  eventsList = ('\n'.join(result)).split("BEGIN")
  return eventsList

# Params :
# area : the area, to know the creds to load and the timetable to use
# event : the event to create
# Returns :
# A boolean, True if succeded, False if failed after 5 retry
# This function try 5 times to add an event on google calendar
def createEvent(area, event, retry=5):
  if retry == 0:
    printModifs(logs.CAL, logs.ERROR, "Error creating {} on {}".format(event["Subject"], event["Start"]))
    return False
  try:
    calendarId = area['Address']
    timezone = "Europe/Paris"
    service = build('calendar', 'v3', credentials=findCreds(area['Timetable']))
    if event["Total"] < 2: description = event["Description"]
    else:
      description = "{} ({}/{})".format(event["Description"], event["Number"],event["Total"])
    subject = event["Type"]
    if event["Number"] == event["Total"] and event["Number"] > 1 and not "CC" in event["Type"]:
      subject += "\n-LAST-"
    newEvent = {
      "summary": subject,
      'description': description,
      "colorId": event["Color"],
      "start": {
        'dateTime': event["Start"],
        'timeZone': timezone,
      },
      'end': {
        'dateTime': event["End"],
        'timeZone': timezone,
      },
    }
    id = service.events().insert(calendarId=calendarId,body=newEvent,sendNotifications=True).execute()["id"]
    printModifs(logs.CAL, logs.INFO, "Created {}".format(id))
    return id
  except:
    printModifs(logs.CAL, logs.WARN, "Retry create ({})".format(retry))
    return createEvent(area, event, retry - 1)

# Params :
# area : the area, to know the creds to load and the timetable to use
# event : the event to update
# This function try 5 times to update an event on google calendar
def updateEvent(area, event, retry=5):
  calId = event["id"]
  if retry == 0:
    printModifs(logs.CAL, logs.ERROR, "Error updating {}".format(calId))
    return
  try:
    calendarId = area['Address']
    service = build('calendar', 'v3', credentials=findCreds(area['Timetable']))
    service.events().update(calendarId=calendarId, eventId=calId,body=event).execute()
    printModifs(logs.CAL, logs.INFO, "Updated {}".format(calId))
  except:
    printModifs(logs.CAL, logs.WARN,"Retry update ({}) ({})".format(retry, calId))
    updateEvent(area, event, retry - 1)

# Returns all the events find in google calendar, associated with the given area
def getCalendarEvents(area):
  printLogs(logs.CAL, logs.INFO, "[{}] Fetching all events".format(area['Name'].center(5)))
  calendarId = area['Address']
  credentials = findCreds(area['Timetable'])
  service = build('calendar', 'v3', credentials=credentials)
  now = date.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
  lastYear = getLastYear(now)
  eventsResults = service.events().list(calendarId=calendarId, timeMin=lastYear, singleEvents=True, maxResults=2500, orderBy='startTime').execute()
  events = eventsResults.get("items", [])
  return events

# Loads the creads associated with the given area
def findCreds(timetable):
  creds = None
  fileName = "token" + str(timetable)
  if path.exists("DB/" + fileName + ".pkl"):
    obj = load_crypted(fileName)
    creds = obj["credentials"]
  if not creds or not obj["valid"]:
    creds.refresh(Request())
    crypted_creds = code_credentials(creds)
    with open("DB/" + fileName + ".pkl", 'wb') as token:
      pickle.dump(crypted_creds, token)
  return creds

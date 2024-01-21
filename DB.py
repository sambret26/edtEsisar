# -*- coding: utf-8 -*-

# IMPORTS
from logs import printLogs, printModifs
from dotenv import load_dotenv
import mysql.connector
import logs
import os


load_dotenv()

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(host=os.environ.get('DB_HOST'),
                                             user=os.environ.get('DB_USER'),
                                             password=os.environ.get('DB_PASSWORD'),
                                             database=os.environ.get('DB_DATABASE'))
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

  ### GETTERS


# Returns the list of all area found in the database
def getAreaList(db):
  query = "SELECT Name, Timetable, Address, CalId FROM Areas"
  db.cursor.execute(query)
  areaList = [{'Name' : row[0], 'Timetable' : row[1], 'Address' : row[2], 'CalId' : row[3]} for row in db.cursor.fetchall()]
  return areaList


# Returns the Id, CalId, Past and SimplyEnd of every events in the given area
def getIdCalIdPastSimplyEnd(db, area):
  query = "SELECT Id, CalId, Past, SimplyEnd FROM Events WHERE Area = %s"
  values = (area, )
  db.cursor.execute(query, values)
  events = db.cursor.fetchall()
  return events


# Returns every Type for a given area
def getTypes(db, area):
  query = "SELECT DISTINCT(Type) FROM Events WHERE Area = %s"
  values = (area, )
  db.cursor.execute(query, values)
  types = db.cursor.fetchall()
  return types


# Returns ID, SimplyEnd for every events find in a given area and type
def getIdSimplyEnd(db, values):
  query = "SELECT Id, SimplyEnd FROM Events WHERE (Type, Area, Find) = (%s, %s, 1)"
  db.cursor.execute(query, values)
  events = db.cursor.fetchall()
  return events


# Returns every events flaged with ToAdd = 1 in a given area
def getEventsToAdd(db, area):
  query = "SELECT * FROM Events WHERE (ToAdd, Area) = (%s, %s)"
  values = (1, area)
  db.cursor.execute(query, values)
  events = db.cursor.fetchall()
  db.connection.commit()
  return events


# Returns id and calId of every events flaged with ToRemove = 1 in a given area
def getIdCalIdToRemove(db, area):
  query = "SELECT Id, CalId FROM Events WHERE (ToRemove, Area) = (%s, %s)"
  values = (1, area)
  db.cursor.execute(query, values)
  events = db.cursor.fetchall()
  return events


# Returns some informations of the events in given area
def getInfosByArea(db, area):
  query = "SELECT Id, CalId, Start, End, Subject, Description, Color, Number, Total FROM Events WHERE (Area) = (%s)"
  if area.startswith("3A"):
    query = "SELECT Id, CalId, Start, End, Type, Description, Color, Number, Total FROM Events WHERE (Area) = (%s)"
  values = (area,)
  db.cursor.execute(query, values)
  datas = db.cursor.fetchall()
  return datas


# Return missing events in the calendar (there are not past but not found)
def getMissingEvents(db, area):
  query = "SELECT Id, Start, Subject FROM Events WHERE (Area, Find, Past) = (%s, %s, %s)"
  values = (area, 0, 0)
  db.cursor.execute(query, values)
  events = db.cursor.fetchall()
  return events


# Returns calId of every events flaged with find = 0 in a given area
def getCalIdStartSubjectUnfind(db, area):
  query = "SELECT CalId, Start, Subject FROM Events WHERE (Find, Area) = (%s, %s)"
  values = (0, area)
  db.cursor.execute(query, values)
  events = db.cursor.fetchall()
  return events


# This function look if there is events with given fields in the database
# If yes, it put it's Id in a list
# If no, it put NULL in this list
# The list of ID/NULL is return
def searchIdsInDatabase(db, area, events):
  query = "SELECT COALESCE(e.id, NULL) FROM( \n"
  for event in events:
      type = event['Type'].replace("'","\\'")
      subject = event['Subject'].replace("'","\\'")
      description = event['Description'].replace("'","\\'")
      query+=f"SELECT CONVERT ('{event['Start']}' USING utf8mb4) AS Start, \n"
      query+=f"CONVERT ('{event['End']}' USING utf8mb4) AS End, \n"
      query += f"CONVERT('{type}' USING utf8mb4) AS Type, \n"
      query+=f"CONVERT ('{subject}' USING utf8mb4) AS Subject, \n"
      query+=f"CONVERT ('{description}' USING utf8mb4) AS Description, \n"
      query+=f"'{event['Color']}' AS Color, \n"
      query+=f"CONVERT ('{area}' USING utf8mb4) AS Area \n"
      if event != events[-1] : query+="UNION ALL \n"
  query += ") As v LEFT JOIN Events e ON CONVERT(e.Start USING utf8mb4) = v.Start AND CONVERT(e.End USING utf8mb4) = v.End AND CONVERT(e.Type USING utf8mb4) = v.Type AND CONVERT(e.Subject USING utf8mb4) = v.Subject AND CONVERT(e.Description USING utf8mb4) = v.Description AND e.Color = v.Color AND CONVERT(e.Area USING utf8mb4) = v.Area"
  db.cursor.execute(query)
  ids = [row[0] for row in db.cursor.fetchall()]
  return ids

  ### SETTERS


# This function is used to update database
# We want to know every event to add/remove
# Setting the flag Find to 0 is the init step
# After that, real event (always present) will be flags with Find = 1
def setEventsToUnfind(db, area):
  printLogs(logs.DB, logs.INFO, "[{}] Setting events to unfind".format(area.center(5)))
  query = "UPDATE Events SET Find = %s WHERE Area = %s"
  values = (0, area)
  db.cursor.execute(query, values)
  db.connection.commit()


# This function is used to update database from calendar
# We want to know every event missing in cal
# Setting the flag Find to 0 is the init step
# After that, real event (always present) will be flags with Find = 1
def setCurrentEventsToUnfind(db, area):
  printLogs(logs.DB, logs.INFO,
            "[{}] Setting current events to unfind".format(area.center(5)))
  query = "UPDATE Events SET Find = %s WHERE (Area, Past) = (%s, 0)"
  values = (0, area)
  db.cursor.execute(query, values)
  db.connection.commit()


# This function set flag Find to 1 for the given events
def setEventsToFind(db, listId):
  values = ', '.join(['%s'] * len(listId))
  query = f"UPDATE Events SET Find = 1 WHERE Id In ({values})"
  db.cursor.execute(query, listId)
  db.connection.commit()


# This function set/unset flags Past, ToRemove and ToAdd for given events
def setPastToRemoveToAdd(db, events):
  for event in events:
      printModifs(
        logs.DB, logs.INFO,
        "Setting Past = 1, ToRemove = {}, ToAdd = 0 at {}".format(event['toRemove'], event['calId']))
  query = "UPDATE Events SET Past = %s, ToRemove = %s, ToAdd = %s WHERE Id = %s"
  values = [(1, event['toRemove'], 0, event['id']) for event in events]
  db.cursor.executemany(query, values)
  db.connection.commit()


# This function set number ans total for given events
def setNumbers(db, events):
  query = "UPDATE Events SET Number = %s, Total = %s WHERE Id = %s"
  values = [(event['number'], event['total'], event['id']) for event in events]
  db.cursor.executemany(query, values)
  db.connection.commit()


# This function set ToAdd = 0 for given events
def setToAdd(db, events):
  for event in events :
      printModifs(logs.DB, logs.INFO,
                  "Setting CalId = {}, ToAdd = 0, Find = 1".format(event['calId']))
  query = "UPDATE Events SET CalId = %s, ToAdd = 0, Find = 1 WHERE Id = %s"
  values = [(event['calId'], event['id']) for event in events]
  db.cursor.executemany(query, values)
  db.connection.commit()


# This function set Past = 1, ToRemove = 0 and CalId = "None" for given events
def setPastToRemoveCalId(db, events):
  for event in events :
      printModifs(logs.DB, logs.INFO,
                  "Setting Past = 1, ToRemove = 0 at {}".format(calId))
  query = "UPDATE Events SET Past = %s, ToRemove = %s, CalId = %s WHERE Id = %s"
  values = [(1, 0, "None", event) for event in events]
  db.cursor.executemany(query, values)
  db.connection.commit()


# This function delete given events of the database
def deleteEventsByCalId(db, area, events):
  query = "DELETE FROM Events WHERE (CalId, Area) = (%s, %s)"
  values = [(event[0], area) for event in events]
  db.cursor.executemany(query, values)
  for event in events :
      printModifs(logs.DB, logs.INFO, "Deleting {} {}".format(event[2], event[1]))


# This function delete given events of the database
def deleteEventsById(db, area, events):
  query = "DELETE FROM Events WHERE (Id, Area) = (%s, %s)"
  values = [(event[0], area) for event in events]
  db.cursor.executemany(query, values)
  db.connection.commit()
  for event in events :
      printModifs(logs.DB, logs.INFO, "Deleting {} {}".format(event[2], event[1]))

  ### INSERT


# This function insert in the database given events
def addEvents(db, area, events):
  for event in events :
      printModifs(logs.DB, logs.INFO,
                  "Adding in DB {} {}".format(event["Subject"], event["Start"]))
  query = "INSERT INTO Events (CalId, Start, End, SimplyEnd, Subject, Type, Room, Teacher, Description, Color, Number, Total, Past, Area, Find, ToAdd, ToRemove) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  values = [(event["CalId"], event["Start"], event["End"], event["SimplyEnd"],
            event["Subject"], event["Type"], event["Room"], event["Teacher"],
            event["Description"], event["Color"], event["Number"],
            event["Total"], 0, area, 1, 1, 0) for event in events]
  db.cursor.executemany(query, values)
  db.connection.commit()


# This function update the value of the table Last_update with current date, and set Running flag to 1
def startRunning(db, currentDate):
  query = "UPDATE Last_update SET Last_update = %s, Running = %s WHERE Id = %s"
  values = (currentDate, 1, 1)
  db.cursor.execute(query, values)
  db.connection.commit()


# This function update the value of the table Last_update with current date, and set Running flag to 0
def endRunning(db, currentDate):
  query = "UPDATE Last_update SET Last_update = %s, Running = %s WHERE Id = %s"
  values = (currentDate, 0, 1)
  db.cursor.execute(query, values)
  db.connection.commit()

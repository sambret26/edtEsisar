# -*- coding: utf-8 -*-

# IMPORTS
from logs import printLogs, printModifs
import mysql.connector
import logs


# Returns a connection object to the database
def connect():
  connection = mysql.connector.connect(host=X,
                                       user=x,
                                       password=x,
                                       database=x)
  return connection

  ### GETTERS


# Returns the list of all area found in the database
def getAreaList():
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Name FROM Areas"
  cursor.execute(query)
  areaList = [row[0] for row in cursor.fetchall()]
  connection.close()
  return areaList


# Returns the address of the calendar associated with the given area
def getCalendarId(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Address FROM Areas WHERE Name = %s"
  values = (area, )
  cursor.execute(query, values)
  calendarId = cursor.fetchone()[0]
  connection.close()
  return calendarId


# Returns the timetable with the given area
def getTimetable(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Timetable FROM Areas WHERE Name = %s"
  values = (area, )
  cursor.execute(query, values)
  timetable = cursor.fetchone()[0]
  connection.close()
  return timetable


# Returns the ginp ID associated with the given area
def getId(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT calId FROM Areas WHERE Name = %s"
  values = (area, )
  cursor.execute(query, values)
  calId = cursor.fetchone()[0]
  connection.close()
  return calId


# Returns the Id, CalId, Past and SimplyEnd of every events in the given area
def getIdCalIdPastSimplyEnd(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Id, CalId, Past, SimplyEnd FROM Events WHERE Area = %s"
  values = (area, )
  cursor.execute(query, values)
  events = cursor.fetchall()
  connection.close()
  return events


# Returns every Type for a given area
def getTypes(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT DISTINCT(Type) FROM Events WHERE Area = %s"
  values = (area, )
  types = cursor.execute(query, values).fetchall()
  connection.close()
  return types


# Returns ID, SimplyEnd and CalId for every events find in a given area and type
def getIdSimplyEndCalId(values):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Id, SimplyEnd, CalId FROM Events WHERE (Type, Area, Find) = (%s, %s, 1)"
  cursor.execute(query, values)
  events = cursor.fetchall()
  connection.close()
  return events


# Returns every events flaged with ToAdd = 1 in a given area
def getEventsToAdd(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT * FROM Events WHERE (ToAdd, Area) = (%s, %s)"
  values = (1, area)
  cursor.execute(query, values)
  events = cursor.fetchall()
  connection.commit()
  connection.close()
  return events


# Returns calId of every events flaged with find = 0 in a given area
def getCalIdUnfind(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT CalId FROM Events WHERE (Find, Area) = (%s, %s)"
  values = (0, area)
  cursor.execute(query, values)
  events = [row[0] for row in cursor.fetchall()]
  connection.close()
  return events


# Returns id and calId of every events flaged with ToRemove = 1 in a given area
def getIdCalIdToRemove(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Id, CalId FROM Events WHERE (ToRemove, Area) = (%s, %s)"
  values = (1, area)
  cursor.execute(query, values)
  events = cursor.fetchall()
  connection.close()
  return events


# Returns calId of every events in a given area
def getCalId(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT CalId FROM Events WHERE Area = %s"
  values = (area, )
  cursor.execute(query, values)
  listEvents = [event[0] for event in cursor.fetchall()]
  connection.close()
  return listEvents


# Returns some informations of the events with the given calId in a given area
def getInfo(area, calId):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Id, Start, End, Subject, Description, Color, Number, Total FROM Events WHERE (CalId, Area) = (%s, %s)"
  if area.startswith("3A"):
    query = "SELECT Id, Start, End, Type, Description, Color, Number, Total FROM Events WHERE (CalId, Area) = (%s, %s)"
  values = (calId, area)
  cursor.execute(query, values)
  data = cursor.fetchone()
  connection.close()
  return data


# Return missing events in the calendar (there are not past but not found)
def getMissingEvents(area):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT CalId FROM Events WHERE (Area, Find, Past) = (%s, %s, %s)"
  values = (area, 0, 0)
  cursor.execute(query, values)
  listCalId = [event[0] for event in cursor.fetchall()]
  connection.commit()
  return listCalId


# This function look if there is an event with given field in the database
# If yes, it returns it's Id, Past and CalId fields.
# If no, it returns [False, False, False]
def searchEventInDatabase(area, event):
  connection = connect()
  cursor = connection.cursor()
  query = "SELECT Id, Past, CalId FROM Events WHERE (Start, End, Type, Subject, Description, Color, Area) = (%s, %s, %s, %s, %s, %s, %s)"
  values = (event["Start"], event["End"], event["Type"], event["Subject"],
            event["Description"], event["Color"], area)
  cursor.execute(query, values)
  result = cursor.fetchall()
  connection.close()
  if (len(result) == 0): return (False, False, False)
  return result[0]

  ### SETTERS


# This function is used to update database
# We want to know every event to add/remove
# Setting the flag Find to 0 is the init step
# After that, real event (always present) will be flags with Find = 1
def setEventsToUnfind(area):
  printLogs(logs.DB, logs.INFO, "Setting events to unfind for {}".format(area))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET Find = %s WHERE Area = %s"
  values = (0, area)
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function is used to update database from calendar
# We want to know every event missing in cal
# Setting the flag Find to 0 is the init step
# After that, real event (always present) will be flags with Find = 1
def setCurrentEventsToUnfind(area):
  printLogs(logs.DB, logs.INFO,
            "Setting current events to unfind for {}".format(area))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET Find = %s WHERE (Area, Past) = (%s, 0)"
  values = (0, area)
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function set flag Find to 1 for the given event
def setEventToFind(id, calId):
  #printLogs(logs.DB, logs.INFO, "Setting Find = 1 at {}".format(calId))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET Find = 1 WHERE (Find, Id) = (%s, %s)"
  values = (0, str(id))
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function set/unset flags Past, ToRemove and ToAdd for a given event
def setPastToRemoveToAdd(toRemove, id, calId):
  printModifs(
    logs.DB, logs.INFO,
    "Setting Past = 1, ToRemove = {}, ToAdd = 0 at {}".format(toRemove, calId))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET Past = %s, ToRemove = %s, ToAdd = %s WHERE Id = %s"
  values = (1, toRemove, 0, id)
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function set number ans total for a given event
def setNumbers(values, calId):
  #printLogs(
  #logs.DB, logs.INFO,
  #"Set Number = {}, Total = {} at {}".format(values[0], values[1], calId))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET Number = %s, Total = %s WHERE Id = %s"
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function set ToAdd = 0 for a given event
def setToAdd(calId, Id):
  printModifs(logs.DB, logs.INFO,
              "Setting CalId = {}, ToAdd = 0".format(calId))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET CalId = %s, ToAdd = 0 WHERE Id = %s"
  values = (calId, Id)
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function set Past = 1, ToRemove = 0 and CalId = "None" for a given event
def setPastToRemoveCalId(calId):
  printModifs(logs.DB, logs.INFO,
              "Setting Past = 1, ToRemove = 0 at {}".format(calId))
  connection = connect()
  cursor = connection.cursor()
  query = "UPDATE Events SET Past = %s, ToRemove = %s, CalId = %s WHERE Id = %s"
  values = (1, 0, "None", calId)
  cursor.execute(query, values)
  connection.commit()
  connection.close()


# This function delete a given event of the database
def deleteEvent(area, calId):
  datas = getInfo(area, calId)
  connection = connect()
  cursor = connection.cursor()
  query = "DELETE FROM Events WHERE (CalId, Area) = (%s, %s)"
  values = (calId, area)
  cursor.execute(query, values)
  connection.commit()
  printModifs(logs.DB, logs.INFO, "Deleting {} {}".format(datas[3], datas[1]))

  ### INSERT


# This function insert in the database a given event
def addEvent(area, event):
  connection = connect()
  cursor = connection.cursor()
  printModifs(logs.DB, logs.INFO,
              "Adding in DB {} {}".format(event["Subject"], event["Start"]))
  values = (event["CalId"], event["Start"], event["End"], event["SimplyEnd"],
            event["Subject"], event["Type"], event["Room"], event["Teacher"],
            event["Description"], event["Color"], event["Number"],
            event["Total"], 0, area, 1, 1, 0)
  query = "INSERT INTO Events (CalId, Start, End, SimplyEnd, Subject, Type, Room, Teacher, Description, Color, Number, Total, Past, Area, Find, ToAdd, ToRemove) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  values = (event["CalId"], event["Start"], event["End"], event["SimplyEnd"],
            event["Subject"], event["Type"], event["Room"], event["Teacher"],
            event["Description"], event["Color"], event["Number"],
            event["Total"], 0, area, 1, 1, 0)
  cursor.execute(query, values)
  connection.commit()
  connection.close()

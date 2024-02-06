# -*- coding: utf-8 -*-

# IMPORTS
from dotenv import load_dotenv
import sqlite3
import os

import logsConstants as logs

load_dotenv()

logsTypes = os.environ.get("LOGS")
if (logsTypes and logsTypes == "FILES"):
    from logsInFile import printLogs, printModifs, printDB
elif (logsTypes and logsTypes == "DB"):
    from logsInDB import printLogs, printModifs, printDB
else :
    from noLogs import printLogs, printModifs, printBD

class MyCursor(sqlite3.Cursor):
    def execute(self, operation, params=None):
        if params:
            printDB(self._format_query(operation, params))
            return super().execute(operation, params)
        printDB(operation)
        return super().execute(operation)

    def executemany(self, operation, seq_params):
        for params in seq_params:
            query = operation
            printDB(self._format_query(query, params))
        return super().executemany(operation, seq_params)

    def _format_query(self, query, params):
        if params:
            return f"{query} ({', '.join(map(repr, params))})"
        return query

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(os.environ.get("DB_FILENAME"))
        self.cursor = self.connection.cursor(factory=MyCursor)
    def close(self):
        self.connection.close()

  ### GETTERS

def getCalendarDatas(area):
    db = Database()
    query = f"SELECT Timetable, Address FROM Areas WHERE Name = '{area}'"
    db.cursor.execute(query)
    datas = db.cursor.fetchone()
    db.close()
    return datas

# Returns the list of all area found in the database
def getAreaList(db):
    query = "SELECT Name, Timetable, Address, CalId FROM Areas"
    db.cursor.execute(query)
    areaList = [{'Name' : row[0], 'Timetable' : row[1], 'Address' : row[2], 'CalId' : row[3]} for row in db.cursor.fetchall()]
    return areaList

# Returns the Id, CalId and SimplyEnd of every events in the given area with PAst = 0
def getIdCalIdSimplyEnd(db, area):
    query = f"SELECT Id, CalId, SimplyEnd FROM Events WHERE Area = '{area}' AND Past = 0"
    db.cursor.execute(query)
    events = db.cursor.fetchall()
    return events

# Returns every Type for a given area
def getTypes(db, area):
    query = f"SELECT DISTINCT(Type) FROM Events WHERE Area = '{area}'"
    db.cursor.execute(query)
    types = [row[0] for row in db.cursor.fetchall()]
    return types

# Returns Id and SimplyEnd for every events find in a given area and type
def getIdSimplyEnd(db, area, type):
    type = type.replace("'","''")
    query = f"SELECT Id, SimplyEnd FROM Events WHERE Area = '{area}' AND Type = '{type}' AND Find = 1"
    db.cursor.execute(query)
    events = db.cursor.fetchall()
    return events

# Returns every events flaged with ToAdd = 1 in a given area
def getEventsToAdd(db, area):
    query = f"SELECT * FROM Events WHERE Area = '{area}' AND ToAdd = 1"
    db.cursor.execute(query)
    events = db.cursor.fetchall()
    return events

# Returns Id and CalId of every events flaged with ToRemove = 1 in a given area
def getIdCalIdToRemove(db, area):
    query = f"SELECT Id, CalId FROM Events WHERE Area = '{area}' AND ToRemove = 1"
    db.cursor.execute(query)
    events = db.cursor.fetchall()
    return events

# Returns some informations of the events in given area
def getInfosByArea(db, area):
    query = f"SELECT Id, CalId, Start, End, Subject, Description, Color, Number, Total FROM Events WHERE Area = '{area}'"
    if area.startswith("3A"):
        query = f"SELECT Id, CalId, Start, End, Type, Description, Color, Number, Total FROM Events WHERE Area = '{area}'"
    db.cursor.execute(query)
    datas = db.cursor.fetchall()
    return datas

# Return Id, Start and Subject of missing events in the calendar (there are not past but not found)
def getMissingEvents(db, area):
    query = f"SELECT Id, Start, Subject FROM Events WHERE Area = '{area}' AND Find = 0 AND Past = 0"
    db.cursor.execute(query)
    events = db.cursor.fetchall()
    return events

# Returns CalId, Start and Subject of every events flaged with find = 0 in a given area
def getCalIdStartSubjectUnfind(db, area):
    query = f"SELECT CalId, Start, Subject FROM Events WHERE AREA = '{area}' AND Find = 0"
    db.cursor.execute(query)
    events = db.cursor.fetchall()
    return events

# This function look if there is events with given fields in the database
# If yes, it put it's Id in a list
# If no, it put NULL in this list
# The list of Id/NULL is return
def searchIdsInDatabase(db, area, events):
    query = "SELECT COALESCE(e.id, NULL) FROM( "
    for event in events:
        type = event['Type'].replace("'","''")
        subject = event['Subject'].replace("'","''")
        description = event['Description'].replace("'","''")
        query+=f"SELECT CAST ('{event['Start']}' AS TEXT) AS Start, "
        query+=f"CAST ('{event['End']}' AS TEXT) AS End, "
        query += f"CAST('{type}' AS TEXT) AS Type, "
        query+=f"CAST ('{subject}' AS TEXT) AS Subject, "
        query+=f"CAST ('{description}' AS TEXT) AS Description, "
        query+=f"'{event['Color']}' AS Color, "
        query+=f"CAST ('{area}' AS TEXT) AS Area "
        if event != events[-1] : query+="UNION ALL "
    query += ") As v LEFT JOIN Events e ON CAST(e.Start AS TEXT) = v.Start AND CAST(e.End AS TEXT) = v.End AND CAST(e.Type AS TEXT) = v.Type AND CAST(e.Subject AS TEXT) = v.Subject AND CAST(e.Description AS TEXT) = v.Description AND e.Color = v.Color AND CAST(e.Area AS TEXT) = v.Area"
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
    query = f"UPDATE Events SET Find = 0 WHERE Area = '{area}'"
    db.cursor.execute(query)
    db.connection.commit()

# This function is used to update database from calendar
# We want to know every event missing in cal
# Setting the flag Find to 0 is the init step
# After that, real event (always present) will be flags with Find = 1
def setCurrentEventsToUnfind(db, area):
    printLogs(logs.DB, logs.INFO, "[{}] Setting current events to unfind".format(area.center(5)))
    query = f"UPDATE Events SET Find = 0 WHERE Area = '{area}' AND Past = 0"
    db.cursor.execute(query)
    db.connection.commit()

# This function set flag Find to 1 for the given events
def setEventsToFind(db, listId):
    values = ', '.join(['?'] * len(listId))
    query = f"UPDATE Events SET Find = 1 WHERE Id In ({values})"
    db.cursor.execute(query, listId)
    db.connection.commit()

# This function set/unset flags Past, ToRemove and ToAdd for given events
def setPastToRemoveToAdd(db, events):
    for event in events:
        printModifs(logs.DB, logs.INFO, f"Setting Past = 1, ToRemove = {event['toRemove']}, ToAdd = 0 at {event['calId']}")
    query = "UPDATE Events SET Past = 1, ToRemove = ?, ToAdd = 0 WHERE Id = ?"
    values = [(event['toRemove'], event['id']) for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

# This function set number and total for given events
def setNumbers(db, events):
    query = "UPDATE Events SET Number = ?, Total = ? WHERE Id = ?"
    values = [(event['number'], event['total'], event['id']) for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

# This function set ToAdd = 0 for given events
def setToAdd(db, events):
    for event in events :
        printModifs(logs.DB, logs.INFO, "Setting CalId = {}, ToAdd = 0, Find = 1".format(event['calId']))
    query = "UPDATE Events SET CalId = ?, ToAdd = 0, Find = 1 WHERE Id = ?"
    values = [(event['calId'], event['id']) for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

# This function set Past = 1, ToRemove = 0 and CalId = "None" for given events
def setPastToRemoveCalId(db, events):
    for event in events :
        printModifs(logs.DB, logs.INFO, "Setting Past = 1, ToRemove = 0 at {}".format(event[1]))
    query = "UPDATE Events SET Past = 1, ToRemove = 0, CalId = 'None' WHERE Id = ?"
    values = [event[0] for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

# This function delete given events of the database
def deleteEventsByCalId(db, area, events):
    for event in events :
        printModifs(logs.DB, logs.INFO, "Deleting {} {}".format(event[2], event[1]))
    query = "DELETE FROM Events WHERE (CalId, Area) = (?, ?)"
    values = [(event[0], area) for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

# This function delete given events of the database
def deleteEventsById(db, area, events):
    for event in events :
        printModifs(logs.DB, logs.INFO, "Deleting {} {}".format(event[2], event[1]))
    query = "DELETE FROM Events WHERE (Id, Area) = (?, ?)"
    values = [(event[0], area) for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

  ### INSERT

# This function insert in the database given events
def addEvents(db, area, events):
    for event in events :
        printModifs(logs.DB, logs.INFO, "Adding in DB {} {}".format(event["Subject"], event["Start"]))
    query = f"INSERT INTO Events (CalId, Start, End, SimplyEnd, Subject, Type, Room, Teacher, Description, Color, Number, Total, Past, Area, Find, ToAdd, ToRemove) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '{area}', 1, 1, 0)"
    values = [(event["CalId"], event["Start"], event["End"], event["SimplyEnd"], event["Subject"], event["Type"], event["Room"], event["Teacher"], event["Description"], event["Color"], event["Number"], event["Total"]) for event in events]
    db.cursor.executemany(query, values)
    db.connection.commit()

# This function update the value of the table Last_update with current date, and set Running flag to 1
def startRunning(db, currentDate):
    query = f"UPDATE Last_update SET Last_update = '{currentDate}', Running = 1 WHERE Id = 1"
    db.cursor.execute(query)
    db.connection.commit()

# This function update the value of the table Last_update with current date, and set Running flag to 0
def endRunning(db, currentDate):
    query = f"UPDATE Last_update SET Last_update = '{currentDate}', Running = 0 WHERE Id = 1"
    db.cursor.execute(query)
    db.connection.commit()

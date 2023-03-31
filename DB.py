# -*- coding: utf-8 -*-

# IMPORTS 
import sqlite3

# CONST
DBNAME = "DB.db"

# Returns a connection object to the database
def connect():
    return sqlite3.connect(DBNAME)

# Returns the list of all area find in the database
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
    query = "SELECT Address FROM Areas WHERE Name = ?"
    values = (area,)
    calendarId = cursor.execute(query, values).fetchone()[0]
    connection.close()
    return calendarId

# Returns the timetable with the given area
def getTimetable(area):
    connection = connect()
    cursor = connection.cursor()
    query = "SELECT Timetable FROM Areas WHERE Name = ?"
    values = (area, )
    timetable = cursor.execute(query,values).fetchone()[0]
    connection.close()
    return timetable

#Returns the ginp ID associated with the given area
def getId(area):
    connection = connect()
    cursor = connection.cursor()
    query = "SELECT calId FROM Areas WHERE Name = ?"
    values = (area ,)
    calId = cursor.execute(query,values).fetchone()[0]
    connection.close()
    return calId

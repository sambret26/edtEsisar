from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

connection = mysql.connector.connect(host=os.environ.get('DB_HOST'),
                                     user=os.environ.get('DB_USER'),
                                     password=os.environ.get('DB_PASSWORD'),
                                     database=os.environ.get('DB_DATABASE'))
c = connection.cursor()

# Drop all tables if exists
c.execute("DROP TABLE IF EXISTS Areas")
c.execute("DROP TABLE IF EXISTS Events")
c.execute("DROP TABLE IF EXISTS Last_update")

# Initiate Areas
c.execute('''CREATE TABLE Areas
             (Id INT AUTO_INCREMENT PRIMARY KEY,
             Name TEXT NOT NULL,
             Timetable TEXT NOT NULL,
             Address TEXT NOT NULL,
             CalId INT NOT NULL)''')

# Initiate Events
c.execute('''CREATE TABLE Events
             (Id INT AUTO_INCREMENT PRIMARY KEY,
             CalId TEXT,
             Area TEXT,
             Start TEXT,
             End TEXT,
             SimplyEnd BIGINT,
             Subject TEXT,
             Type TEXT,
             Room TEXT,
             Teacher TEXT,
             Description TEXT,
             Color INT,
             Number INT,
             Total INT,
             Past INT CHECK (Past IN (0,1)),
             Find INT CHECK (Find IN (0,1)),
             ToAdd INT CHECK (ToAdd IN (0,1)),
             ToRemove INT CHECK (ToRemove IN (0,1)))''')

# Initiate Last_update
c.execute('''CREATE TABLE Last_update
             (Id INT AUTO_INCREMENT PRIMARY KEY,
             Last_update TEXT,
             Running INT CHECK (Running IN (0,1)))''')

# This function create Area with parameters
def createArea(c, name, timetable, address, calId):
    c.execute('''INSERT INTO Areas
                 (Name, Timetable, Address, CalId)
                 VALUES (%s, %s, %s, %s)''',
                 (name, timetable, address, calId))

createArea(c, '3AS2', '3A', 'ftoon2p22e07besr9dn06eibp8@group.calendar.google.com', 13250)
c.execute('''INSERT INTO Last_update (Last_update, Running) VALUES ('None', 0)''')
connection.commit()
connection.close()

import sqlite3

conn = sqlite3.connect('DB.db')
c = conn.cursor()

# Drop all tables if exists
c.execute("DROP TABLE IF EXISTS Areas")
c.execute("DROP TABLE IF EXISTS Events")

# Create Areas
c.execute('''CREATE TABLE Areas
             (Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Name TEXT NOT NULL,
             Timetable TEXT NOT NULL,
             Address TEXT NOT NULL,
             CalId INTEGER NOT NULL)''')

# Create Events
c.execute('''CREATE TABLE Events
             (Id INTEGER PRIMARY KEY AUTOINCREMENT,
             CalId TEXT,
             Area TEXT,
             Start TEXT,
             End TEXT,
             SimplyEnd INTEGER,
             Subject TEXT,
             Type TEXT,
             Room TEXT,
             Teacher TEXT,
             Description TEXT,
             Color INTEGER,
             Number INTEGER,
             Total INTEGER,
             Past INTEGER CHECK (Past IN (0,1)),
             Find INTEGER CHECK (Find IN (0,1)),
             ToAdd INTEGER CHECK (ToAdd IN (0,1)),
             ToRemove INTEGER CHECK (ToRemove IN (0,1)))''')

conn.commit()
conn.close()

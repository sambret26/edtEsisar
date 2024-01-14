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

# Create Areas
c.execute('''CREATE TABLE Areas
             (Id INT AUTO_INCREMENT PRIMARY KEY,
             Name TEXT NOT NULL,
             Timetable TEXT NOT NULL,
             Address TEXT NOT NULL,
             CalId INT NOT NULL)''')

# Create Events
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

conn.commit()
conn.close()

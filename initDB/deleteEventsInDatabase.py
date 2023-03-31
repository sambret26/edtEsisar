import sqlite3

conn = sqlite3.connect('DB.db')
c = conn.cursor()

c.execute("DELETE FROM Events")
conn.commit()
conn.close()

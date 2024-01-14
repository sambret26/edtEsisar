import mysql.connector

connection = mysql.connector.connect(host=X,
                                     user=x,
                                     password=x,
                                     database=x)
c = connection.cursor()

c.execute("DELETE FROM Events")
connection.commit()
connection.close()

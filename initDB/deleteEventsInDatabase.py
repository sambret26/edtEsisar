from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

connection = mysql.connector.connect(host=os.environ.get('DB_HOST'),
                                     user=os.environ.get('DB_USER'),
                                     password=os.environ.get('DB_PASSWORD'),
                                     database=os.environ.get('DB_DATABASE'))
c = connection.cursor()

c.execute("DELETE FROM Events")
connection.commit()
connection.close()

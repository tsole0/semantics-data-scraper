import sqlite3
import csv

connection = sqlite3.connect("finalValues.db")
# INITIALIZING SQL DATABASE CONNECTION
cur = connection.cursor()
query = 'SELECT * FROM finalValues'

cur.execute(query)
with open("finalOutput.csv", 'w',newline='') as csv_file: 
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in cur.description]) 
    csv_writer.writerows(cur)
connection.close()

print('Done.')
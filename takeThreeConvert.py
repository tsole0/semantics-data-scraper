import csv, sqlite3
from statistics import mean

con2 = sqlite3.connect("searchableDatabase.db") # change to 'sqlite:///your_filename.db'
cur2 = con2.cursor()
con1 = sqlite3.connect("kanji_output.db")
cur1 = con1.cursor()
con3 = sqlite3.connect("finalValues.db")
cur3 = con3.cursor()


cur2.execute("CREATE TABLE IF NOT EXISTS concretnessValues (word, bigram, conc_m, conc_sd, unknown, total, percent_known, subtlex, dom_pos);") # use your column names here

with open('Concreteness_ratings_Brysbaert_et_al_BRM-1.csv','r') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin, delimiter=';') # comma is default delimiter
    to_db = [(i['Word'], i['Bigram'], i['Conc.M'], i['Conc.SD'], i['Unknown'], i['Total'], i['Percent_known'], i['SUBTLEX'], i['Dom_Pos']) for i in dr]

cur2.executemany("INSERT INTO concretnessValues (word, bigram, conc_m, conc_sd, unknown, total, percent_known, subtlex, dom_pos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

### Find kanji values ###

listOfCols = ("word", "bigram", "conc_m", "conc_sd", "unknown", "total", "percent_known", "subtlex", "dom_pos")

# Create a table in the new database
query = """
CREATE TABLE IF NOT EXISTS search_results (
    column1 TEXT,
    strokeCount INTEGER,
    search_result REAL
)
"""
cur3.execute(query)

# Select all rows from kanji_values
query = "SELECT * FROM kanji_values"
cur1.execute(query)

# Iterate over the rows in kanji_values
for row in cur1:
    # Get the values in columns 3-12
    values = row[2:11]
    
    # Select the value in column 3 from concretnessValues for each searched for value
    search_query = "SELECT conc_m FROM concretnessValues WHERE word=?"
    cur2.execute(search_query, (values[0],))

    
    # Fetch the search results
    search_results = cur2.fetchall()
    
    # Calculate the mean of the search results if the list is not empty
    if len(search_results) > 0:
        search_result = mean([result[0] for result in search_results])
    else:
        search_result = None
    
    # Insert the values from column 1 of kanji_values and the mode of the search results into the new database
    insert_query = "INSERT INTO search_results (column1, strokeCount, search_result) VALUES (?, ?, ?)"
    insert_values = (row[0], row[1], search_result)
    cur3.execute(insert_query, insert_values)
    
# Commit the changes to the new database and close the cursors and connections
con3.commit()
cur1.close()
cur2.close()
cur3.close()
con1.close()
con2.close()
con3.close()
import csv, sqlite3
from statistics import mean

con2 = sqlite3.connect("searchableDatabase.db") # change to 'sqlite:///your_filename.db'
cur2 = con2.cursor()
con1 = sqlite3.connect("kanji_output.db")
cur1 = con1.cursor()
con3 = sqlite3.connect("finalValues.db")
cur3 = con3.cursor()

# Convert searchableDatabase to .db
cur2.execute("CREATE TABLE IF NOT EXISTS concretnessValues (word TEXT, bigram TEXT, conc_m, conc_sd, unknown, total, percent_known, subtlex, dom_pos);") # use your column names here

with open('Concreteness_ratings_Brysbaert_et_al_BRM-1.csv','r') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin, delimiter=';') # comma is default delimiter
    to_db = [(i['Word'], i['Bigram'], i['Conc.M'], i['Conc.SD'], i['Unknown'], i['Total'], i['Percent_known'], i['SUBTLEX'], i['Dom_Pos']) for i in dr]

cur2.executemany("INSERT INTO concretnessValues (word, bigram, conc_m, conc_sd, unknown, total, percent_known, subtlex, dom_pos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)


# Create a table in the new database
query1 = """
CREATE TABLE IF NOT EXISTS finalValues (
    column1 TEXT,
    strokeCount INTEGER,
    search_result REAL
)
"""

cur3.execute(query1)


query = "SELECT * FROM kanji_values"
cur1.execute(query)

list_of_values = []

# Iterate over the rows in kanji_values
for row in cur1:
    # Get the values in columns 3-12
    values = row[2:11]
    for item in values:
        query = "SELECT conc_m FROM concretnessValues WHERE word=?"
        cur2.execute(query, (item,))
        result = cur2.fetchone()
        print(f'item: {item}, result: {result}')
        list_of_values.append(result)

    list_of_values = [x for x in list_of_values if x is not None]

    for i, item in enumerate(list_of_values):
            string = item[0]
            modified_string = string.replace(",", ".")
            list_of_values[i] = modified_string

    #Turn strings into floats

    for i in range(len(list_of_values)):
        list_of_values[i] = float(list_of_values[i])

    if list_of_values:
        abstractnessAverage = mean(list_of_values)
    else:
        abstractnessAverage = None


    query = "INSERT INTO finalValues (column1, strokeCount, search_result) VALUES (?, ?, ?);"

    cur3.execute(query, (row[0], row[1], abstractnessAverage))

    print(list_of_values)


    list_of_values = []

con3.commit()
con2.commit()
cur1.close()
cur2.close()
cur3.close()
con1.close()
con2.close()
con3.close()

print("Done.")


from bs4 import BeautifulSoup
import requests
import sqlite3
import csv

#### GETTING KANJI FROM WIKIPEDIA LIST ####

html_text = requests.get('https://en.wiktionary.org/wiki/Appendix:Japanese_kanji_by_JIS_X_0208_kuten_code').text

soup = BeautifulSoup(html_text, 'lxml')

kanjiDump = soup.find_all('span', class_ = 'Jpan')

kanjiList = []
individualkanji = []

for row in kanjiDump:
    firstKanji = row.find('a')
    kanjiList.append(firstKanji)

for row in kanjiDump:
    firstKanji = row.find('a')
    individualKanji = firstKanji.findNextSiblings('a')
    kanjiList.extend(individualKanji)


for i in range(len(kanjiList)):
    kanjiList[i] = kanjiList[i].text

# print(kanjiList)
# print(len(kanjiList))

#### GETTING VALUES FROM JISHO ####

jisho_index = []
jisho_list = []
meaning_list = [] * 10


connection = sqlite3.connect("kanji_output.db")
# INITIALIZING SQL DATABASE CONNECTION
cur = connection.cursor()
query = 'SELECT * FROM kanji_values'
cur.execute('''
CREATE TABLE IF NOT EXISTS kanji_values (
    Kanji TEXT,
    StrokeCount INTEGER,
    MeaningOne TEXT,
    MeaningTwo TEXT,
    MeaningThree TEXT,
    MeaningFour TEXT,
    MeaningFive TEXT,
    MeaningSix TEXT,
    MeaningSeven TEXT,
    MeaningEight TEXT,
    MeaningNine TEXT,
    MeaningTen TEXT)''')
cur.execute(query)


for i in range(len(kanjiList)):
    # Everything related to jisho and formatting data in this loop
    jisho_index = ('https://jisho.org/search/%23kanji {}'.format(kanjiList[i]))
    jisho_list.append(jisho_index)
    jisho_page = requests.get(jisho_list[i]).text
    kanji_soup = BeautifulSoup(jisho_page, 'lxml')
    # Fetching pages from jisho using kanjiList

    stroke_count = getattr(kanji_soup.find('div', class_ = 'kanji-details__stroke_count'), 'text', None)
    # Scraping the stroke count from the fetched page and setting value equal to "None" if no value found
    
    if stroke_count == None:
        # Removing kanji not found on jisho
        print("'{}' skipped and replaced as null".format(kanjiList[i]))
        kanjiList[i] = None

    else:
        stroke_count = stroke_count.split('  ', 1)[0]
        #Cut out alternate stroke counts

        stroke_count = stroke_count.split(' ', 1)[0]
        #Cut out noninteger values in stroke_count variable

        meanings = getattr(kanji_soup.find('div', class_ = 'kanji-details__main-meanings'), 'text', None)
        # Scraping kanji meanings from fetched page
        meaning_list = meanings.split(", ")
        for j in range(len(meaning_list)):
            meaning_list[j] = meaning_list[j].replace("\n", "")
            meaning_list[j] = meaning_list[j].replace('  ', '')
        # Splitting kanji meanings into separate items stored in "meaning_list" list and reformatting

        for l in range(len(meaning_list)):
            meaning_list[l] = meaning_list[l].split(' ', 1)[0]
        # Restricting items in "meaning_list" to only the first word


        for k in range(10 - len(meaning_list)):
            meaning_list.append('')
        # Assigning blank values to the rest of indices so they can be added to the SQL database


        
        cur.execute("INSERT INTO kanji_values VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (kanjiList[i], stroke_count, meaning_list[0], meaning_list[1], meaning_list[2], meaning_list[3], meaning_list[4], meaning_list[5], meaning_list[6], meaning_list[7], meaning_list[8], meaning_list[9]))
        connection.commit()

    



    # Update "Progress Bar"
    print('Request {} / {} completed'.format(i, len(kanjiList)))

for i in range(len(kanjiList)):
    if kanjiList[i] == None:
        kanjiList.pop(i)
        
cur.execute(query)
with open("out.csv", 'w',newline='') as csv_file: 
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in cur.description]) 
    csv_writer.writerows(cur)
connection.close()


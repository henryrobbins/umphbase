import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

# NOTE: As of 2021-11-14, the API does not provide a way to pull Jimmy Stewart
# information (songs with a significant improvisational component). This script
# provides web-scraping functionality for obtaining this information.

driver = webdriver.Chrome("/Applications/chromedriver")
url = "https://allthings.umphreys.com/setlists/metadata/1"
driver.get(url)
content = driver.page_source
soup = BeautifulSoup(content, "lxml")

table_class_attr = 'table table-striped sortable dataTable no-footer'
table = soup.find('table', attrs={'class': table_class_attr})

rows = []
for row in table.find('tbody').findAll('tr'):
    rows.append([field.findAll(text=True)[0] for field in row.findAll('td')])

df = pd.DataFrame(rows)
df.columns = ['show_date', 'original_artist', 'name', 'footnote']
df['with_lyrics'] = df['footnote'].apply(lambda x: 'lyrics' in x.lower())
df = df[['name', 'show_date', 'with_lyrics']]

df.to_csv('data/jimmy_stewarts.csv', index=False)

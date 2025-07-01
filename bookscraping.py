import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import csv

base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
start_url = 'https://books.toscrape.com/index.html'

books = []
page = 1

while True:
    if page == 1:
        response = requests.get(start_url)
    else:
        response = requests.get(base_url.format(page))
    
    if response.status_code != 200:
       break
    else: 
        soup = BeautifulSoup(response.text, 'html.parser')
        book_list = soup.select('article.product_pod')

    for book in book_list:
        title = book.h3.a.text
        price = book.select_one('p.price_color').text
        stock = book.select_one('p.instock.availability').text.strip()
        books.append({'title': title, 'price': price, 'stock': stock})
    
    page += 1

# Save as CSV
# with open('books.csv', 'w', newline='', encoding='utf-8') as f:
    # writer = csv.DictWriter(f, fieldnames=['title', 'price', 'stock'])
    # writer.writeheader()
    # writer.writerows(books)

# Save as JSON
with open('books.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, indent=4)

# Save as Excel
df = pd.DataFrame(books)
df.to_excel('books.xlsx', index=False)

# Save as csv
df=pd.DataFrame(books)
df.to_csv('books.csv', index=False)

print('Scraping completed. Total books scraped:', len(books))




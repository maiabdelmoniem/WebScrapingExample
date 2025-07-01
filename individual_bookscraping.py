import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import xlsxwriter
import time
from tqdm import tqdm 
import re


def scrape_book_data():
    base_url = "https://books.toscrape.com/"
    all_books_data = []

    # Get the initial page to find the total number of pages
    response = requests.get(base_url + "index.html")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    pager = soup.find('li', class_='current')
    if pager:
        total_pages = int(pager.text.strip().split('of')[1].strip())
    else:
        total_pages = 1 

    print(f"Total pages to scrape: {total_pages}")

    # Iterate through each page
    for page_num in tqdm(range(1, total_pages + 1), desc="Scraping Pages"):
        if page_num == 1:
            page_url = base_url + "index.html"
        else:
            page_url = f"{base_url}catalogue/page-{page_num}.html"

        try:
            response = requests.get(page_url)
            response.raise_for_status()  
            page_soup = BeautifulSoup(response.content, 'html.parser')

            articles = page_soup.find_all('article', class_='product_pod')

            for article in articles:
                title = article.h3.a['title']
                product_page_relative_url = article.h3.a['href']
                
                if "catalogue" not in product_page_relative_url:
                    product_page_full_url = base_url + 'catalogue/' + product_page_relative_url
                else:
                    product_page_full_url = base_url + product_page_relative_url
                
                try:
                    book_response = requests.get(product_page_full_url)
                    book_response.raise_for_status()
                    book_soup = BeautifulSoup(book_response.content, 'html.parser')

                    # Extract details from the book page
                    price = book_soup.find('p', class_='price_color').text
                    price = float(re.search(r'\d+', price).group())
                    breadcrumb = book_soup.find("ul", class_="breadcrumb")
                    
                    crumbs = breadcrumb.find_all("li")
                    if len(crumbs) >= 3:
                         category = crumbs[2].get_text(strip=True)
                    else:
                        category = "Unknown"

                    stock = book_soup.find('p', class_='instock availability').text.strip()
                    stock= re.sub(r'\s*\(.*?\)', '', stock)
                    product_description_tag = book_soup.find('div', id='product_description')
                    description = product_description_tag.find_next_sibling('p').text.strip() if product_description_tag else 'N/A'
                    
                    # Extract UPC, Product Type, Price (excl. tax), Price (incl. tax), Tax, Availability, Number of reviews
                    table_rows = book_soup.find('table', class_='table table-striped').find_all('tr')
                
                    upc = table_rows[0].find('td').text
                    product_type = table_rows[1].find('td').text
                    price_excl_tax = table_rows[2].find('td').text
                    price_excl_tax = float(re.search(r'\d+', price_excl_tax).group())

                    

                    price_incl_tax = table_rows[3].find('td').text
                    price_incl_tax = float(re.search(r'\d+', price_incl_tax).group())

                    tax = table_rows[4].find('td').text
                    tax = float(re.search(r'\d+', tax).group())

                    availability = table_rows[5].find('td').text
                    availability = int(re.search(r'\d+', availability).group())

                    num_reviews = table_rows[6].find('td').text
                    star_rating_element = book_soup.find('p', class_='star-rating')
                    star_rating = star_rating_element['class'][1] if star_rating_element else 'N/A'
                    

                    all_books_data.append({
                        'Title': title,
                        'Product Page URL': product_page_full_url,
                        'Category': category,
                        'Price (Scraped)': price,
                        'Stock (Scraped)': stock,
                        'Description': description,
                        'UPC': upc,
                        'Price (excl. tax)': price_excl_tax,
                        'Price (incl. tax)': price_incl_tax,
                        'Tax': tax,
                        'Availability': availability,
                        'Number of Reviews': num_reviews,
                        'Star Rating': star_rating
                    })
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching book page {product_page_full_url}: {e}")
                time.sleep(0.1) 

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_url}: {e}")
            continue 
    
    return all_books_data

def save_data(data, filename_base="books_data"):
    if not data:
        print("No data to save.")
        return

    df = pd.DataFrame(data)

    # Save to CSV
    csv_filename = f"{filename_base}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"Data saved to {csv_filename}")

    # Save to XLSX
    xlsx_filename = f"{filename_base}.xlsx"
    df.to_excel(xlsx_filename, index=False, engine='xlsxwriter')
    print(f"Data saved to {xlsx_filename}")

    # Save to JSON
    json_filename = f"{filename_base}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {json_filename}")

if __name__ == "__main__":
    print("Starting book scraping...")
    scraped_data = scrape_book_data()
    if scraped_data:
        save_data(scraped_data)
        print("Scraping and saving complete!")
    else:
        print("No data was scraped.")
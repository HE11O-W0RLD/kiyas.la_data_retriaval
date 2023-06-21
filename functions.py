import mysql.connector.pooling
import requests
from bs4 import BeautifulSoup
import numpy as np

# create a connection pool
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_OWN_PASSWORD",
    "database": "webscraping",
    "pool_size": 5,
    "pool_name": "my_connection_pool"
}
cnxpool = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)

def url_search(url):
    return lambda href: href and href.startswith(url)

def get_words_until_stop(text):
    try:
        words = text.split()
        index = 0
        for word in words:
            if '"' in word or word == "OLED":
                break
            index += 1
        return ' '.join(words[:index])
    except Exception as e:
        print("error0: ", str(e))

def append_to_sql(values):
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        sql = 'INSERT INTO laptops(laptop_name, laptop_ram, laptop_screen, laptop_memory) VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, values)
        cnx.commit()
    except Exception as e:
        print("Sql error1: ", str(e))
    finally:
        cursor.close()
        cnx.close()

def find_property(frame, href):
    try:
        return frame.find("a", href=url_search(href)).text
    except Exception as e:
        print("error1: ", str(e))

def find_properties(soup):
    try:
        properties = {}
        main = soup.find("div", class_="row px-3 px-sm-0 js-masonry-list")
        properties['ram'] = find_property(main, "https://kiyas.la/tr/laptop-notebook?filtreler=ram:")
        properties['ekran_boyut'] = find_property(main, "https://kiyas.la/tr/laptop-notebook?filtreler=ekranboyutu:")
        properties['hafiza'] = find_property(main, "https://kiyas.la/tr/laptop-notebook?filtreler=dahilihafiza:")
        return properties
    except Exception as e:
        print("error2: ", str(e))

def get_write_laptop_data(url):
    try:
        with requests.Session() as session:
            response = session.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            name = get_words_until_stop(soup.find("h1", class_="d-inline-block font-l font-weight-700 mx-3 mx-sm-0").text[1:-1])
            properties = find_properties(soup)
            result_list = np.array([name, properties['ram'], properties['ekran_boyut'], properties['hafiza']])
            result_list[-1] = get_words_until_stop(result_list[-1])
            append_to_sql(tuple(result_list))
    except Exception as e:
        print("error3: ", str(e))
    
def get_laptop_pages():
    urls = []
    i=1
    while True:
        url = f"https://kiyas.la/tr/laptop-notebook?page={i}"
        try:
            s = BeautifulSoup(requests.get(url).text, "lxml")
            main = s.find("div", class_="row no-gutters mt-3 mt-sm-0")
            for link in main.find_all("button"):
                urls.append(f"https://kiyas.la/tr/{link.get('data-product-url')}")
            i+=1

        except:
            break
    return urls
        
def main_func():
    urls= get_laptop_pages()
    for url in urls:
        get_write_laptop_data(url)

main_func()
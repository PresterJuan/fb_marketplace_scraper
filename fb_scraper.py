from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import re
from selenium.webdriver.support.ui import Select
from CSV_IO import write_csv, read_csv
from selenium.webdriver.firefox.options import Options
from read_file_write_file import open_file, write_file
import _thread
import requests
import sqlite3
import asyncio
import aiosqlite
import datetime
import multiprocessing
import os


def the_opening(headless_True_or_False, url):
    options = Options()
    options.headless = headless_True_or_False
    browser = webdriver.Firefox(options=options)
    browser.implicitly_wait(30)
    browser.get(url)
    return browser


def log_in(browser, my_email, my_password):
    email = browser.find_element_by_name('email')
    password = browser.find_element_by_name('pass')
    email.click()
    email.send_keys(my_email)
    password.click()
    password.send_keys(my_password)
    password.submit()


def search(browser, term_to_search):
    search_input = browser.find_element_by_xpath(
        "//input[@placeholder='Search Marketplace']")
    search_input.send_keys(term_to_search)
    search_input.send_keys(Keys.ENTER)


# This is old and no longer used
"""
def grab_local_listings(browser):
    local_listings =  browser.find_elements_by_tag_name('img')
    #You can search through the alt tags to see what you've found
    for i in local_listings:
        alt_text = i.get_attribute('alt')
        if 'San Antonio' in alt_text or 'Austin' in alt_text or 'Houston' in alt_text:
            local_listings.remove(i)
            print('Removed: ', alt_text)
        elif 'TX' in alt_text:
            pass
        else:
            local_listings.remove(i)
            print('Removed: ', alt_text)
    return local_listings
"""


def scroll_down(driver):
    SCROLL_PAUSE_TIME = 5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    x = 0
    while True:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        x += 1


def grab_data(browser):
    """Grabs all of the image tags, tries to find their alt text for the descritpion, grabs the next string, which happens to be the price, grabs the url for the post by snagging the previous a tag"""
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    imgs = soup.find_all('img')
    payload = []
    for i in imgs:
        try:
            alt_text = i['alt']
            if 'San Antonio' in alt_text or 'Austin' in alt_text or 'Houston' in alt_text:
                imgs.remove(i)
                print('Removed: ', alt_text)
            elif 'TX' in alt_text:
                stuff = {}
                stuff['description'] = alt_text
                stuff['cost'] = i.find_next(string=True)
                stuff['url'] = 'https://www.facebook.com' + \
                    i.find_previous('a')['href']
                payload.append(stuff)
            else:
                imgs.remove(i)
                print('Removed: ', alt_text)
        except Exception as e:
            print(e)
    return payload


def screen_out(payload, *args):
    """Make what you want the first arg! ex mini for mac mini. The rest of the args are what to avoid. The Put the args in as a tuple so you only have results with args in them, put the payload in and narrow the results to what you want"""
    bad_list = []
    new_list = []
    x = 0
    while x < len(args[0][1:]):
        x += 1
    for i in payload:
        if args[0][0].lower() in i['description'].lower():
            print('\n\n', str(args[0][0]).lower(), 'found')
            for x in args[0][1:]:
                if str(x).lower() in i['description'].lower():
                    print('\n\nscreened out due to', x)
                    try:
                        bad_list.append(i)
                        print('Removed: ', i)
                    except Exception as e:
                        print('\n\n\nEXCEPTION', e)

        else:
            print('mini not found\n', i['description'])
            bad_list.append(i)
    for i in payload:
        if i in bad_list:
            pass
        else:
            new_list.append(i)
    return new_list


# async version
"""
async def get_listings_from_db(search_table, name_of_db):
    conn = await aiosqlite.connect(name_of_db)
    fb_listings = await conn.execute(search_table)
    all_listings = await fb_listings.fetchall()
    await conn.close()
    return all_listings
"""


def get_listings_from_db(search_table, name_of_db):
    """String of SQL to search example: 'SELECT * FROM listings'"""
    conn = sqlite3.connect(name_of_db)
    c = conn.cursor()
    fb_listings = c.execute(search_table)
    all_listings = fb_listings.fetchall()
    conn.close()
    return all_listings


def setup_db(db_name, table_name, *args):
    """Only run this the first time you're setting up a new database
    db_name example: 'al_counties.db', table_name example 'listings', args example ('price','description', 'url')
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {args[0]}")
    conn.commit()
    conn.close()


def save_to_db(dict_instance, table_name, name_of_db):
    conn = sqlite3.connect(name_of_db)
    c = conn.cursor()
    url_to_search = dict_instance['url']
    print(type(url_to_search))
    ban_list_check = c.execute(
        f"SELECT * FROM ban_list WHERE url=(?)", (url_to_search,))
    banned = ban_list_check.fetchone()
    if banned != None:
        print('\n\n\nFound band url:', dict_instance)
        return
    null_test = c.execute(
        f"SELECT * FROM listings WHERE url=(?)", (url_to_search,))
    old_row = null_test.fetchone()
    if old_row == None:
        new_tuple = (int(dict_instance['cost'][1:].replace(
            ',', '')), dict_instance['description'], dict_instance['url'], datetime.date.today())
        c.executemany(
            f'INSERT INTO {table_name} VALUES (?,?,?,?)', {new_tuple})
    else:
        if old_row[0] == int(dict_instance['cost'][1:].replace(',', '')):
            pass
        else:
            new_cost = int(dict_instance['cost'][1:].replace(',', ''))
            c.execute(f"UPDATE {table_name} SET price = (?)", (new_cost,))
            price_change = int(
                dict_instance['cost'][1:].replace(',', '')) - old_row[0]
            change_tuple = (
                dict_instance['url'], dict_instance['description'], price_change, datetime.date.today())
            c.execute(f'INSERT INTO price_change VALUES (?,?,?,?)',
                      {change_tuple})
    conn.commit()
    conn.close()


def ban_urls(table_name, name_of_db, *args):
    conn = sqlite3.connect(name_of_db)
    c = conn.cursor()
    for i in args[0]:
        print(i)
        c.execute(f"""DELETE FROM {table_name} WHERE url=(?)""", (i,))
        conn.commit()
        c.execute(f"""INSERT INTO ban_list VALUES (?)""", (i,))
        conn.commit()
        print('Banned:', i)
    conn.close()

# OLD DO NOT USE


async def save_listing(dict_instance, table_name, name_of_db):
    """dict_instance = dict that contains all of the categories to put in the table, table_name = 'listings' or whatever you called the table, name_of_db = 'al_counties.db' or whatever you named the db"""
    # need to see if the url is currently in the table
    # if the url is in the table, make sure the values haven't changed
    conn = await aiosqlite.connect(name_of_db)
    db_row = await conn.execute(f"SELECT * FROM {table_name} WHERE url = {dict_instance['url']}")
    dict_in_db = await db_row.fetchone()
    await print(tuple(dict_in_db))
    # if the url is in the table, make sure the values haven't changed
    # if the values have changed or it doesn't exist, update the values
    await conn.execute(f"UPDATE {table_name} SET price = {dict_instance['price']}, description = {dict_instance['description']} WHERE url = {dict_instance['url']}")
    conn.commit()


def delete_data(condition, table_name, name_of_db):
    """Condition is the term you are matching for. 
    example:
    DELETE FROM Customers WHERE CustomerName='Alfreds Futterkiste';
    It is like this but you don't have to put in condition, just the part right of the equals sign
    condition = "url='https://www.facebook.com/marketplace/item/280027246507749/'"
    """
    conn = sqlite3.connect(name_of_db)
    c = conn.cursor()
    c.execute(f"""DELETE FROM {table_name} WHERE {condition}""")
    conn.commit()
    conn.close()


def delete_all(table_name, name_of_db):
    conn = sqlite3.connect(name_of_db)
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    url = "https://facebook.com/marketplace"
    setup_db('mac_mini.db', 'listings', ('price', 'description', 'url'))
    email = os.environ.get('FB_EMAIL')
    password = os.environ.get('FB_PASSWORD')
    browser = the_opening(True, url)
    try:
        log_in(browser, email, password)
        time.sleep(5)
        try:
            log_in(browser, email, password)
        except:
            pass
        time.sleep(8)
        try:
            log_in(browser, email, password)
        except:
            pass
        print('login three worked')
        time.sleep(10)
        search(browser, 'mac mini')
        print('search worked')
        scroll_down(browser)
        print('scroll down worked')
        payload = grab_data(browser)
        print('\n\n\npayload grabbed')
        print(payload)
        new_payload = screen_out(
            payload, ('mini', 'ipad', 'imac', 'dell', 'fridge', 'cooler', 'bar', 'keyboard'))
        print('\n\n\nnew_payload worked')
        print(new_payload)
        for i in new_payload:
            print('Down here:', i)
            try:
                save_to_db(i, 'listings', 'mac_mini.db')
            except Exception as e:
                print('\n\n\n\n\nPROBLEM SAVING:', i)
                print(e)
        browser.close()
    except Exception as e:
        print('last exception...oh sh....')
        print(e)
        pass


# For testing in terminal
"""
from importlib import import_module, reload
import os
fb = import_module('fb_scraper')
url = "https://facebook.com/marketplace"
my_email = os.environ.get('FB_EMAIL')
my_password = os.environ.get('FB_PASSWORD')
browser = fb.the_opening(False, url)
fb.log_in(browser,my_email,my_password)
fb.search(browser, 'mac mini')
fb.scroll_down(browser)
payload = fb.grab_data(browser)
new_payload = fb.screen_out(payload,('mini','ipad','imac','dell','keyboard'))
"""

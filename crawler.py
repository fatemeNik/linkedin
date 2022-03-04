
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import math
import sqlite3
import logging


logging.basicConfig(filename='linkedin.log',
                    encoding='utf-8', level=logging.INFO)


def sqlite():
    # db
    conn = sqlite3.connect('linkedin.db')
    cursor = conn.cursor()

    # Creating table
    table = """CREATE TABLE IF NOT EXISTS LINKEDIN(NAME VARCHAR(255), HEADLINE VARCHAR(255),COMPANY VARCHAR(255),
    EDUCATION VARCHAR(255),LOCATION VARCHAR(255),CONNECTIONS VARCHAR(255));"""
    cursor.execute(table)
    return conn, cursor


def insert(conn, cursor, name, headline, company, education, location, connections):
    # parameters
    params = (name, headline, company, education,
              location, connections)
    # store profile in table
    cursor.execute(
        '''INSERT INTO LINKEDIN VALUES (?, ?, ?, ?, ?, ?)''', params)
    conn.commit()

# print inserted rows


def view():

    conn = sqlite3.connect('linkedin.db')
    cursor = conn.cursor()
    print("Data Inserted in the table: ")
    data = cursor.execute('''SELECT * FROM LINKEDIN''')
    for row in data:
        print(row)

    # Closing the connection
    conn.close()


def open_url(url, browser):
    browser.get(url)
    src = browser.page_source
    soup = BeautifulSoup(src, 'lxml')
    return soup


def my_profile_crawler(url, browser):

    soup = open_url(url, browser)
    try:
        name = soup.find(
            'h1', {'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'}).get_text().strip()
        # print(name)
    except:
        name = ""

    try:
        headline = soup.find(
            'div', {'class': 'text-body-medium break-words'}).get_text().strip()
        # print(headline)
    except:
        headline = ""

    try:
        education = soup.find('ul', {'class': 'pv-text-details__right-panel'})

        education = education.find_all(
            'li', {'class': 'pv-text-details__right-panel-item'})
    except:
        education = ""

    # list for company and education
    edu = []

    # if there is no company name
    if(len(education) == 1):
        edu.append("None")

    for i in range(len(education)):
        education = education[i].find(
            'a', {'class': 'pv-text-details__right-panel-item-link link-without-hover-visited t-black'})

        education = education.find('h2', {
            'class': 'pv-text-details__right-panel-item-text hoverable-link-text break-words text-body-small inline'})

        education = education.find(
            'div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp inline'
                    }).get_text().strip()
        # print(education)
        edu.append(education)

    try:
        location = soup.find(
            'span', {'class': 'text-body-small inline t-black--light break-words'}).get_text().strip()
        # print(location)
    except:
        location = ""

    try:
        connections = soup.find(
            'ul', {'class': 'pv-top-card--list pv-top-card--list-bullet display-flex pb1'})

        connections = connections.find('a')
        connections_page_url = 'https://www.linkedin.com/'+connections['href']

        connections = soup.find(
            'li', {'class': 'text-body-small'}).get_text().strip()
        # print(connections)
    except:
        connections = ""

    conn, cursor = sqlite()
    insert(conn, cursor, name, headline,
           edu[0], edu[1], location, connections)

    log = {"name": name, "headline": headline,
           "company": edu[0], "education": edu[1], "location": location, "connections": connections}
    logging.info(log)

    return connections_page_url


def connections_profile_crawler(url, browser):

    soup = open_url(url, browser)

    try:
        name = soup.find(
            'h1', {'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'}).get_text().strip()
        # print(name)
    except:
        name = ""

    try:
        headline = soup.find(
            'div', {'class': 'text-body-medium break-words'}).get_text().strip()
        # print(headline)
    except:
        headline = ""

    try:
        education = soup.find('ul', {'class': 'pv-text-details__right-panel'})

        education_list = education.find_all(
            'li', {'class': 'pv-text-details__right-panel-item'})
    except:
        education_list = ""

    # print("edlen", len(education_list))
    edu = []
    if(len(education_list) == 1):
        edu.append("None")

    for i in range(len(education_list)):
        education_a_tag = education_list[i].find(
            'a', {'class': 'pv-text-details__right-panel-item-link link-without-hover-visited t-black'})

        education_h_tag = education_a_tag.find('h2', {
            'class': 'pv-text-details__right-panel-item-text hoverable-link-text break-words text-body-small inline'})

        education_title = education_h_tag.find(
            'div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp inline',
                    }).get_text().strip()
        # print(education_title)
        edu.append(education_title)

    try:
        location = soup.find(
            'span', {'class': 'text-body-small inline t-black--light break-words'}).get_text().strip()
        # print(location)
    except:
        location = ""

    try:
        connections = soup.find(
            'li', {'class': 'text-body-small'}).get_text().strip()
        # print(connections)
    except:
        connections = ""

    conn, cursor = sqlite()
    insert(conn, cursor, name, headline, edu[0], edu[1], location, connections)
    log = {"name": name, "headline": headline,
           "company": edu[0], "education": edu[1], "location": location, "connections": connections}
    logging.info(log)


def connections_crawler(url, browser):

    soup = open_url(url, browser)
    connections_list = soup.find_all(
        'li', {'class': 'reusable-search__result-container'})
    # print(connections_list)

    # loop through all connections in ine page and find all of their own profile links
    for i in range(len(connections_list)):

        try:
            each_connection = connections_list[i].find(
                'a', {'class': 'app-aware-link'})
            each_connection_page = each_connection['href']
            connections_profile_crawler(each_connection_page, browser)
            time.sleep(5)

        except:
            pass


def get_number_of_connections(url, browser):
    soup = open_url(url, browser)
    connections = soup.find(
        'span', {'class': 't-bold'}).get_text().strip()

    return int(connections)


s = Service('C:/Users/PicoNet/Downloads/chromedriver.exe')
browser = webdriver.Chrome(service=s)
browser.get('https://www.linkedin.com/login')
file = open('login.txt')
data = file.readlines()
username = data[0]
password = data[1]

element_id = browser.find_element_by_id('username')
element_id.send_keys(username)

element_id = browser.find_element_by_id('password')
element_id.send_keys(password)

element_id.submit()

time.sleep(5)

# my profile url
url = 'https://www.linkedin.com/in/fateme-nikkhah-229584214/'
connections_page_url = my_profile_crawler(url, browser)


print(connections_page_url)
time.sleep(5)
connections_crawler(connections_page_url, browser)


num_of_connections = get_number_of_connections(url, browser)
num_of_pages = math.ceil(num_of_connections/10)
for i in range(2, num_of_pages+1):
    page = '&page={:d}'.format(i)
    next_page_url = connections_page_url+page
    connections_crawler(next_page_url, browser)

view()

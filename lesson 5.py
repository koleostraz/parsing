from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymongo
from pymongo.errors import DuplicateKeyError as dke
from datetime import datetime

start = datetime.now()

client = pymongo.MongoClient('localhost', 27017)
db = client.mails
mails_collection = db.mail_collection


def find_send(by, arg: str, text: str):
    element = wait.until(EC.element_to_be_clickable((by, arg)))
    element.send_keys(text)
    return element


def auth():
    find_send(By.NAME, 'username', login).submit()
    find_send(By.NAME, 'password', password).submit()


def get_urls(element, set_url=None):
    if set_url is None:
        set_url = set()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, element)))
    elements = driver.find_elements(By.CLASS_NAME, element)
    for el in elements:
        url_list = [el.get_attribute('href')]
        if url_list[-1] in set_url:
            return set_url
        else:
            set_url.update(url_list)
            elements[-1].send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            return get_urls(element, set_url)


def get_data(urls):
    data_list = []
    for url in urls:
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h2[@class]")))
        dict_data_incoming_emails = {
            '_id': url,
            'url': url,
            'from': driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title'),
            'date': driver.find_element(By.CLASS_NAME, 'letter__date').text,
            'title': driver.find_element(By.XPATH, "//h2[@class]").text,
            'body': driver.find_element(By.XPATH, '//div[contains(@class, "body-content")]').text
        }
        data_list.append(dict_data_incoming_emails)
        time.sleep(1)
    return data_list


def write_to_db(dl, collection=mails_collection):
    for data in dl:
        try:
            collection.insert_one(data)
        except dke:
            print(f'DuplicateKeyError in id: {data["_id"]}')


base_url = 'https://account.mail.ru/'

options = Options()
options.add_argument('uaer-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
wait = WebDriverWait(driver, 30)
driver.maximize_window()


login = 'study.ai_172'
password = 'NextPassword172#'

driver.get(base_url)
auth()

data = get_urls('js-letter-list-item')
data = get_data(data)
write_to_db(data)

print(f'Собранно {len(data)} писем.')
print(f'Время работы: {datetime.now() - start}')

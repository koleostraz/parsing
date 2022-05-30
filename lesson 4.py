from lxml import html
from pprint import pprint
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError as dke


start = datetime.now()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0'
}
base_url = 'https://lenta.ru/parts'


client = MongoClient('localhost', 27017)
db = client['lenta_news_pars']
news = db.news
main_news = db.main_news


def base_request(page=1):
    url = f'{base_url}/news/{page}/'
    response = requests.get(url, headers=headers)
    return html.fromstring(response.text)


def lenta_imp_pars():
    news_list = []
    dom = base_request()
    containers = dom.xpath('//a[@class="card-mini _compact"]')
    for container in containers:
        news_dict = {}
        name = container.xpath('.//span[@class="card-mini__title"]/text()')
        link = container.xpath('.//span[@class="card-mini__title"]/../../@href')
        news_dict['Name'] = name[0]
        news_dict['tags'] = 'Important'
        news_dict['_id'] = link[0]
        if 'https://' in link[0]:
            news_dict['link'] = link[0]
            news_dict['source'] = 'сторонний сайт'
        else:
            link = 'https://lenta.ru' + link[0]
            news_dict['link'] = link
            news_dict['source'] = 'https://lenta.ru/'
        date = int(start.strftime("%Y%m%d"))
        news_dict['date'] = date
        write_to_db(news_dict, main_news)
        write_to_db(news_dict, news, True)
        news_list.append(news_dict)


def lenta_full_pars():
    page = 1
    news_list = []
    for i in range(21):
        dom = base_request(i)
        containers = dom.xpath("//li[@class='parts-page__item']")
        for container in containers:
            news_dict = {}
            name = container.xpath(".//h3[@class='card-full-news__title']/text()")
            link = container.xpath(".//h3[@class='card-full-news__title']/../@href")
            tag = container.xpath(".//span[contains(@class, 'card-full-news__rubric')]/text()")
            news_dict['name'] = name[0]
            try:
                news_dict['tag'] = tag[0]
            except:
                news_dict['tag'] = None
                print('No tags', link[0])
            news_dict['_id'] = link[0]

            if 'https://' in link[0]:
                news_dict['link'] = link[0]
                date = int(start.strftime("%Y%m%d"))
                news_dict['date'] = date
                news_dict['source'] = 'сторонний сайт'
            else:
                list = link[0].split(sep='/')
                date = int(list[2]+list[3]+list[4])
                news_dict['date'] = date
                link = base_url+link[0]
                news_dict['link'] = link
                news_dict['source'] = 'https://lenta.ru/'
            write_to_db(news_dict)
            news_list.append(news_dict)
    lenta_imp_pars()


def write_to_db(news_dict, collection=news, up=False):
    try:
        collection.insert_one(news_dict)
    except dke:
        print(f'DuplicateKeyError in id: {news_dict["_id"]}')
        if up:
            try:
                for doc in collection.find({'_id': news_dict['id']}):
                    print(doc['tag'])
                    tag = doc['tag']
                    tags = tag + news_dict['tags']
                collection.update_one({'_id': news_dict['_id']}, {'$set': {'tag': tags}})
            except:
                print('mistake')


n = lenta_full_pars()
pprint(n)
print(f'Время работы: {datetime.now() - start}.')


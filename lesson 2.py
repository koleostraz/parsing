import json
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
from datetime import datetime


start = datetime.now()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0'
}

base_url = 'https://spb.hh.ru/search/vacancy'

ur_request = input('Искомая вакансия, используйте + вместо пробела: ')
name = ur_request + '_hh_pars.json'
items_on_page = input('Введите количесво вакансий на странице (20, 50 или 100), рекомендуется 20: ')
result_list = []


def base_request(page):
    url = f'{base_url}?clusters=true&area=2&no_magic=true&ored_clusters=true&items_on_page={items_on_page}\
    &enable_snippets=true&salary=&text={ur_request}&page={page}'
    response = requests.get(url, headers=headers)
    return bs(response.text, 'html.parser')


def hh_pars():
    page = 0
    dom = base_request(page)
    while dom.find('a', {'data-qa': 'pager-next'}):
        data_parse = dom.select('div.vacancy-serp-item__layout')
        for data in data_parse:
            vacancy_name = data.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            title_vacancy = vacancy_name.get_text()
            link_vacancy = vacancy_name['href']
            data_money = data.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            vacancy_dict = {}
            dict_money = {}
            if data_money:
                data_money = data_money.get_text().replace('\u202f', '')

                data_list_money = data_money.split()
                dict_money['currency'] = data_list_money[-1]
                if data_money.startswith('от'):
                    dict_money['min_salary'] = int(data_list_money[1])
                elif data_money.startswith('до'):
                    dict_money['max_salary'] = int(data_list_money[1])
                elif len(data_list_money) == 4:
                    dict_money['min_salary'] = int(data_list_money[0])
                    dict_money['max_salary'] = int(data_list_money[2])
            else:
                dict_money['min_salary'] = None
                dict_money['max_salary'] = None
                dict_money['currency'] = None
            vacancy_dict['base_url'] = base_url
            vacancy_dict['vacancy_title'] = title_vacancy
            vacancy_dict['vacancy_link'] = link_vacancy
            vacancy_dict['salary'] = dict_money
            result_list.append(vacancy_dict)
        write_to_file(result_list)
        page += 1
        dom = base_request(page)
    dom = base_request(page)
    data_parse = dom.select('div.vacancy-serp-item__layout')
    for data in data_parse:
        vacancy_name = data.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        title_vacancy = vacancy_name.get_text()
        link_vacancy = vacancy_name['href']
        data_money = data.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vacancy_dict = {}
        dict_money = {}
        if data_money:
            data_money = data_money.get_text().replace('\u202f', '')

            data_list_money = data_money.split()
            dict_money['currency'] = data_list_money[-1]
            if data_money.startswith('от'):
                dict_money['min_salary'] = int(data_list_money[1])
            elif data_money.startswith('до'):
                dict_money['max_salary'] = int(data_list_money[1])
            elif len(data_list_money) == 4:
                dict_money['min_salary'] = int(data_list_money[0])
                dict_money['max_salary'] = int(data_list_money[2])
        else:
            dict_money['min_salary'] = None
            dict_money['max_salary'] = None
            dict_money['currency'] = None
        vacancy_dict['base_url'] = base_url
        vacancy_dict['vacancy_title'] = title_vacancy
        vacancy_dict['vacancy_link'] = link_vacancy
        vacancy_dict['salary'] = dict_money
        result_list.append(vacancy_dict)
    write_to_file(result_list)


def write_to_file(result):
    with open(name, 'w') as file:
        for res in result:
            json.dump(res, file)


hh_pars()
pprint(result_list)
print(len(result_list))
print(f'Время работы: {datetime.now() - start}.')

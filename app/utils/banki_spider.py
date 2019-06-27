# This script loads the responses from http://www.banki.ru/
# Responses and marks are transformed to responses_dataset.csv file
# Copyright 2016 (c) Ilya Zakharkin

from bs4 import BeautifulSoup
import requests
import csv

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
})

def load_data(url, session):
    request = session.get(url)
    return request.text

def extract_response(text):
    soup = BeautifulSoup(text, "lxml")
    resp_text = soup.find('div', {'itemprop': 'description'}).text.strip()
    return resp_text

# end_lists_num states for the number of the last page with reponses,
# so you can vary it

start_lists_num = 1
end_lists_num = 2000  # 11580

with open('responses_dataset.csv', 'w') as csvfile:
    fieldnames = ['mark', 'description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    def iterate_over_list_of_responses(html_list):
        soup = BeautifulSoup(html_list, "lxml")
        resp_list = soup.find('div', {'class' : 'responses-list'})
        items = resp_list.find_all('article', {'class' : 'responses__item'})
        for item in items:
            mark = item.find('div', {'class' : 'responses__item__rating'}).find('span')
            if mark is not None:
                mark = mark.find('meta')
                if mark is not None:
                    mark = mark.get('content')
                    mark = int(mark)
            resp_url = item.find('div', {'class' : 'responses__item__message'}).find('a')
            response = None
            if resp_url is not None:
                resp_url = 'http://www.banki.ru' + resp_url.get('href')
                resp_doc = load_data(resp_url, s)
                response = extract_response(resp_doc)
            if mark is not None and response is not None:
                writer.writerow({'mark' : mark, 'description' : response})

    for page in range(start_lists_num, end_lists_num + 1):
        list_url = 'http://www.banki.ru/services/responses/list/?page=%d' % (page)
        resps_doc = load_data(list_url, s)
        iterate_over_list_of_responses(resps_doc)
        page += 1
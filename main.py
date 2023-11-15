import json
import re


import bs4
import fake_headers
import requests

headers_gen = fake_headers.Headers(os='win', browser='yandex')

response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=headers_gen.generate())
main_html_data = response.text
main_soup = bs4.BeautifulSoup(main_html_data, 'lxml')
results_vacancy = main_soup.find(attrs={"data-qa": "vacancy-serp__results"}, id="a11y-main-content")
vacancy_data = []
for vacancy in results_vacancy.find_all('div', class_='vacancy-serp-item-body'):
    # получаем ссылку на вакансию:
    a_tag = vacancy.find('a')
    link = a_tag['href']

    response = requests.get(link, headers=headers_gen.generate())
    vacancy_html_data = response.text
    vacancy_soup = bs4.BeautifulSoup(vacancy_html_data, 'lxml')
    vacancy_description_text = vacancy_soup.find('div', class_='vacancy-description')
    v = vacancy_description_text.text
    pattern = re.compile("Flask|Django")

    if pattern.search(v):
        # получаем заголовок:
        header = a_tag.text.strip()

        # получаем зарплату
        try:
            salary_tag = vacancy.find('span', class_='bloko-header-section-2')
            salary = salary_tag.text.strip()
            salary_2 = salary.replace('\u202f', ' ')
        except AttributeError:
            salary_2 = 'Размер з/п не указан.'
        # получаем город:
        city_tag = vacancy.find('div', class_='bloko-text', attrs={'data-qa': "vacancy-serp__vacancy-address"})
        city = city_tag.text.split(',')[0]
        # получаем название фирмы
        firm_tag = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary')
        firm = firm_tag.text.strip().replace('\xa0', ' ')

        vacancy_data.append(
          {
            'header': header,
            'salary': salary_2,
            'city': city,
            'firm': firm,
            'link': link
          }
        )

with open('Вакансии.json', 'w', encoding="UTF-8") as f:
    json.dump(vacancy_data, f, ensure_ascii=False, indent=2)
#
#

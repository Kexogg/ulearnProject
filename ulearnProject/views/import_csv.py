import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

import pandas as pd
import re
import io

import requests_cache
from django.http import HttpResponse
from django.shortcuts import redirect
from ulearnProject import models
from xml.etree import ElementTree as ET

def process_row(row):
    if pd.isnull(row['salary_currency']) or (pd.isnull(row['salary_from']) and pd.isnull(row['salary_to'])):
        return None
    if not pd.isnull(row['salary_from']) and not pd.isnull(row['salary_to']):
        row['salary'] = (row['salary_from'] + row['salary_to']) / 2
    elif not pd.isnull(row['salary_from']):
        row['salary'] = row['salary_from']
    else:
        row['salary'] = row['salary_to']
    if row['salary_currency'] != 'RUR':
        row['salary'] = row['salary'] * get_cbrf_rate(row['salary_currency'],
                                                      datetime.strptime(row['published_at'],
                                                                        '%Y-%m-%dT%H'
                                                                        ':%M:%S%z'))
    vacancy_object = models.Vacancy(name=row['name'], area_name=row['area_name'],
                                    salary=row['salary'], published_at=row['published_at'])
    skills = re.split(",|\n", str(row['key_skills']))
    process_row.counter += 1
    return vacancy_object, skills

process_row.counter = 0


def import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"].read().decode("utf-8")
        data = pd.read_csv(io.StringIO(csv_file), low_memory=False)
        with ThreadPoolExecutor() as executor:
            print("Processing", len(data), "vacancies with " + str(threading.active_count()) + " threads")
            vacancies, skills = list(executor.map(process_row, data.iterrows()))
            print("Processed", process_row.counter, "rows.")
        vacancies = [v for v in vacancies if v is not None]
        print("Processed", len(vacancies), "vacancies. Saving...")
        models.Vacancy.objects.bulk_create(vacancies)
        print("Saved vacancies. Processing skills...")
        for vacancy_object in vacancies:
            skill_objects = [models.Skill.objects.get_or_create(name=skill.strip().lower())[0] for skill in skills]
            vacancy_object.skills.set(skill_objects)

        return redirect("..")
    return HttpResponse("Invalid request method.")


def get_cbrf_rate(currency, date):
    # BYR -> BYN after 2016-07-01
    if currency == 'BYR' and date > datetime(2016, 7, 1, tzinfo=timezone(timedelta(hours=0))):
        currency = 'BYN'
    session = requests_cache.CachedSession('hh_cache', expire_after=360)
    response = session.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01{date.strftime("/%m/%Y")}')
    response.raise_for_status()
    tree = ET.fromstring(response.content)
    for node in tree.findall('Valute'):
        if node.find('CharCode').text == currency:
            return float(node.find('VunitRate').text.replace(',', '.'))

    raise ValueError(f'Currency {currency} not found. Date: {date}')

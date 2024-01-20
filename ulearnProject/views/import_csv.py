import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone, timedelta

import pandas as pd
import re
import io

import requests_cache
from django.http import HttpResponse
from django.shortcuts import redirect
from ulearnProject import models
from xml.etree import ElementTree as ET

if os.name != 'nt':
    multiprocessing.set_start_method('fork')


def process_row(row):
    if all(word not in row['name'].lower() for word in ['fullstack', 'фулстак', 'фуллтак', 'фуллстэк', 'фулстэк', 'full stack']):
        return None
    if pd.isnull(row['salary_currency']) or (pd.isnull(row['salary_from']) and pd.isnull(row['salary_to'])) or \
            (pd.isnull(row['published_at'])):
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
    skills = [skill.strip() for skill in re.split(",|\n", str(row['key_skills']))]
    return vacancy_object, skills



def process_chunk(chunk):
    processed_rows = [process_row(row) for _, row in chunk.iterrows()]
    processed_rows = [row for row in processed_rows if row is not None]
    vacancies, skills = zip(*processed_rows)
    vacancies = [v for v in vacancies if v is not None]
    models.Vacancy.objects.bulk_create(vacancies)
    vacancy_skills_list = []
    for vacancy_object, vacancy_skills in zip(vacancies, skills):
        skill_names = [skill.strip().lower() for skill in vacancy_skills]
        existing_skills = models.Skill.objects.filter(name__in=skill_names)
        existing_skill_names = [skill.name for skill in existing_skills]
        new_skill_names = set(skill_names) - set(existing_skill_names)
        new_skills = models.Skill.objects.bulk_create([models.Skill(name=name) for name in new_skill_names])
        all_skills = list(existing_skills) + new_skills
        for skill in all_skills:
            vacancy_skills_list.append(models.VacancySkill(vacancy=vacancy_object, skill=skill))
    models.VacancySkill.objects.bulk_create(vacancy_skills_list)


def import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"].read().decode("utf-8")
        data = pd.read_csv(io.StringIO(csv_file), low_memory=False)
        chunk_size = 10000
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        print(chunks)
        with ProcessPoolExecutor() as executor:
            print("Processing", len(data), "vacancies with " + str(os.cpu_count()) + " processes")
            executor.map(process_chunk, chunks)
        print("Processed", len(data), "rows.")
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

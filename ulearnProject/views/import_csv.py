import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import pandas as pd
import re
import io

from django.http import HttpResponse
from django.shortcuts import redirect
from ulearnProject import models
from ulearnProject.utils import get_cbrf_rate

if os.name != 'nt':
    multiprocessing.set_start_method('fork')


def process_row(row):
    if pd.isnull(row['salary_currency']) or (pd.isnull(row['salary_from']) and pd.isnull(row['salary_to'])) or \
            (pd.isnull(row['published_at'])):
        row['salary'] = None
    else:
        if not pd.isnull(row['salary_from']) and not pd.isnull(row['salary_to']):
            row['salary'] = (row['salary_from'] + row['salary_to']) / 2
        elif not pd.isnull(row['salary_from']):
            row['salary'] = row['salary_from']
        else:
            row['salary'] = row['salary_to']
        if row['salary_currency'] != 'RUR':
            date = datetime.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%S%z')
            date = date.replace(day=1)
            rate = get_cbrf_rate(row['salary_currency'], date)
            if rate is None:
                row['salary'] = None
            else:
                row['salary'] = row['salary'] * rate
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



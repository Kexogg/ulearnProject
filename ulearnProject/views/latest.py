import requests_cache
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render

from ulearnProject.models import Page
from ulearnProject.utils import get_cbrf_rate


def latest(request):
    try:
        session = requests_cache.CachedSession('hh_cache', expire_after=3600)
        data = session.get(
            'https://api.hh.ru/vacancies?text=%22fullstack%22&specialization=1&per_page=10&order_by=publication_time'
            '&only_with_salary=true').json()
        vacancies = {}
        for index, vacancy in enumerate(data['items']):
            vacancies[index] = parse_vacancy(session.get(f'https://api.hh.ru/vacancies/{vacancy["id"]}').json())
        return render(request, 'latest.html',
                      {"page": Page.objects.get(path='/latest/'),
                       'vacancies': vacancies.values()})
    except Exception as e:
        print(e)
        return HttpResponse(status=500, content=f'Error: {e}')


def parse_vacancy(vacancy):
    vacancy['published_at'] = datetime.strptime(vacancy['published_at'], '%Y-%m-%dT%H:%M:%S%z')
    if vacancy['salary']['currency'] != 'RUR':
        if vacancy['salary']['from'] is not None:
            vacancy['salary']['from'] = int(
                vacancy['salary']['from'] * get_cbrf_rate(vacancy['salary']['currency'], vacancy['published_at']))
        if vacancy['salary']['to'] is not None:
            vacancy['salary']['to'] = int(
                vacancy['salary']['to'] * get_cbrf_rate(vacancy['salary']['currency'], vacancy['published_at']))
        vacancy['salary']['currency'] = 'RUR'
    if vacancy['salary']['from'] is not None and vacancy['salary']['to'] is not None:
        vacancy[
            'salary'] = f"от {'{0:,}'.format(vacancy['salary']['from']).replace(',', ' ')} до {'{0:,}'.format(vacancy['salary']['to']).replace(',', ' ')} {vacancy['salary']['currency']}"
    elif vacancy['salary']['from'] is not None:
        vacancy[
            'salary'] = f"{'{0:,}'.format(vacancy['salary']['from']).replace(',', ' ')} {vacancy['salary']['currency']}"
    elif vacancy['salary']['to'] is not None:
        vacancy[
            'salary'] = f"{'{0:,}'.format(vacancy['salary']['to']).replace(',', ' ')} {vacancy['salary']['currency']}"
    vacancy['key_skills'] = ', '.join([skill['name'] for skill in vacancy['key_skills']])
    return vacancy

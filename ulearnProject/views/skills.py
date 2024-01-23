import math
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from ulearnProject.models import SkillStats, Page


def get_graph(skills):
    width = 0.5
    sqrt_len_skills = math.sqrt(skills.values('year').distinct().count())
    if sqrt_len_skills.is_integer():
        rows = cols = int(sqrt_len_skills)
    else:
        rows = int(sqrt_len_skills)
        cols = rows + 1
    fig, axs = plt.subplots(rows, cols)
    fig.set_figwidth(15)
    fig.set_figheight(10)
    fig.subplots_adjust(wspace=0.75)
    fig.subplots_adjust(hspace=0.5)
    fig.suptitle('Востребованность навыков', fontsize=24)
    years = skills.values_list('year', flat=True).distinct()
    for i, year in enumerate(years):
        x = np.arange(skills.filter(year=year).count())
        y = np.array(skills.filter(year=year).values_list('count', flat=True))
        axs[i // cols, i % cols].barh(x, y, width)
        axs[i // cols, i % cols].set_title(year)
        axs[i // cols, i % cols].set_yticks(x)
        axs[i // cols, i % cols].set_yticklabels(
            [skill[:17] + '...' if len(skill) > 20 else skill for skill in
             skills.filter(year=year).values_list('skill', flat=True)], fontsize=8)
        axs[i // cols, i % cols].set_xlabel('Упоминания')
        axs[i // cols, i % cols].set_xlim([0, max(y) * 1.2])
        axs[i // cols, i % cols].grid(True)
        axs[i // cols, i % cols].invert_yaxis()
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


def get_data():
    return SkillStats.objects.order_by('year').all()


def get_content(query):
    return [{'skill': skill['skill'], 'count': skill['count'],
             'fraction': skill['fraction'], 'avg_salary': skill['average_salary']} for skill in
            query[:20].values('skill', 'count', 'fraction', 'average_salary')]


@cache_page(60 * 60 * 24)
def skills(request):
    skills = get_data()
    years = skills.values_list('year', flat=True).distinct()
    content_all_by_frac = {}
    content_all_by_salary = {}
    content_fullstack_by_frac = {}
    content_fullstack_by_salary = {}
    for year in years:
        content_all_by_frac[year] = get_content(skills.order_by('-fraction').filter(year=year, isFullstack=False))
        content_all_by_salary[year] = get_content(skills.order_by('-average_salary').filter(year=year, isFullstack=False))
        content_fullstack_by_frac[year] = get_content(skills.order_by('-fraction').filter(year=year, isFullstack=True))
        content_fullstack_by_salary[year] = get_content(skills.order_by('-average_salary').filter(year=year, isFullstack=True))

    return render(request, 'stats.html',
                  {
                      "page": Page.objects.get(path='/skills/'),
                      "title": "Востребованность навыков",
                      "accordions":
                          {
                              "Топ-20 навыков всех вакансий по годам":
                                  [
                                      {
                                          'title': 'Статистика по доле вакансий',
                                          'columns': {'skill': 'Навык', 'count': 'Кол-во', 'fraction': 'Доля',
                                                      'avg_salary': 'Сред. з/п'},
                                          'type': 'table_grid',
                                          'content': content_all_by_frac
                                      },
                                      {
                                          'title': 'Статистика по средней зарплате',
                                          'columns': {'skill': 'Навык', 'count': 'Кол-во', 'fraction': 'Доля',
                                                      'avg_salary': 'Сред. з/п'},
                                          'type': 'table_grid',
                                          'content': content_all_by_salary
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(skills.filter(isFullstack=False))
                                      },
                                  ],
                              "Топ-20 навыков FullStack-вакансий по годам":
                                  [
                                      {
                                          'title': 'Статистика по доле вакансий',
                                          'columns': {'skill': 'Навык', 'count': 'Кол-во', 'fraction': 'Доля',
                                                      'avg_salary': 'Сред. з/п'},
                                          'type': 'table_grid',
                                          'content': content_fullstack_by_frac
                                      },
                                      {
                                          'title': 'Статистика по средней зарплате',
                                          'columns': {'skill': 'Навык', 'count': 'Кол-во', 'fraction': 'Доля',
                                                      'avg_salary': 'Сред. з/п'},
                                          'type': 'table_grid',
                                          'content': content_fullstack_by_salary
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(skills.filter(isFullstack=True))
                                      },
                                  ]
                          }
                  })

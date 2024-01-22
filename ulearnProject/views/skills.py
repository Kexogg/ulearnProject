import math
from functools import lru_cache

import matplotlib.pyplot as plt
from io import StringIO

import numpy as np
from django.db.models import Q, Count
from django.db.models.functions import ExtractYear
from django.shortcuts import render
from django.db import models
from django.views.decorators.cache import cache_page
from ulearnProject.models import Vacancy, VacancySkill


def get_graph(skills):
    width = 0.35
    sqrt_len_skills = math.sqrt(len(skills))
    if sqrt_len_skills.is_integer():
        rows = cols = int(sqrt_len_skills)
    else:
        rows = int(sqrt_len_skills)
        cols = rows + 1
    fig, axs = plt.subplots(rows, cols)
    fig.set_figwidth(15)
    fig.set_figheight(15)
    fig.subplots_adjust(hspace=0.5)
    fig.subplots_adjust(wspace=0.5)
    fig.suptitle('Востребованность навыков', fontsize=24)
    for i, year in enumerate(skills):
        x = np.arange(len(skills[year]))
        y = np.array(list(skills[year].values()))
        axs[i // cols, i % cols].bar(x, y, width)
        axs[i // cols, i % cols].set_title(year)
        axs[i // cols, i % cols].set_xticks(x)
        axs[i // cols, i % cols].set_xticklabels(list(skills[year].keys()), rotation=90, fontsize=8)
        axs[i // cols, i % cols].set_ylabel('Упоминания')
        axs[i // cols, i % cols].set_xlabel('Навык')
        axs[i // cols, i % cols].set_ylim([0, max(y) * 1.2])
        axs[i // cols, i % cols].grid(True)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


@lru_cache(maxsize=None)
def get_data():
    skills = {}
    skills_fullstack = {}
    for year in range(Vacancy.objects.earliest('published_at').published_at.year,
                      Vacancy.objects.latest('published_at').published_at.year + 1):
        skills_year = VacancySkill.objects.filter(vacancy__published_at__year=year) \
                          .values('skill__name') \
                          .annotate(skill_count=Count('skill')) \
                          .order_by('-skill_count')[:20]
        if len(skills_year) == 0:
            continue
        else:
            skills[year] = {}
        for skill in skills_year:
            skills[year][skill['skill__name']] = skill['skill_count']
        skills_fullstack_year = VacancySkill.objects.filter(Q(vacancy__name__icontains='fullstack') |
                                                            Q(vacancy__name__icontains='фулстак') |
                                                            Q(vacancy__name__icontains='фуллтак') |
                                                            Q(vacancy__name__icontains='фуллстэк') |
                                                            Q(vacancy__name__icontains='фулстэк') |
                                                            Q(vacancy__name__icontains='full stack'),
                                                            vacancy__published_at__year=year) \
                                    .values('skill__name') \
                                    .annotate(skill_count=Count('skill')) \
                                    .order_by('-skill_count')[:20]
        if len(skills_fullstack_year) == 0:
            continue
        else:
            skills_fullstack[year] = {}
        for skill in skills_fullstack_year:
            if year not in skills:
                skills_fullstack[year] = {}
            skills_fullstack[year][skill['skill__name']] = skill['skill_count']

    return skills, skills_fullstack


@cache_page(60 * 60 * 24)
def skills(request):
    skills, skills_fullstack = get_data()
    return render(request, 'stats.html',
                  {
                      "title": "Востребованность навыков",
                      "accordions":
                          {
                              "Топ-20 навыков по годам":
                                  [
                                      {
                                          'title': 'Таблицы',
                                          'columns': {'title': 'Навык', 'count': 'Количество'},
                                          'type': 'table_grid',
                                          'content': {year: [[{'title': k, 'count': v} for k, v in skills[year].items()]] for year in skills}
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(skills)
                                      },
                                  ],
                              "Топ-20 навыков FullStack-вакансий по годам":
                                  [
                                      {
                                          'title': 'Таблицы',
                                          'columns': {'title': 'Навык', 'count': 'Количество'},
                                          'type': 'table_grid',
                                          'content': {year: [[{'title': k, 'count': v} for k, v in skills[year].items()]] for year in skills_fullstack}
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(skills_fullstack)
                                      },
                                  ]
                          }
                  })
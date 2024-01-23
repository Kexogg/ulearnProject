from django.db.models import Q, Case, When, IntegerField, Count
from django.db.models.functions import ExtractYear
from django.http import HttpResponse
from django.shortcuts import redirect
from ulearnProject.models import Vacancy, GeographyStats, DemandStats, VacancySkill, SkillStats
from django.db import models


def create_stats(request):
    if request.method == "POST":
        create_geo_stats()
        create_demand_stats()
        create_skills_stats()
        return redirect("..")
    return HttpResponse("Invalid request method.")


def create_geo_stats():
    fullstack_count = Vacancy.objects.filter(
        Q(name__icontains='fullstack') |
        Q(name__icontains='фулстак') |
        Q(name__icontains='фуллтак') |
        Q(name__icontains='фуллстэк') |
        Q(name__icontains='фулстэк') |
        Q(name__icontains='full stack')
    ).count()
    regions = Vacancy.objects.values('area_name').annotate(
        count=models.Count('id'),
        count_fullstack=models.Sum(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        fraction=models.Count('id') / float(Vacancy.objects.count()) * 100.0,
        avg_salary=models.Avg('salary', output_field=models.IntegerField()),
        avg_salary_fullstack=models.Avg(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then='salary'
                ),
                default=None,
                output_field=IntegerField()
            )
        ),
        fraction_fullstack=models.Sum(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ) / float(fullstack_count) * 100.0
    ).exclude(salary__gt=10000000).exclude(count__lt=100)
    queries = [
        regions.order_by('-fraction')[:10],
        regions.order_by('-fraction_fullstack')[:10],
        regions.exclude(fraction__lt=0.7).exclude(salary=None).order_by('-avg_salary')[:10],
        regions.exclude(fraction__lt=0.7).exclude(salary=None).order_by('-avg_salary_fullstack')[:10]
    ]
    GeographyStats.objects.all().delete()
    GeographyStats.objects.bulk_create(
        [GeographyStats(area_name=region['area_name'], count=region['count'], fraction=region['fraction'],
                        fraction_fullstack=region['fraction_fullstack'],
                        count_fullstack=region['count_fullstack'],
                        average_salary=region['avg_salary'],
                        average_salary_fullstack=region['avg_salary_fullstack']) for q in queries for region in q],
        ignore_conflicts=True)


def create_demand_stats():
    years = Vacancy.objects.annotate(
        year=ExtractYear('published_at')
    ).values('year').annotate(
        count=models.Count('id'),
        avg_salary=models.Avg('salary', output_field=models.IntegerField()),
        count_fullstack=models.Sum(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        avg_salary_fullstack=models.Avg(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then='salary'
                ),
                default=None,
                output_field=IntegerField()
            )
        ),
    ).exclude(salary__gt=10000000).order_by('year')
    DemandStats.objects.all().delete()
    DemandStats.objects.bulk_create(
        [DemandStats(year=year['year'], count=year['count'], fraction_fullstack=year['count_fullstack'],
                     average_salary=year['avg_salary'],
                     count_fullstack=year['count_fullstack'],
                     average_salary_fullstack=year['avg_salary_fullstack']) for year in years],
        ignore_conflicts=True)

def create_skills_stats():
    skills = {}
    skills_fullstack = {}
    for year in range(Vacancy.objects.earliest('published_at').published_at.year,
                      Vacancy.objects.latest('published_at').published_at.year + 1):
        skills_year = VacancySkill.objects.filter(vacancy__published_at__year=year) \
                          .values('skill__name') \
                          .annotate(skill_count=Count('skill'),
                                    fraction=Count('skill') / float(VacancySkill.objects.filter(vacancy__published_at__year=year).count()) * 100.0
                                    ) \
                          .order_by('-skill_count')[:20]
        if len(skills_year) == 0:
            continue
        else:
            skills[year] = {}
        for skill in skills_year:
            skills[year][skill['skill__name']] = {'count': skill['skill_count'], 'fraction': skill['fraction']}
        skills_fullstack_year = VacancySkill.objects.filter(Q(vacancy__name__icontains='fullstack') |
                                                            Q(vacancy__name__icontains='фулстак') |
                                                            Q(vacancy__name__icontains='фуллтак') |
                                                            Q(vacancy__name__icontains='фуллстэк') |
                                                            Q(vacancy__name__icontains='фулстэк') |
                                                            Q(vacancy__name__icontains='full stack'),
                                                            vacancy__published_at__year=year) \
                                    .values('skill__name') \
                                    .annotate(skill_count=Count('skill'),
                                              fraction=Count('skill') / float(VacancySkill.objects.filter(Q(vacancy__name__icontains='fullstack') |
                                                            Q(vacancy__name__icontains='фулстак') |
                                                            Q(vacancy__name__icontains='фуллтак') |
                                                            Q(vacancy__name__icontains='фуллстэк') |
                                                            Q(vacancy__name__icontains='фулстэк') |
                                                            Q(vacancy__name__icontains='full stack'),
                                                            vacancy__published_at__year=year).count()) * 100.0

                                              ) \
                                    .order_by('-skill_count')[:20]
        if len(skills_fullstack_year) == 0:
            continue
        else:
            skills_fullstack[year] = {}
        for skill in skills_fullstack_year:
            if year not in skills:
                skills_fullstack[year] = {}
            skills_fullstack[year][skill['skill__name']] = {'count': skill['skill_count'], 'fraction': skill['fraction']}

    SkillStats.objects.all().delete()
    SkillStats.objects.bulk_create(
        [SkillStats(year=year, skill=skill, count=skills[year][skill]['count'],
                    fraction=skills[year][skill]['fraction'], isFullstack=False)
         for year in skills for skill in skills[year]],
        ignore_conflicts=True)
    SkillStats.objects.bulk_create(
        [SkillStats(year=year, skill=skill, count=skills_fullstack[year][skill]['count'],
                    fraction=skills_fullstack[year][skill]['fraction'], isFullstack=True)
         for year in skills_fullstack for skill in skills_fullstack[year]],
        ignore_conflicts=True)

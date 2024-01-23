"""
URL configuration for ulearnProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import ulearnProject.views.home
import ulearnProject.views.geography
import ulearnProject.views.skills
import ulearnProject.views.demand
import ulearnProject.views.latest
import ulearnProject.views.import_csv
import ulearnProject.views.create_stats

urlpatterns = [
    path('admin/import_csv/', ulearnProject.views.import_csv.import_csv, name='ulearnProject_vacancy_import_csv'),
    path('admin/create_stats/', ulearnProject.views.create_stats.create_stats, name='ulearnProject_vacancy_create_stats'),
    path('admin/', admin.site.urls),
    path('', ulearnProject.views.home.home),
    path('geography/', ulearnProject.views.geography.geography),
    path('skills/', ulearnProject.views.skills.skills),
    path('demand/', ulearnProject.views.demand.demand),
    path('latest/', ulearnProject.views.latest.latest),
]

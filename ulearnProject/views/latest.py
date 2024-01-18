from django.shortcuts import render


def latest(request):
    return render(request, 'latest.html', {})
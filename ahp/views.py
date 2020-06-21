from django.shortcuts import render, redirect, reverse
from django.urls import resolve
from django.http import HttpResponse

from ahp import models

# Create your views here.

def home(request):
    if request.method == 'POST':
        r = models.CriterionsAlternativesAmount(
            criterions=request.POST.get('criterions'),
            alternatives=request.POST.get('alternatives'),
        )
        r.save()
        return redirect(start_analysis, id=r.pk)
    else:
        return render(request, 'home_page.html')

def start_analysis(request, id):
    if request.method == 'POST':
        return HttpResponse('POST')
    else:
        record = models.CriterionsAlternativesAmount.objects.get(pk=id)
        context = {}
        context['criterions'] = [x for x in range(1, record.criterions+1)]
        context['alternatives'] = [x for x in range(1, record.alternatives+1)]

        return render(request, 'start_analysis_page.html', context)
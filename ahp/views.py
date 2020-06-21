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
    record = models.CriterionsAlternativesAmount.objects.get(pk=id)
    cnum_list = [x for x in range(1, record.criterions+1)]
    anum_list = [x for x in range(1, record.alternatives+1)]

    if request.method == 'POST':
        for i in cnum_list:
            r = models.CriterionsNames(
                fk_id=id,
                cname=request.POST.get(f'c_{i}')
            )
            r.save()
        for i in anum_list:
            r = models.AlternativesNames(
                fk_id=id,
                aname=request.POST.get(f'a_{i}')
            )
            r.save()
        return redirect(analysis_info, id=r.pk)
    else:
        context = {'criterions': cnum_list, 'alternatives': anum_list}
        return render(request, 'start_analysis_page.html', context)

def analysis_info(request, id):
    cnames = models.CriterionsNames.objects.raw(f'SELECT * from ahp_criterionsnames where fk_id=id')
    anames = models.AlternativesNames.objects.raw(f'SELECT * from ahp_alternativesnames where fk_id=id')

    if request.method == 'POST':
        pass
    else:
        context = {'criterions': cnames, 'alternatives': anames}
        return render(request, 'analysis_info_page.html', context)
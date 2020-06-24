from django.shortcuts import render, redirect, reverse
from django.urls import resolve
from django.http import HttpResponse

from ahp import models

import numpy as np
import pandas as pd

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
        return redirect(analysis_info, id=id)
    else:
        context = {'criterions': cnum_list, 'alternatives': anum_list}
        return render(request, 'start_analysis_page.html', context)

def analysis_info(request, id):
    cnames = models.CriterionsNames.objects.raw(
        f'SELECT * from ahp_criterionsnames where fk_id={id}',
        )
    anames = models.AlternativesNames.objects.raw(
        f'SELECT * from ahp_alternativesnames where fk_id={id}',
        )

    if request.method == 'POST':
        for a in anames:
            for c in cnames:
                r = models.AlternativesCriterionsInfo(
                    fk_id = id,
                    c_id = c.id,
                    a_id = a.id,
                    value = request.POST.get(f'{a.id}_{c.id}'),
                )
                r.save()
        return redirect(criterions_comparison, id=id)
    else:
        context = {'criterions': cnames, 'alternatives': anames}
        return render(request, 'analysis_info_page.html', context)


def criterions_comparison(request, id):
    """
    Метод для ввода и сохранения информации по сравнению критериев
    """
    cnames = models.CriterionsNames.objects.raw(f'SELECT * from ahp_criterionsnames where fk_id={id}')
    if request.method == 'POST':
        for c1, item1 in enumerate(cnames):
            c1 = c1 + 1
            for c2, item2 in enumerate(cnames):
                c2 = c2 + 1
                if c2 > c1:
                    r = models.CriterionsComparison(
                        fk_id = id,
                        c1 = item1.id,
                        c2 = item2.id,
                        c1c2_value = request.POST.get(f'{item1.id}_{item2.id}'),
                    )
                    r.save()
        return redirect(criterions_comparison_show, id=id)
    else:
        context = {'criterions': cnames}
        return render(request, 'criterions_comparison_page.html', context)

def criterions_comparison_show(request, id):
    """
    Метод для отображения информации по сравнению критериев
    """
    criterions = models.CriterionsNames.objects.raw(
        f'SELECT * from ahp_criterionsnames where fk_id={id}',
    )
    comparison_df = _get_criterions_comparison_table(id=id)

    if request.method == 'POST':
        pass
    else:
        context = { 
            'comparison_table': comparison_df.to_html(),
        }
        return render(request, 'criterions_comparison_show_page.html', context)

def alternatives_comparison(request):
    pass

def _get_criterions_comparison_table(id: int) -> pd.DataFrame:
    """
    Метод для формирования датафрейма со сравнением критериев
    """
    items = models.CriterionsNames.objects.raw(
        f'SELECT * from ahp_criterionsnames where fk_id={id}',
    )
    values = models.CriterionsComparison.objects.raw(
        f'SELECT * from ahp_criterionscomparison where fk_id={id}',
    )
    values = [v for v in values]
    values = {
        f'{c1}_{c2}': v for c1, c2,v in zip(
            [i.c1 for i in values],
            [i.c2 for i in values],
            [i.c1c2_value for i in values],
        )
    }
    
    cnames = [i.cname for i in items]
    df = pd.DataFrame(columns=cnames)

    for i, row in enumerate(items):
        r = []
        i1 = i + 1
        for j, col in enumerate(items):
            j1 = j + 1
            if j1 == i1:
                r.append(1)
            else:
                v = values.get(f'{row.id}_{col.id}') or values.get(f'{col.id}_{row.id}')
                if j1 > i1:
                    r.append(v)
                else:
                    r.append(1/v)
        df = df.append(pd.DataFrame([r], columns=cnames), ignore_index=True)

    df = df.set_index([pd.Index(cnames)], 'R')

    return df


                    
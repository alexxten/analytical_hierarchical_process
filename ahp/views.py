import copy
import enum
from typing import Tuple

import pandas as pd

from django.shortcuts import render, redirect, reverse
from django.urls import resolve
from django.http import HttpResponse

from ahp import models


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
        if "check" in request.POST:
            consistency_mark, df = _get_consistency_mark(comparison_table=comparison_df)
            context = { 
                'comparison_table': df.to_html(),
                'consistency_mark': consistency_mark,
                'show_next': True,
                'show_check': False,
            }
            return render(request, 'criterions_comparison_show_page.html', context)
        elif 'next' in request.POST:
            return redirect(alternatives_comparison, id=id)
    else:
        context = { 
            'comparison_table': comparison_df.to_html(),
            'show_next': False,
            'show_check': True,
        }
        return render(request, 'criterions_comparison_show_page.html', context)

def alternatives_comparison(request, id):
    """
    Метод для ввода и сохранения информации по сравнению альтернатив
    """
    anames = models.AlternativesNames.objects.raw(f'SELECT * from ahp_alternativesnames where fk_id={id}')
    if request.method == 'POST':
        for a1, item1 in enumerate(anames):
            a1 = a1 + 1
            for a2, item2 in enumerate(anames):
                a2 = a2 + 1
                if a2 > a1:
                    r = models.AlternativesComparison(
                        fk_id = id,
                        a1 = item1.id,
                        a2 = item2.id,
                        a1a2_value = request.POST.get(f'{item1.id}_{item2.id}'),
                    )
                    r.save()
        # return redirect(alternatives_comparison_show, id=id)
    else:
        context = {'alternatives': anames}
        return render(request, 'alternatives_comparison_page.html', context)

def make_alternatives_comparison(id: int):
    return 

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

def _get_consistency_mark(comparison_table: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    df = copy.deepcopy(comparison_table)
    items_cols_num = len(df.columns)
    items_names = [col for col in df.columns]

    df['component_eval'] = __component_evaluation(data=df)
    df = df.append(df.sum(axis=0), ignore_index=True)
    df['normalized_eval'] = __normalized_evaluation(data=df)

    consistency_mark = __consistency_mark(data=df, items_num=items_cols_num)

    col_names = items_names + ['Оценки компонент соб.вектора', 'Нормализованные оценки']
    col_names = {k: v for k, v in zip(df.columns, col_names)}
    row_names = items_names + ['Суммы']
    row_names = {k: v for k, v in zip(df.index, row_names)}

    df = df.rename(
        columns=col_names,
        index=row_names,
    )

    return consistency_mark, df


def __component_evaluation(data: pd.DataFrame):
    df = copy.deepcopy(data)
    mult = 1
    for col in df.columns:
        mult *= df[col]
    c_eval = mult ** (1/len(df.columns))

    return c_eval

def __normalized_evaluation(
    *,
    data: pd.DataFrame, 
    component_eval_col: str = 'component_eval',
) -> pd.DataFrame:
    df = copy.deepcopy(data)
    normalized_eval = df[component_eval_col].iloc[:-1] / df[component_eval_col].iloc[[-1]].values[0]
    normalized_eval = normalized_eval.append(pd.Series(normalized_eval.sum()), ignore_index=True)
    return normalized_eval
    
def __consistency_mark(
    *,
    data: pd.DataFrame, 
    normalized_eval_col: str = 'normalized_eval', 
    items_num: int,
) -> float:
    df = copy.deepcopy(data)

    L = (df.iloc[-1, :-2] * df[normalized_eval_col].iloc[:-1]).sum()
    consistency_index = (L - items_num) / (items_num - 1)
    consistency_mark = consistency_index / RandomConsistencyIndex[f'item_{items_num}'].value
    
    return consistency_mark

class RandomConsistencyIndex(enum.Enum):
    item_1 = 0
    item_2 = 0
    # TODO что с этим делать??? division by zero
    item_3 = 0.58
    item_4 = 0.9
    item_5 = 1.12
    item_6 = 1.24
    item_7 = 1.32
    item_8 = 1.41
    item_9 = 1.45
    item_10 = 1.49
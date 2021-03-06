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
        c_num = request.POST.get('c_num')
        a_num = request.POST.get('a_num')
        if c_num is None or a_num is None:
            return render(
                request, 
                'error_500.html', 
                {'description': 'Отсутствуют необходимые данные'},
            )
        else:
            r = models.CriterionsAlternativesAmount(
                criterions=c_num,
                alternatives=a_num,
            )
            r.save()
            return redirect(start_analysis, id=r.pk)
    else:
        c_max_num = [i for i in range(3, 11)]
        a_max_num = [i for i in range(3, 11)]
        context = {
            'c_max_num': c_max_num,
            'a_max_num': a_max_num,
        }
        return render(request, 'home_page.html', context)

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
        if 'show' in request.POST:
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
            comparison_df = __get_criterions_comparison_table(id=id)
            context = {
                'criterions': cnames, 
                'comparison_df': comparison_df.to_html(
                    classes=['table', 'table-striped', 'table-bordered', 'text-center'],
                ),
                'show': True,
            }
            return render(request, 'criterions_comparison_page.html', context)
        elif 'check' in request.POST:
            comparison_df = __get_criterions_comparison_table(id=id)
            consistency_mark, df = __get_consistency_mark(comparison_table=comparison_df)
            context = { 
                'comparison_df': df.to_html(
                    classes=['table', 'table-striped', 'table-bordered', 'text-center'],
                ),
                'consistency_mark': consistency_mark,
                'check': True,
            }
            return render(request, 'criterions_comparison_page.html', context)
        elif 'main' in request.POST:
            return redirect(home)
        else:
            return redirect(alternatives_comparison, id=id)
    else:
        context = {'criterions': cnames}
        return render(request, 'criterions_comparison_page.html', context)

def alternatives_comparison(request, id):
    """
    Метод для ввода и сохранения информации по сравнению альтернатив
    """
    alternatives = models.AlternativesNames.objects.raw(
        f'SELECT * from ahp_alternativesnames where fk_id={id}',
    )
    criterions = models.CriterionsNames.objects.raw(
        f'SELECT * from ahp_criterionsnames where fk_id={id}',
    )
    analysis_info_table = __get_analysis_info(id=id)
    analysis_info_table = analysis_info_table.to_html(
        classes=['table', 'table-striped', 'table-bordered', 'text-center'],
    )

    df_dict = {}
    consistency_marks = {}
    df_consistency_dict = {}

    if request.method == 'POST':
        if 'show' in request.POST:
            for c in criterions:
                for a1, item1 in enumerate(alternatives):
                    a1 = a1 + 1
                    for a2, item2 in enumerate(alternatives):
                        a2 = a2 + 1
                        if a2 > a1:
                            r = models.AlternativesComparison(
                                fk_id = id,
                                c_id=c.id,
                                a1=item1.id,
                                a2=item2.id,
                                a1a2_value = request.POST.get(f'{c.id}_{item1.id}_{item2.id}'),
                            )
                            r.save()
                df = __get_alternatives_comparison_table(id=id, c_id=int(c.id))
                df_dict[c.id] = df.to_html(
                    classes=['table', 'table-striped', 'table-bordered', 'text-center'],
                )

            context = {
                'alternatives': alternatives, 
                'criterions': criterions,
                'show': True,
                'df_dict': df_dict,
                'check': False,
            }
            return render(request, 'alternatives_comparison_page.html', context)
        
        elif 'check' in request.POST:
            for c in criterions:
                df = __get_alternatives_comparison_table(id=id, c_id=int(c.id))
                consistency_mark, df = __get_consistency_mark(comparison_table=df)
                df_consistency_dict[c.id] = df.to_html(
                    classes=['table', 'table-striped', 'table-bordered', 'text-center'],
                )
                consistency_marks[c.id] = consistency_mark
            
            show_summary_btn = [i < 1 for i in consistency_marks.values()]
            show_summary_btn = False if False in show_summary_btn else True

            context = {
                'alternatives': alternatives, 
                'criterions': criterions,
                'show': False,
                'df_consistency_dict': df_consistency_dict,
                'check': True,
                'consistency_marks': consistency_marks,
                'show_summary_btn': show_summary_btn,
            }
            return render(request, 'alternatives_comparison_page.html', context)

        elif 'main' in request.POST:
            return redirect(home)

        else:
            return redirect(final_comparison, id=id)

    else:
        context = {
            'alternatives': alternatives, 
            'criterions': criterions,
            'show': False,
            'check': False,
            'analysis_info': analysis_info_table,
        }
        return render(request, 'alternatives_comparison_page.html', context)

def final_comparison(request, id):
    if request.method == 'POST':
            return redirect(home)
    else:
        alternatives = models.AlternativesNames.objects.raw(
            f'SELECT * from ahp_alternativesnames where fk_id={id}',
        )
        result = __get_global_priority_value(id=id)
        context = {
            'alternatives': alternatives,
            'result': result,
        }
        return render(request, 'final_comparison_page.html', context)

def __get_alternatives_comparison_table(id: int, c_id: int) -> pd.DataFrame:
    """
    Метод для формирования датафрейма со сравнением альтернатив по определенному критерию
    """
    items = models.AlternativesNames.objects.raw(
        f'SELECT * from ahp_alternativesnames where fk_id={id}',
    )
    values = models.AlternativesComparison.objects.raw(
        f'SELECT * from ahp_alternativescomparison where fk_id={id} and c_id={c_id}',
    )
    values = [v for v in values]
    values = {
        f'{a1}_{a2}': v for a1, a2,v in zip(
            [i.a1 for i in values],
            [i.a2 for i in values],
            [i.a1a2_value for i in values],
        )
    }
    
    anames = [i.aname for i in items]
    df = pd.DataFrame(columns=anames)

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
        df = df.append(pd.DataFrame([r], columns=anames), ignore_index=True)

    df = df.set_index([pd.Index(anames)])
    return df

def __get_analysis_info(id: int) -> pd.DataFrame:
    """
    Метод для получения информации о значениях критериев по альтернативам
    """
    criterions = models.CriterionsNames.objects.raw(
        f'SELECT * from ahp_criterionsnames where fk_id={id}',
    )
    alternatives = models.AlternativesNames.objects.raw(
        f'SELECT * from ahp_alternativesnames where fk_id={id}',
    )

    values = models.AlternativesCriterionsInfo.objects.raw(
        f'SELECT * from ahp_alternativescriterionsinfo where fk_id={id}'
    )
    values = [v for v in values]
    values = {
        f'{a_id}_{c_id}': v for a_id, c_id, v in zip(
            [i.a_id for i in values],
            [i.c_id for i in values],
            [i.value for i in values],
        )
    }

    cnames = [c.cname for c in criterions]
    anames = [a.aname for a in alternatives]
    df = pd.DataFrame(columns=cnames)

    for a in alternatives:
        row = []
        for c in criterions:
            val = values.get(f'{a.id}_{c.id}')
            row.append(val)
        df = df.append(pd.DataFrame([row], columns=cnames), ignore_index=True)

    df = df.set_index([pd.Index(anames)])
    return df




def __get_criterions_comparison_table(id: int) -> pd.DataFrame:
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

    df = df.set_index([pd.Index(cnames)])

    return df

def __get_consistency_mark(comparison_table: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    Метод для получения показателя согласованности
    """
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

def __get_global_priority_value(id: int) -> dict:
    """
    Метод для подведения итогов посредством расчета глобального критерия
    """
    result = {}

    criterions = models.CriterionsNames.objects.raw(
        f'SELECT * from ahp_criterionsnames where fk_id={id}',
    )
    c_df = __get_criterions_comparison_table(id=id)
    _, c_df = __get_consistency_mark(comparison_table=c_df)
    norm_c_df = c_df['Нормализованные оценки'].iloc[:-1]
    # indexes - criterions

    df = pd.DataFrame()
    for c in criterions:
        a_df = __get_alternatives_comparison_table(id=id, c_id=int(c.id))
        _, a_df = __get_consistency_mark(comparison_table=a_df)
        norm_df = a_df['Нормализованные оценки'].iloc[:-1]
        # indexes - alternatives
        df[c.cname] = norm_df

    for a in df.iterrows():
        res = 0
        for i in norm_c_df.index:
            mult = (a[1][a[1].index == i] * norm_c_df[i]).values[0]
            res += mult
        result[a[0]] = res

    return {k: v for k, v in sorted(result.items(), key=lambda item: item[1])}


def __component_evaluation(data: pd.DataFrame) -> pd.Series:
    """
    Оценка компонент
    """
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
    """
    Нормализованная оценка
    """
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
    """
    Показатель согласованности
    """
    df = copy.deepcopy(data)

    L = sum([v1*v2 for v1, v2 in zip(df.iloc[-1, :-2],df[normalized_eval_col].iloc[:-1])])
    consistency_index = (L - items_num) / (items_num - 1)
    consistency_mark = consistency_index / RandomConsistencyIndex[f'item_{items_num}'].value
    
    return consistency_mark

class RandomConsistencyIndex(enum.Enum):
    item_1 = 0
    item_2 = 0
    # TODO how to handle division by zero
    item_3 = 0.58
    item_4 = 0.9
    item_5 = 1.12
    item_6 = 1.24
    item_7 = 1.32
    item_8 = 1.41
    item_9 = 1.45
    item_10 = 1.49

def handler404(request, exception):
    return render(request, 'error_404.html')

def handler500(request):
    return render(request, 'error_500.html')
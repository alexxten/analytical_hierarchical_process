from django.urls import path, re_path

from ahp import views

urlpatterns = [
    re_path(r'^home/$', views.home, name='home'),
    path('start-analysis/id=<id>', views.start_analysis, name='start'),
    path('analysis-info/id=<id>', views.analysis_info, name='info'),
    path('criterions-comparison/id=<id>', views.criterions_comparison, name='criterions comparison'),
    path('criterions-comparison-show/id=<id>', views.criterions_comparison_show, name='criterions comparison show'),
    path('alternatives-comparison/id=<id>', views.alternatives_comparison, name='alternatives comparison'),
    # path('alternatives-comparison-show/id=<id>', views.alternatives_comparison_show, name='alternatives comparison show'),

]
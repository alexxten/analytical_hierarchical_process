from django.urls import path, re_path

from ahp import views

urlpatterns = [
    re_path(r'^home/$', views.home, name='home'),
    path('start-analysis/id=<id>', views.start_analysis, name='start'),
]
from django.urls import path

from robots import views

urlpatterns = [
    path('weekly_report/', views.weekly_report, name='weekly_report'),
]

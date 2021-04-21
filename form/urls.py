from django.urls import path, include
from . import views

urlpatterns = [
    path('analysis', views.analysis, name='analysis'),
]

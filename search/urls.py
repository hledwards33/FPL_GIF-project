from django.urls import path, include
from . import views

urlpatterns = [
    path('barrace', views.search, name='barrace'),
]

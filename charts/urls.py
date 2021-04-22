from django.urls import path, include
from . import views

urlpatterns = [
    path('graphs', views.graphs, name='graphs'),
    path('graphs_result', views.graphs_result, name='graphs_result'),
]
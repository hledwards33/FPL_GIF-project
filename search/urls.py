from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('barrace', views.search, name='barrace'),
    path('search_result', views.search_result, name='search_result'),
]

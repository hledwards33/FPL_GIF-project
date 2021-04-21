from django.contrib import admin
from django.urls import path, include
from search import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('search/', include('search.urls')),
    path('form/', include('form.urls')),
    path('charts/', include('charts.urls')),
]

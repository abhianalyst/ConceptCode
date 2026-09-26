from django.urls import path
from . import views

app_name = 'nlp_module'

urlpatterns = [
    path('', views.search_page, name='search'),
    path('api/search/', views.search_api, name='search-api'),
]
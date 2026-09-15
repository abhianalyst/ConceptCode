from django.urls import path
from . import views

app_name = 'ml_module'

urlpatterns = [
    path('weak-areas/', views.weak_areas_api, name='weak-areas'),
    path('recommended/', views.recommended_topic_api, name='recommended'),
]
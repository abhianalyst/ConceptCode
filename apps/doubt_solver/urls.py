from django.urls import path
from . import views

app_name = 'doubt_solver'

urlpatterns = [
    path('', views.doubt_solver, name='solver'),
    path('ask/', views.ask_doubt, name='ask'),
    path('<int:doubt_id>/delete/', views.delete_doubt, name='delete'),
]
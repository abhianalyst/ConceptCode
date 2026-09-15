from django.urls import path
from . import views

app_name = 'doubt_solver'

urlpatterns = [
    # Doubt Solver (FR-07)
    path('', views.doubt_solver, name='solver'),
    path('ask/', views.ask_doubt, name='ask'),
    path('<int:doubt_id>/delete/', views.delete_doubt, name='delete'),

    # Concept Explainer (FR-08)
    path('topics/<int:topic_id>/explain/', views.explain_topic, name='explain-topic'),
    path('topics/<int:topic_id>/regenerate/', views.regenerate_explanation, name='regenerate'),

    # Question Explainer (NEW)
    path('questions/<int:question_id>/explain/', views.explain_question_view, name='explain-question'),
]
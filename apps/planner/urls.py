from django.urls import path

from . import views

app_name = "planner"

urlpatterns = [
    path("", views.planner_dashboard, name="dashboard"),
    path("create/", views.create_plan, name="create-plan"),
    path("regenerate/", views.regenerate_plan, name="regenerate-plan"),
    path("task/<int:task_id>/complete/", views.complete_task, name="complete-task"),
    path("task/<int:task_id>/skip/", views.skip_task, name="skip-task"),
]
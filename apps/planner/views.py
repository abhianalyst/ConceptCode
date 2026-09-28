from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import StudyPlan, StudyTask
from .services import StudyPlanner, StudyTaskService


@login_required
def planner_dashboard(request):
    """Main planner page — today's tasks + progress + upcoming week."""
    plan = StudyPlan.objects.filter(user=request.user, is_active=True).first()

    if not plan:
        return redirect("planner:create-plan")

    today = timezone.localdate()
    todays_tasks = StudyTaskService.todays_tasks(plan)
    upcoming_tasks = StudyTaskService.upcoming_tasks(plan, days=7)

    # Progress per day for the next 7 days (for calendar strip)
    calendar_strip = []
    for i in range(7):
        day = today + timedelta(days=i)
        day_tasks = plan.tasks.filter(scheduled_date=day)
        calendar_strip.append({
            "date": day,
            "label": day.strftime("%a"),
            "num": day.day,
            "total": day_tasks.count(),
            "completed": day_tasks.filter(status=StudyTask.Status.COMPLETED).count(),
            "is_today": day == today,
        })

    context = {
        "plan": plan,
        "todays_tasks": todays_tasks,
        "upcoming_tasks": upcoming_tasks,
        "calendar_strip": calendar_strip,
    }
    return render(request, "planner/dashboard.html", context)


@login_required
def create_plan(request):
    """Setup wizard to create a study plan."""
    existing = StudyPlan.objects.filter(user=request.user, is_active=True).first()

    if request.method == "POST":
        exam_date_str = request.POST.get("exam_date", "").strip()
        daily_hours_str = request.POST.get("daily_hours", "4").strip()

        try:
            from datetime import date
            exam_date = date.fromisoformat(exam_date_str)
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid exam date.")
            return render(request, "planner/create.html", {"existing": existing})

        try:
            daily_hours = int(daily_hours_str)
            if not (1 <= daily_hours <= 16):
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Daily hours must be between 1 and 16.")
            return render(request, "planner/create.html", {"existing": existing})

        if exam_date <= timezone.localdate():
            messages.error(request, "Exam date must be in the future.")
            return render(request, "planner/create.html", {"existing": existing})

        plan = StudyPlanner.generate_plan(
            user=request.user,
            exam_date=exam_date,
            daily_hours=daily_hours,
        )
        messages.success(
            request,
            f"Study plan generated! {plan.total_tasks} tasks scheduled.",
        )
        return redirect("planner:dashboard")

    context = {
        "existing": existing,
        "default_exam_date": (timezone.localdate() + timedelta(days=180)).isoformat(),
    }
    return render(request, "planner/create.html", context)


@login_required
def regenerate_plan(request):
    """Regenerate the active plan using the same settings."""
    plan = StudyPlan.objects.filter(user=request.user, is_active=True).first()
    if not plan:
        messages.error(request, "No active plan to regenerate.")
        return redirect("planner:create-plan")

    new_plan = StudyPlanner.generate_plan(
        user=request.user,
        exam_date=plan.exam_date,
        daily_hours=plan.daily_hours,
    )
    messages.success(
        request,
        f"Plan regenerated! {new_plan.total_tasks} tasks scheduled.",
    )
    return redirect("planner:dashboard")


@login_required
@require_POST
def complete_task(request, task_id):
    """Mark a task as completed (AJAX)."""
    task = StudyTaskService.mark_completed(task_id, request.user)
    if not task:
        return JsonResponse({"error": "Task not found."}, status=404)

    plan = task.plan
    return JsonResponse({
        "success": True,
        "task_id": task.id,
        "status": task.status,
        "plan_progress": plan.progress_percent,
        "completed_tasks": plan.completed_tasks,
        "total_tasks": plan.total_tasks,
    })


@login_required
@require_POST
def skip_task(request, task_id):
    """Mark a task as skipped (AJAX)."""
    task = StudyTaskService.mark_skipped(task_id, request.user)
    if not task:
        return JsonResponse({"error": "Task not found."}, status=404)

    plan = task.plan
    return JsonResponse({
        "success": True,
        "task_id": task.id,
        "status": task.status,
        "plan_progress": plan.progress_percent,
    })
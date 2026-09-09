from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    LoginForm,
    ProfileForm,
    RegistrationForm,
    QuestionForm,
    QuestionImportForm,
    QuestionFilterForm,
)
from .models import Profile
from .permissions import admin_required
from .services.email_verification import send_verification_email

from apps.core.models import (
    Subject,
    Chapter,
    Topic,
    Question,
)

# IMPORTANT:
# Only import QuestionImportService.
# Do NOT import anything from question_generator.
from apps.core.services.question_import import QuestionImportService


User = get_user_model()


# ============================================================
# REGISTRATION
# ============================================================

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Create profile for the user.
            Profile.objects.create(
                user=user
            )

            send_verification_email(
                request,
                user,
            )

            return redirect(
                "accounts:verification-pending"
            )

    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


# ============================================================
# EMAIL VERIFICATION
# ============================================================

def verification_pending(request):
    return render(
        request,
        "accounts/verification_pending.html",
    )


def verify_email(request, user_id, token):
    try:
        user = User.objects.get(
            pk=user_id
        )

    except User.DoesNotExist:
        return render(
            request,
            "accounts/email_verification_failed.html",
            {
                "message": "Invalid verification link.",
            },
            status=400,
        )

    if user.email_verified:
        return render(
            request,
            "accounts/email_verification_failed.html",
            {
                "message": (
                    "This email address has already "
                    "been verified."
                ),
            },
            status=400,
        )

    if not default_token_generator.check_token(
        user,
        token,
    ):
        return render(
            request,
            "accounts/email_verification_failed.html",
            {
                "message": (
                    "This verification link is invalid "
                    "or has expired."
                ),
            },
            status=400,
        )

    user.email_verified = True

    user.save(
        update_fields=[
            "email_verified",
        ]
    )

    return render(
        request,
        "accounts/email_verified.html",
    )


# ============================================================
# LOGIN / LOGOUT
# ============================================================

# apps/accounts/views.py - Corrected login_view

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()  # Convert to lowercase
            password = form.cleaned_data["password"]

            # Try to find user by email first
            try:
                user_obj = User.objects.get(email=email)
                if not user_obj.is_active:
                    form.add_error(
                        None,
                        "Your account has been deactivated. Please contact support."
                    )
                    return render(request, "accounts/login.html", {"form": form})
                if not user_obj.email_verified:
                    form.add_error(
                        None,
                        "Please verify your email address before logging in."
                    )
                    return render(request, "accounts/login.html", {"form": form})
            except User.DoesNotExist:
                form.add_error(None, "Invalid email or password.")
                return render(request, "accounts/login.html", {"form": form})

            user = authenticate(
                request,
                email=email,
                password=password,
            )

            if user is None:
                form.add_error(
                    None,
                    "Invalid email or password.",
                )
            else:
                login(request, user)

                # Redirect admins to admin dashboard
                if user.role == User.Role.ADMIN:
                    return redirect("accounts:admin-dashboard")

                # Students go to the main home page
                return redirect("core:home")

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )

@login_required
def logout_view(request):
    """Show logout confirmation page."""
    return render(
        request,
        "accounts/logout_confirm.html"
    )


@login_required
def logout_confirm(request):
    """Confirm logout and log out the user."""
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login")
    return redirect("accounts:logout")


# ============================================================
# USER ACCOUNT
# ============================================================

@login_required
def account(request):
    return render(
        request,
        "accounts/account.html",
        {
            "user": request.user,
        },
    )


@login_required
def profile_edit(request):
    # Get or create profile for the user.
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            user=request.user,
            profile=profile,
        )

        if form.is_valid():
            request.user.full_name = form.cleaned_data[
                "full_name"
            ]

            request.user.save(
                update_fields=[
                    "full_name",
                ]
            )

            profile.phone_number = form.cleaned_data[
                "phone_number"
            ]

            profile_picture = form.cleaned_data.get(
                "profile_picture"
            )

            if profile_picture:
                profile.profile_picture = profile_picture

            profile.save()

            messages.success(
                request,
                (
                    "Your profile has been updated "
                    "successfully!"
                ),
            )

            return redirect(
                "accounts:account"
            )

    else:
        form = ProfileForm(
            user=request.user,
            profile=profile,
        )

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
            "profile": profile,
        },
    )


# ============================================================
# SETTINGS
# ============================================================

@login_required
def settings_view(request):
    """Display the user settings page."""

    return render(
        request,
        "accounts/settings.html",
    )


# ============================================================
# PASSWORD CHANGE
# ============================================================

@login_required
def password_change(request):
    """Change the authenticated user's password."""

    if request.method == "POST":
        form = PasswordChangeForm(
            user=request.user,
            data=request.POST,
        )

        if form.is_valid():
            user = form.save()

            # Keep the user logged in after changing
            # the password.
            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Your password was successfully updated!",
            )

            return redirect(
                "accounts:settings"
            )

        messages.error(
            request,
            "Please correct the errors below.",
        )

    else:
        form = PasswordChangeForm(
            user=request.user,
        )

    return render(
        request,
        "accounts/password_change.html",
        {
            "form": form,
        },
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()

    total_students = User.objects.filter(
        role=User.Role.STUDENT
    ).count()

    total_admins = User.objects.filter(
        role=User.Role.ADMIN
    ).count()

    active_users = User.objects.filter(
        is_active=True
    ).count()

    # Question statistics.
    total_questions = Question.objects.count()

    active_questions = Question.objects.filter(
        is_active=True
    ).count()

    total_subjects = Subject.objects.count()

    total_chapters = Chapter.objects.count()

    total_topics = Topic.objects.count()

    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "total_users": total_users,
            "total_students": total_students,
            "total_admins": total_admins,
            "active_users": active_users,
            "total_questions": total_questions,
            "active_questions": active_questions,
            "total_subjects": total_subjects,
            "total_chapters": total_chapters,
            "total_topics": total_topics,
        },
    )


# ============================================================
# ADMIN USER MANAGEMENT
# ============================================================

@admin_required
def admin_users(request):
    users = User.objects.all().order_by(
        "email"
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    role_filter = request.GET.get(
        "role",
        "",
    ).strip()

    status_filter = request.GET.get(
        "status",
        "",
    ).strip()

    if search_query:
        users = users.filter(
            Q(email__icontains=search_query)
            | Q(full_name__icontains=search_query)
        )

    if role_filter in {
        User.Role.STUDENT,
        User.Role.ADMIN,
    }:
        users = users.filter(
            role=role_filter
        )

    if status_filter == "active":
        users = users.filter(
            is_active=True
        )

    elif status_filter == "inactive":
        users = users.filter(
            is_active=False
        )

    return render(
        request,
        "accounts/admin_users.html",
        {
            "users": users,
            "search_query": search_query,
            "role_filter": role_filter,
            "status_filter": status_filter,
        },
    )


@admin_required
def toggle_user_active(request, user_id):
    if request.method != "POST":
        return redirect(
            "accounts:admin-users"
        )

    user = get_object_or_404(
        User,
        pk=user_id,
    )

    # Prevent an admin from deactivating
    # their own account.
    if user == request.user:
        messages.warning(
            request,
            "You cannot deactivate your own account.",
        )

        return redirect(
            "accounts:admin-users"
        )

    user.is_active = not user.is_active

    user.save(
        update_fields=[
            "is_active",
        ]
    )

    status = (
        "activated"
        if user.is_active
        else "deactivated"
    )

    messages.success(
        request,
        f"User {user.email} has been {status}.",
    )

    return redirect(
        "accounts:admin-users"
    )


# ============================================================
# ADMIN QUESTION MANAGEMENT
# ============================================================

@admin_required
def question_list(request):
    """List all questions with filtering and pagination."""

    questions = Question.objects.select_related(
        "topic__chapter__subject"
    )

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    filter_form = QuestionFilterForm(
        request.GET
    )

    if filter_form.is_valid():
        subject = filter_form.cleaned_data.get(
            "subject"
        )

        chapter = filter_form.cleaned_data.get(
            "chapter"
        )

        topic = filter_form.cleaned_data.get(
            "topic"
        )

        difficulty = filter_form.cleaned_data.get(
            "difficulty"
        )

        search = filter_form.cleaned_data.get(
            "search",
            "",
        ).strip()

        is_active = filter_form.cleaned_data.get(
            "is_active"
        )

        if subject:
            questions = questions.filter(
                topic__chapter__subject=subject
            )

        if chapter:
            questions = questions.filter(
                topic__chapter=chapter
            )

        if topic:
            questions = questions.filter(
                topic=topic
            )

        if difficulty:
            questions = questions.filter(
                difficulty=difficulty
            )

        if search:
            questions = questions.filter(
                Q(question__icontains=search)
                | Q(source__icontains=search)
                | Q(explanation__icontains=search)
            )

        if is_active == "true":
            questions = questions.filter(
                is_active=True
            )

        elif is_active == "false":
            questions = questions.filter(
                is_active=False
            )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    paginator = Paginator(
        questions.order_by("-created_at"),
        20,
    )

    page_number = request.GET.get(
        "page",
        1,
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "page_obj": page_obj,
        "filter_form": filter_form,
        "total_questions": Question.objects.count(),
        "active_questions": Question.objects.filter(
            is_active=True
        ).count(),
        "total_subjects": Subject.objects.count(),
        "total_chapters": Chapter.objects.count(),
        "total_topics": Topic.objects.count(),
    }

    return render(
        request,
        "accounts/admin_question_list.html",
        context,
    )


@admin_required
def question_create(request):
    """Create a new question."""

    if request.method == "POST":
        form = QuestionForm(
            request.POST
        )

        if form.is_valid():
            question = form.save()

            messages.success(
                request,
                (
                    "Question created successfully! "
                    f"(ID: {question.id})"
                ),
            )

            return redirect(
                "accounts:admin-questions"
            )

    else:
        form = QuestionForm()

    context = {
        "form": form,
        "title": "Add New Question",
        "submit_text": "Create Question",
    }

    return render(
        request,
        "accounts/admin_question_form.html",
        context,
    )


@admin_required
def question_edit(request, pk):
    """Edit an existing question."""

    question = get_object_or_404(
        Question,
        pk=pk,
    )

    if request.method == "POST":
        form = QuestionForm(
            request.POST,
            instance=question,
        )

        if form.is_valid():
            question = form.save()

            messages.success(
                request,
                (
                    f"Question {question.id} "
                    "updated successfully!"
                ),
            )

            return redirect(
                "accounts:admin-questions"
            )

    else:
        form = QuestionForm(
            instance=question
        )

    context = {
        "form": form,
        "question": question,
        "title": f"Edit Question #{question.id}",
        "submit_text": "Update Question",
    }

    return render(
        request,
        "accounts/admin_question_form.html",
        context,
    )


@admin_required
def question_delete(request, pk):
    """Delete a question with confirmation."""

    question = get_object_or_404(
        Question,
        pk=pk,
    )

    if request.method == "POST":
        question_id = question.id

        question.delete()

        messages.success(
            request,
            (
                f"Question #{question_id} "
                "deleted successfully!"
            ),
        )

        return redirect(
            "accounts:admin-questions"
        )

    context = {
        "question": question,
    }

    return render(
        request,
        "accounts/admin_question_delete.html",
        context,
    )


# ============================================================
# QUESTION IMPORT
# ============================================================

@admin_required
def question_import(request):
    """Import questions from JSON or CSV."""

    if request.method == "POST":
        form = QuestionImportForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            import_type = form.cleaned_data[
                "import_type"
            ]

            uploaded_file = request.FILES[
                "file"
            ]

            create_missing = form.cleaned_data[
                "create_missing"
            ]

            skip_duplicates = form.cleaned_data[
                "skip_duplicates"
            ]

            # Read uploaded file content.
            file_content = uploaded_file.read().decode(
                "utf-8"
            )

            # Initialize import service.
            service = QuestionImportService(
                create_missing=create_missing,
                skip_duplicates=skip_duplicates,
            )

            # Import according to selected format.
            if import_type == "json":
                stats = service.import_from_json(
                    file_content
                )

            else:
                stats = service.import_from_csv(
                    file_content
                )

            # ------------------------------------------------
            # Import result
            # ------------------------------------------------

            if stats["errors"]:
                messages.warning(
                    request,
                    (
                        "Import completed with "
                        f'{len(stats["errors"])} errors. '
                        f'Created: {stats["created"]}, '
                        f'Updated: {stats["updated"]}, '
                        f'Skipped: {stats["skipped"]}'
                    ),
                )

                # Store detailed errors in session.
                request.session[
                    "import_errors"
                ] = stats["errors"]

            else:
                messages.success(
                    request,
                    (
                        "Import successful! "
                        f'Created: {stats["created"]}, '
                        f'Updated: {stats["updated"]}, '
                        f'Skipped: {stats["skipped"]}'
                    ),
                )

            return redirect(
                "accounts:admin-questions"
            )

    else:
        form = QuestionImportForm()

    context = {
        "form": form,
        "title": "Import Questions",
    }

    return render(
        request,
        "accounts/admin_question_import.html",
        context,
    )


# ============================================================
# AJAX: CHAPTERS BY SUBJECT
# ============================================================

@admin_required
def get_chapters_by_subject(request):
    """Return active chapters for a selected subject."""

    subject_id = request.GET.get(
        "subject_id"
    )

    if subject_id:
        chapters = Chapter.objects.filter(
            subject_id=subject_id,
            is_active=True,
        ).values(
            "id",
            "name",
        )

        return JsonResponse(
            list(chapters),
            safe=False,
        )

    return JsonResponse(
        [],
        safe=False,
    )


# ============================================================
# AJAX: TOPICS BY CHAPTER
# ============================================================

@admin_required
def get_topics_by_chapter(request):
    """Return active topics for a selected chapter."""

    chapter_id = request.GET.get(
        "chapter_id"
    )

    if chapter_id:
        topics = Topic.objects.filter(
            chapter_id=chapter_id,
            is_active=True,
        ).values(
            "id",
            "name",
        )

        return JsonResponse(
            list(topics),
            safe=False,
        )

    return JsonResponse(
        [],
        safe=False,
    )

@admin_required
def admin_dashboard(request):
    from apps.core.models import QuestionReport
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    
    User = get_user_model()
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_users = User.objects.count()
    total_students = User.objects.filter(
        role=User.Role.STUDENT
    ).count()
    total_admins = User.objects.filter(
        role=User.Role.ADMIN
    ).count()
    active_users = User.objects.filter(
        is_active=True
    ).count()
    
    # Daily active users (logged in today)
    daily_active_users = User.objects.filter(
        last_login__gte=today_start
    ).count()
    
    # Question statistics
    total_questions = Question.objects.count()
    active_questions = Question.objects.filter(
        is_active=True
    ).count()
    total_subjects = Subject.objects.count()
    total_chapters = Chapter.objects.count()
    total_topics = Topic.objects.count()
    
    # Question reports - handle if table doesn't exist yet
    try:
        pending_reports = QuestionReport.objects.filter(
            status=QuestionReport.ReportStatus.PENDING
        ).count()
        reviewing_reports = QuestionReport.objects.filter(
            status=QuestionReport.ReportStatus.REVIEWING
        ).count()
        total_reports = QuestionReport.objects.count()
    except Exception:
        pending_reports = 0
        reviewing_reports = 0
        total_reports = 0
    
    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "total_users": total_users,
            "total_students": total_students,
            "total_admins": total_admins,
            "active_users": active_users,
            "daily_active_users": daily_active_users,
            "total_questions": total_questions,
            "active_questions": active_questions,
            "total_subjects": total_subjects,
            "total_chapters": total_chapters,
            "total_topics": total_topics,
            "pending_reports": pending_reports,
            "reviewing_reports": reviewing_reports,
            "total_reports": total_reports,
        },
    )

# ============================================================
# QUESTION REPORTS MANAGEMENT
# ============================================================

@admin_required
def admin_reports(request):
    """View and manage question reports submitted by students."""
    from apps.core.models import QuestionReport
    from django.core.paginator import Paginator
    
    status_filter = request.GET.get('status', 'all')
    
    reports = QuestionReport.objects.select_related(
        'question', 
        'reported_by',
        'resolved_by'
    )
    
    if status_filter != 'all':
        reports = reports.filter(status=status_filter)
    
    # Counts for badges and stats
    total_count = QuestionReport.objects.count()
    pending_count = QuestionReport.objects.filter(status='pending').count()
    reviewing_count = QuestionReport.objects.filter(status='reviewing').count()
    resolved_count = QuestionReport.objects.filter(status='resolved').count()
    rejected_count = QuestionReport.objects.filter(status='rejected').count()
    
    # Pagination
    paginator = Paginator(reports.order_by('-created_at'), 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'status': status_filter,
        'total_count': total_count,
        'pending_count': pending_count,
        'reviewing_count': reviewing_count,
        'resolved_count': resolved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'accounts/admin_reports.html', context)


@admin_required
def admin_update_report(request, report_id):
    """Update report status (resolve, reject, or change status)."""
    from apps.core.models import QuestionReport
    
    if request.method != 'POST':
        return redirect('accounts:admin-reports')
    
    report = get_object_or_404(QuestionReport, id=report_id)
    new_status = request.POST.get('status')
    admin_notes = request.POST.get('admin_notes', '').strip()
    
    if new_status in ['pending', 'reviewing', 'resolved', 'rejected']:
        report.status = new_status
        if admin_notes:
            report.admin_notes = admin_notes
        if new_status in ['resolved', 'rejected']:
            report.resolved_by = request.user
        report.save()
        
        status_display = report.get_status_display()
        messages.success(
            request, 
            f'Report #{report_id} updated to {status_display}'
        )
    else:
        messages.error(request, 'Invalid status value.')
    
    return redirect('accounts:admin-reports')


@admin_required
def admin_report_detail(request, report_id):
    """View a single report in detail."""
    from apps.core.models import QuestionReport
    
    report = get_object_or_404(
        QuestionReport, 
        id=report_id
    )
    
    if request.method == 'POST':
        # Update status from detail page
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '').strip()
        
        if new_status in ['pending', 'reviewing', 'resolved', 'rejected']:
            report.status = new_status
            if admin_notes:
                report.admin_notes = admin_notes
            if new_status in ['resolved', 'rejected']:
                report.resolved_by = request.user
            report.save()
            messages.success(
                request, 
                f'Report updated to {report.get_status_display()}'
            )
            return redirect('accounts:admin-report-detail', report_id=report_id)
    
    context = {
        'report': report,
    }
    return render(request, 'accounts/admin_report_detail.html', context)

# apps/accounts/views.py - Add these functions

# ============================================================
# NOTIFICATIONS
# ============================================================

@login_required
def notifications_view(request):
    """View all notifications for the logged-in user."""
    from apps.core.models import Notification
    
    # Get filter parameter
    filter_type = request.GET.get('filter', 'all')  # 'all' or 'unread'
    
    notifications = Notification.objects.filter(user=request.user)
    
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    
    # Counts for badges
    unread_count = notifications.filter(is_read=False).count()
    total_count = Notification.objects.filter(user=request.user).count()
    
    context = {
        'notifications': notifications.order_by('-created_at'),
        'unread_count': unread_count,
        'total_count': total_count,
        'filter_type': filter_type,
    }
    
    return render(request, 'accounts/notifications.html', context)


@login_required
def notification_mark_read(request, notification_id):
    """Mark a specific notification as read."""
    from apps.core.models import Notification
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        # If this was an AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        # Otherwise redirect back
        next_url = request.GET.get('next', 'accounts:notifications')
        return redirect(next_url)
        
    except Notification.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
        return redirect('accounts:notifications')


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read for the logged-in user."""
    from apps.core.models import Notification
    from apps.core.services.notification_service import NotificationService
    
    if request.method == 'POST':
        count = NotificationService.mark_all_as_read(request.user)
        messages.success(request, f'Marked {count} notifications as read.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'count': count})
        
        return redirect('accounts:notifications')
    
    return redirect('accounts:notifications')


@login_required
def notification_click(request, notification_id):
    """Handle notification click - mark as clicked and redirect."""
    from apps.core.models import Notification
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        notification.mark_as_clicked()
        
        # Redirect to the notification's link
        if notification.link:
            return redirect(notification.link)
        
    except Notification.DoesNotExist:
        pass
    
    return redirect('accounts:notifications')


@login_required
def notification_unread_count(request):
    """API endpoint to get unread notification count."""
    from apps.core.models import Notification
    
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})

# ============================================================
# ADMIN SUBJECT MANAGEMENT (CRUD)
# ============================================================

@admin_required
def admin_subjects(request):
    """Manage subjects."""
    subjects = Subject.objects.filter(is_active=True).order_by('name')
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'accounts/admin_subjects.html', context)


@admin_required
def admin_subject_create(request):
    """Create a new subject."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            subject = Subject.objects.create(
                name=name,
                description=description,
                is_active=True
            )
            messages.success(request, f'Subject "{subject.name}" created successfully!')
            return redirect('accounts:admin-subjects')
        else:
            messages.error(request, 'Subject name is required.')
    
    return render(request, 'accounts/admin_subject_form.html', {'title': 'Add Subject'})


@admin_required
def admin_subject_edit(request, subject_id):
    """Edit a subject."""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            subject.name = name
            subject.description = description
            subject.is_active = is_active
            subject.save()
            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('accounts:admin-subjects')
        else:
            messages.error(request, 'Subject name is required.')
    
    return render(request, 'accounts/admin_subject_form.html', {
        'subject': subject,
        'title': 'Edit Subject'
    })


@admin_required
def admin_subject_delete(request, subject_id):
    """Delete a subject."""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" deleted successfully!')
        return redirect('accounts:admin-subjects')
    
    return render(request, 'accounts/admin_subject_delete.html', {'subject': subject})


# ============================================================
# ADMIN CHAPTER MANAGEMENT (CRUD)
# ============================================================

@admin_required
def admin_chapters(request, subject_id):
    """Manage chapters for a subject."""
    subject = get_object_or_404(Subject, id=subject_id)
    chapters = subject.chapters.filter(is_active=True).order_by('unit_number', 'name')
    
    context = {
        'subject': subject,
        'chapters': chapters,
    }
    return render(request, 'accounts/admin_chapters.html', context)


@admin_required
def admin_chapter_create(request, subject_id):
    """Create a new chapter."""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        unit_number = request.POST.get('unit_number', 0)
        description = request.POST.get('description', '').strip()
        
        if name:
            chapter = Chapter.objects.create(
                subject=subject,
                name=name,
                unit_number=unit_number,
                description=description,
                is_active=True
            )
            messages.success(request, f'Chapter "{chapter.name}" created successfully!')
            return redirect('accounts:admin-chapters', subject_id=subject.id)
        else:
            messages.error(request, 'Chapter name is required.')
    
    return render(request, 'accounts/admin_chapter_form.html', {
        'subject': subject,
        'title': 'Add Chapter'
    })


@admin_required
def admin_chapter_edit(request, subject_id, chapter_id):
    """Edit a chapter."""
    subject = get_object_or_404(Subject, id=subject_id)
    chapter = get_object_or_404(Chapter, id=chapter_id, subject=subject)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        unit_number = request.POST.get('unit_number', 0)
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            chapter.name = name
            chapter.unit_number = unit_number
            chapter.description = description
            chapter.is_active = is_active
            chapter.save()
            messages.success(request, f'Chapter "{chapter.name}" updated successfully!')
            return redirect('accounts:admin-chapters', subject_id=subject.id)
        else:
            messages.error(request, 'Chapter name is required.')
    
    return render(request, 'accounts/admin_chapter_form.html', {
        'subject': subject,
        'chapter': chapter,
        'title': 'Edit Chapter'
    })


@admin_required
def admin_chapter_delete(request, subject_id, chapter_id):
    """Delete a chapter."""
    subject = get_object_or_404(Subject, id=subject_id)
    chapter = get_object_or_404(Chapter, id=chapter_id, subject=subject)
    
    if request.method == 'POST':
        chapter_name = chapter.name
        chapter.delete()
        messages.success(request, f'Chapter "{chapter_name}" deleted successfully!')
        return redirect('accounts:admin-chapters', subject_id=subject.id)
    
    return render(request, 'accounts/admin_chapter_delete.html', {
        'subject': subject,
        'chapter': chapter
    })

@login_required
def account(request):
    """User account page with practice stats."""
    from apps.practice.models import PracticeSession, PracticeAttempt
    
    # Get practice stats
    sessions = PracticeSession.objects.filter(user=request.user)
    total_practice_sessions = sessions.count()
    
    attempts = PracticeAttempt.objects.filter(session__user=request.user)
    total_questions_answered = attempts.count()
    correct_answers = attempts.filter(is_correct=True).count()
    
    accuracy = round((correct_answers / total_questions_answered) * 100, 1) if total_questions_answered > 0 else 0
    
    return render(
        request,
        "accounts/account.html",
        {
            "user": request.user,
            "total_practice_sessions": total_practice_sessions,
            "total_questions_answered": total_questions_answered,
            "accuracy": accuracy,
        },
    )
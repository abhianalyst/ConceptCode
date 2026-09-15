from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    # =========================================================
    # AUTHENTICATION
    # =========================================================

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    # Show logout confirmation page
    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # Actually log the user out
    path(
        "logout/confirm/",
        views.logout_confirm,
        name="logout-confirm",
    ),

    # =========================================================
    # EMAIL VERIFICATION
    # =========================================================

    path(
        "verify-email/<int:user_id>/<str:token>/",
        views.verify_email,
        name="verify-email",
    ),

    path(
        "verification-pending/",
        views.verification_pending,
        name="verification-pending",
    ),

    # =========================================================
    # USER ACCOUNT
    # =========================================================

    path(
        "account/",
        views.account,
        name="account",
    ),

    path(
        "profile/edit/",
        views.profile_edit,
        name="profile-edit",
    ),

    # =========================================================
    # ACCOUNT SETTINGS & SECURITY
    # =========================================================

    path(
        "settings/",
        views.settings_view,
        name="settings",
    ),

    path(
        "password-change/",
        views.password_change,
        name="password_change",
    ),

    # =========================================================
    # ADMIN DASHBOARD
    # =========================================================

    path(
        "admin/dashboard/",
        views.admin_dashboard,
        name="admin-dashboard",
    ),

    # =========================================================
    # ADMIN USER MANAGEMENT
    # =========================================================

    path(
        "admin/users/",
        views.admin_users,
        name="admin-users",
    ),

    path(
        "admin/users/<int:user_id>/toggle-active/",
        views.toggle_user_active,
        name="admin-toggle-user-active",
    ),

    # =========================================================
    # ADMIN QUESTION MANAGEMENT
    # =========================================================

    # Question list
    path(
        "admin/questions/",
        views.question_list,
        name="admin-questions",
    ),

    # Add question manually
    path(
        "admin/questions/create/",
        views.question_create,
        name="admin-question-create",
    ),

    # Edit question
    path(
        "admin/questions/<int:pk>/edit/",
        views.question_edit,
        name="admin-question-edit",
    ),

    # Delete question
    path(
        "admin/questions/<int:pk>/delete/",
        views.question_delete,
        name="admin-question-delete",
    ),

    # Import JSON / CSV
    path(
        "admin/questions/import/",
        views.question_import,
        name="admin-question-import",
    ),

    path(
        'admin/reports/',
        views.admin_reports,
        name='admin-reports'
    ),

    path('admin/reports/<int:report_id>/update/',
         views.admin_update_report, name='admin-update-report'
    ),

    # =========================================================
    # AJAX / API ENDPOINTS
    # =========================================================

    # Get chapters for selected subject
    path(
        "api/chapters/",
        views.get_chapters_by_subject,
        name="api-chapters",
    ),

    # Get topics for selected chapter
    path(
        "api/topics/",
        views.get_topics_by_chapter,
        name="api-topics",
    ),

    # =========================================================
    # NOTIFICATIONS
    # =========================================================

    path(
        'notifications/',
        views.notifications_view,
        name='notifications'
    ),

    path(
        'notifications/<int:notification_id>/read/', 
        views.notification_mark_read, name='notification-mark-read'
    ),

    path(
        'notifications/mark-all-read/', 
        views.notification_mark_all_read, 
        name='notification-mark-all-read'
    ),

    path(
        'notifications/<int:notification_id>/click/', 
        views.notification_click, 
        name='notification-click'
    ),

    path(
        'api/notifications/unread-count/', 
        views.notification_unread_count, 
        name='notification-unread-count'
    ),

    # =========================================================
    # PASSWORD RESET
    # =========================================================

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),

    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
        'export-data/', 
        views.export_data, 
        name='export-data'
    ),
]
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

urlpatterns = [

    # Viewer page (same interface)
    path(
        "secure-document/<int:doc_id>/",
        views.secure_document_view,
        name="secure_document_view"
    ),

    # Stream PDF
    path(
        "secure-document/<int:doc_id>/file/",
        views.stream_document,
        name="stream_document"
    ),

    # Log close
    path(
        "log-close/<int:doc_id>/",
        views.log_document_close,
        name="log_document_close",
    ),

    # ================= PASSWORD CHANGE (FIXED) =================
    path(
        "change-password/",
        login_required(
            auth_views.PasswordChangeView.as_view(
                template_name="admin/password_change_form.html"
            )
        ),
        name="change_password",
    ),

    path(
        "change-password-done/",
        login_required(
            auth_views.PasswordChangeDoneView.as_view(
                template_name="admin/password_change_done.html"
            )
        ),
        name="password_change_done",
    ),

    # ================= DOCUMENT DETAIL =================
    path(
        "detail/<int:doc_id>/",
        views.document_detail,
        name="document_detail"
    ),

    path('logout/', LogoutView.as_view(), name='logout'),
]
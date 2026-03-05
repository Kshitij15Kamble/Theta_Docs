from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    # Viewer page (same interface)
    path(
        "secure-document/<int:doc_id>/",
        views.secure_document_view,
        name="secure_document_view"
    ),

    # Stream PDF (new lightweight endpoint)
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

    # Change password
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="documents/change_password.html"
        ),
        name="change_password",
    ),

    path(
        "change-password-done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="documents/change_password_done.html"
        ),
        name="password_change_done",
    ),

    path('logout/', LogoutView.as_view(), name='logout'),
]
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
urlpatterns = [

    # Dashboard
    path('', views.role_redirect, name='role_redirect'),
    path('role-redirect/', views.role_redirect, name='role_redirect'),
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Document viewer page
    path(
        "secure-document/<int:doc_id>/",
        views.secure_document_view,
        name="secure_document_view"
    ),

    path(
        "log-close/<int:doc_id>/",
        views.log_document_close,
        name="log_document_close",),


    # Lazy image loader API
    path(
        "secure-document/<int:doc_id>/page/<int:page_no>/",
        views.secure_document_page,
        name="secure_document_page"
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
]
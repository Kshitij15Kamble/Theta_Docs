from django.urls import path
from . import views

urlpatterns = [
    path(
        "secure-document/<int:doc_id>/",
        views.secure_document_view,
        name="secure_document_view"
    ),
      path('secure-document/<int:doc_id>/page/<int:page_no>/', views.secure_document_page, name='secure_document_page'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]

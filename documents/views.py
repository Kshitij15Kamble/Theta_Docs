from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import CompanyDocument
from .forms import UsernameEmailPasswordResetForm


# ================= VIEWER PAGE (UNCHANGED INTERFACE) =================
@login_required
def secure_document_view(request, doc_id):
    doc = get_object_or_404(CompanyDocument, id=doc_id)
    user = request.user

    allowed = (
        user.is_superuser
        or user.is_staff
        or user in doc.accessible_by.all()
        or user.groups.filter(id__in=doc.accessible_groups.all()).exists()
    )

    if not allowed:
        return render(request, "documents/access_denied.html")

    # Log open
    LogEntry.objects.create(
        user_id=user.id,
        content_type=ContentType.objects.get_for_model(doc),
        object_id=doc.id,
        object_repr=force_str(doc.title),
        action_flag=CHANGE,
        change_message="Opened Document"
    )

    return render(request, "documents/viewer.html", {
        "doc_id": doc.id
    })


# ================= STREAM PDF (NO CONVERSION) =================
@login_required
def stream_document(request, doc_id):
    doc = get_object_or_404(CompanyDocument, id=doc_id)
    user = request.user

    allowed = (
        user.is_superuser
        or user.is_staff
        or user in doc.accessible_by.all()
        or user.groups.filter(id__in=doc.accessible_groups.all()).exists()
    )

    if not allowed:
        return HttpResponseForbidden("Access denied")

    file = open(doc.file.path, "rb")
    response = FileResponse(file, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{doc.file.name}"'
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response


# ================= LOG CLOSE =================
@login_required
@csrf_exempt
def log_document_close(request, doc_id):
    doc = get_object_or_404(CompanyDocument, id=doc_id)
    user = request.user

    LogEntry.objects.create(
        user_id=user.id,
        content_type=ContentType.objects.get_for_model(doc),
        object_id=doc.id,
        object_repr=force_str(doc.title),
        action_flag=CHANGE,
        change_message="Closed Document"
    )

    return JsonResponse({"status": "ok"})

@ensure_csrf_cookie
def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/admin/documents/companydocument/")
        else:
            return render(request, "documents/login.html", {"error": "Invalid username or password"})

    return render(request, "documents/login.html")


# ================= PASSWORD RESET =================
class SecurePasswordResetView(FormView):
    template_name = "documents/password_reset.html"
    form_class = UsernameEmailPasswordResetForm
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)
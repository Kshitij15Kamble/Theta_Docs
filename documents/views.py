from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import CompanyDocument
from .utils import convert_any_to_images
from .forms import UsernameEmailPasswordResetForm

import base64
from io import BytesIO      
from PIL import Image, ImageDraw          


@login_required
def dashboard(request):
    user = request.user

    if user.is_superuser or user.is_staff:
        documents = CompanyDocument.objects.all()
    else:
        documents = CompanyDocument.objects.filter(
            Q(accessible_by=user) |
            Q(accessible_groups__in=user.groups.all())
        ).distinct()

    return render(request, "documents/dashboard.html", {
        "documents": documents
    })

@login_required
def secure_document_page(request, doc_id, page_no):
    doc = get_object_or_404(CompanyDocument, id=doc_id)
    user = request.user

    user_allowed = user in doc.accessible_by.all()
    group_allowed = user.groups.filter(id__in=doc.accessible_groups.all()).exists()
    admin_allowed = user.is_staff or user.is_superuser

    if not (user_allowed or group_allowed or admin_allowed):
        return JsonResponse({"error": "Access denied"}, status=403)

    image_paths = convert_any_to_images(doc.file.path, doc.id)
    print("DEBUG images:", image_paths)
    total_pages = len(image_paths)

    if page_no < 1 or page_no > total_pages:
        return JsonResponse({"end": True}, status=404)

    img_path = image_paths[page_no - 1]

    img = Image.open(img_path)
    draw = ImageDraw.Draw(img) 
    text = "Theta_Learming"
    draw.text((20, 20), text, fill=(255, 0, 0))
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({
        "image": encoded,
        "page": page_no,
        "total_pages": total_pages
    })

@login_required
def secure_document_view(request, doc_id):
    doc = get_object_or_404(CompanyDocument, id=doc_id)
    user = request.user

    user_allowed = user in doc.accessible_by.all()
    group_allowed = user.groups.filter(
        id__in=doc.accessible_groups.all()
    ).exists()
    admin_allowed = user.is_staff or user.is_superuser

    if not (user_allowed or group_allowed or admin_allowed):
        return render(request, "documents/access_denied.html")

    image_paths = convert_any_to_images(doc.file.path, doc.id)

    pages = []
    for img_path in image_paths:
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            pages.append(encoded)

    return render(request, "documents/viewer.html", {"doc_id": doc.id })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "documents/login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "documents/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


class SecurePasswordResetView(FormView):
    template_name = "documents/password_reset.html"
    form_class = UsernameEmailPasswordResetForm
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

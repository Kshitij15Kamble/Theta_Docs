from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from .models import CompanyDocument
from .utils import convert_any_to_images
from .forms import UsernameEmailPasswordResetForm
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
import base64
from io import BytesIO
from PIL import Image, ImageDraw


@login_required
def role_redirect(request):
    user = request.user

    if user.is_superuser:
        return redirect('/admin/')   # Superadmin → full admin

    if user.is_staff:
        return redirect('/admin/')   # Staff/Admin → admin panel

    return redirect('/dashboard/')   # Normal user → custom dashboard

# ===================== DASHBOARD =====================
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


# ===================== VIEWER PAGE =====================
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

    # 🔥 LOG OPEN EVENT (REAL TIME)
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

@login_required
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


# ===================== IMAGE API (Watermarked) =====================
@login_required
def secure_document_page(request, doc_id, page_no):
    doc = get_object_or_404(CompanyDocument, id=doc_id)
    user = request.user

    allowed = (
        user.is_superuser
        or user.is_staff
        or user in doc.accessible_by.all()
        or user.groups.filter(id__in=doc.accessible_groups.all()).exists()
    )

    if not allowed:
        return JsonResponse({"error": "Access denied"}, status=403)

    image_paths = convert_any_to_images(doc.file.path, doc.id)

    if page_no < 1 or page_no > len(image_paths):
        return JsonResponse({"end": True}, status=404)

    img = Image.open(image_paths[page_no - 1]).convert("RGBA")

    # Watermark
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    watermark_text = f"{user.username} - Confidential"

    width, height = img.size
    draw.text(
        (width // 4, height // 2),
        watermark_text,
        fill=(255, 0, 0, 100)
    )

    final = Image.alpha_composite(img, overlay)

    buffer = BytesIO()
    final.convert("RGB").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({
        "image": encoded
    })

# ===================== PASSWORD RESET =====================
class SecurePasswordResetView(FormView):
    template_name = "documents/password_reset.html"
    form_class = UsernameEmailPasswordResetForm
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import CompanyDocument
from .forms import AdminUserCreationForm
from .utils import generate_secure_password, send_user_credentials_email


# ===============================
# Company Document Admin
# ===============================
class CompanyDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author",
        "publication_year",
        "publication_type",
        "created_at",
        "view_button",
        "edit_button",
    )
    list_display_links = None
    list_filter = ("publication_type",)
    search_fields = ("title", "author", "publication_year")
    # VIEW BUTTON
    def view_button(self, obj):
        url = reverse("document_detail", args=[obj.id])
        return format_html(
        '<div class="action-buttons"><a class="button view-btn" href="{}">View</a></div>',
        url
    )

    def edit_button(self, obj):
        url = reverse("admin:documents_companydocument_change", args=[obj.id])
        return format_html(
            '<div class="action-buttons"><a class="button edit-btn" href="{}">Edit</a></div>',
        url
    )


# ===============================
# Redirect Admin Dashboard
# ===============================
def custom_admin_index(request):
    return HttpResponseRedirect("/admin/documents/companydocument/")


admin.site.index = custom_admin_index


# ===============================
# Custom User Admin
# ===============================
class CustomUserAdmin(UserAdmin):

    model = User
    add_form = AdminUserCreationForm
    readonly_fields = ("last_login", "date_joined")

    list_display = (
        "username",
        "email",
        "edit_button",
        "activity_button",
    )

    list_display_links = None
    list_filter = ()

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "first_name", "last_name", "email"),
        }),
    )

    # ---------------- EDIT BUTTON ----------------
    def edit_button(self, obj):

        request = getattr(self, "_request", None)

        if request and request.user.has_perm("auth.change_user"):
            url = reverse("admin:auth_user_change", args=[obj.id])
            return format_html('<a class="button" href="{}">Edit</a>', url)

        return "-"

    # ---------------- ACTIVITY BUTTON ----------------
    def activity_button(self, obj):
        url = reverse("admin:admin_logentry_changelist") + f"?user__id__exact={obj.id}"
        return format_html('<a class="button" href="{}">Activity</a>', url)

    activity_button.short_description = "Activity"

    # ---------------- ADD FORM ----------------
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        self._request = request
        return super().get_queryset(request)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm("auth.change_user"):
            return True
        return False

    # ---------------- SECURITY FIELD CONTROL ----------------
    def get_fieldsets(self, request, obj=None):

        fieldsets = super().get_fieldsets(request, obj)

        if not request.user.is_superuser:

            cleaned = []

            for name, options in fieldsets:

                options = options.copy()
                fields = list(options.get("fields", []))

                for f in ("is_staff", "is_superuser", "user_permissions"):
                    if f in fields:
                        fields.remove(f)

                options["fields"] = tuple(fields)
                cleaned.append((name, options))

            return cleaned

        return fieldsets

    # ---------------- PASSWORD AUTO GENERATE ----------------
    def save_model(self, request, obj, form, change):

        is_new_user = obj.pk is None

        if is_new_user:
            password = generate_secure_password()

            obj.set_password(password)

            # Make user staff
            obj.is_staff = True

        super().save_model(request, obj, form, change)

        if is_new_user:

            send_user_credentials_email(
                username=obj.username,
                password=password,
                email=obj.email
            )

            view_permission = Permission.objects.get(
                codename="view_companydocument"
            )

            obj.user_permissions.add(view_permission)

    # ---------------- RESTRICT PERMISSIONS ----------------
    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == "user_permissions" and not request.user.is_superuser:

            kwargs["queryset"] = Permission.objects.filter(
                codename="view_companydocument"
            )

        return super().formfield_for_manytomany(db_field, request, **kwargs)


# ===============================
# Custom Group Admin
# ===============================
class CustomGroupAdmin(GroupAdmin):

    list_filter = ()
    actions = None

    list_display = (
        "name",
        "edit_button",
    )

    list_display_links = None

    def edit_button(self, obj):
        url = reverse("admin:auth_group_change", args=[obj.id])
        return format_html('<a class="button" href="{}">Edit</a>', url)

    edit_button.short_description = "Edit"


# ===============================
# Log Entry Admin (User Activity)
# ===============================
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "content_type",
        "object_repr",
        "action_flag",
        "action_time",
    )

    list_filter = ("user",)


# ===============================
# Register Everything
# ===============================
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
admin.site.register(CompanyDocument, CompanyDocumentAdmin)


# ===============================
# Admin Branding
# ===============================
admin.site.site_header = "Theta Docs Admin"
admin.site.site_title = "Theta Docs Admin"
admin.site.index_title = "Theta Docs Management"
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

    list_display_links = None
    list_filter = ("publication_type",)
    search_fields = ("title", "author", "publication_year")

    def get_list_display(self, request):
        base = [
            "title",
            "author",
            "publication_year",
            "publication_type",
            "created_at",
            "view_button",
        ]

        if request.user.has_perm("documents.change_companydocument"):
            base.append("edit_button")

        return base

    def get_queryset(self, request):
        self._request = request
        return super().get_queryset(request)

    def view_button(self, obj):
        url = reverse("document_detail", args=[obj.id])
        return format_html(
            '<div class="action-buttons">'
            '<a class="button view-btn" href="{}">View</a>'
            '</div>',
            url
        )
    view_button.short_description = "View"

    def edit_button(self, obj):
        request = getattr(self, "_request", None)

        if request and request.user.has_perm("documents.change_companydocument"):
            url = reverse("admin:documents_companydocument_change", args=[obj.id])
            return format_html(
                '<div class="action-buttons">'
                '<a class="button edit-btn" href="{}">Edit</a>'
                '</div>',
                url
            )
        return "-"
    edit_button.short_description = "Edit"

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("documents.change_companydocument")

    # ===============================
    # 🔥 FILE DELETE FIX (ADD THIS)
    # ===============================

    # Bulk delete
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.file:
                obj.file.delete(save=False)
        queryset.delete()

    # Single delete
    def delete_model(self, request, obj):
        if obj.file:
            obj.file.delete(save=False)
        super().delete_model(request, obj)

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

    # ✅ removed password_display
    readonly_fields = ("last_login", "date_joined")
    list_display_links = None
    list_filter = ()

    # ---------------- DYNAMIC COLUMN CONTROL ----------------
    def get_list_display(self, request):
        columns = [
            "username",
            "email",
            "activity_button",
        ]

        if request.user.has_perm("auth.change_user"):
            columns.insert(2, "edit_button")

        return columns

    # ---------------- EDIT BUTTON ----------------
    def edit_button(self, obj):
        request = getattr(self, "_request", None)

        if request and request.user.has_perm("auth.change_user"):
            url = reverse("admin:auth_user_change", args=[obj.id])
            return format_html('<a class="button" href="{}">Edit</a>', url)

        return "-"
    edit_button.short_description = "Edit"

    # ---------------- ACTIVITY BUTTON ----------------
    def activity_button(self, obj):
        url = reverse("admin:admin_logentry_changelist") + f"?user__id__exact={obj.id}"
        return format_html('<a class="button" href="{}">Activity</a>', url)
    activity_button.short_description = "Activity"

    # ---------------- ADD FORM ----------------
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "first_name", "last_name", "email"),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form

        form = super().get_form(request, obj, **kwargs)

        # 🔥 REMOVE USERNAME HELP TEXT
        if 'username' in form.base_fields:
            form.base_fields['username'].help_text = ""

        return form

    def get_queryset(self, request):
        self._request = request
        return super().get_queryset(request)

    # ---------------- PERMISSION CONTROL ----------------
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("auth.change_user")

    # ================= FIELD SECURITY =================
    def get_fieldsets(self, request, obj=None):

        fieldsets = super().get_fieldsets(request, obj)

        # 🔥 If NO permission → REMOVE password completely
        if not request.user.has_perm("auth.change_user"):

            cleaned = []

            for name, options in fieldsets:

                options = options.copy()
                fields = list(options.get("fields", []))

                # ❌ REMOVE password field
                fields = [f for f in fields if f != "password"]

                # ❌ REMOVE sensitive fields
                fields = [
                    f for f in fields
                    if f not in ("is_staff", "is_superuser", "user_permissions")
                ]

                options["fields"] = tuple(fields)
                cleaned.append((name, options))

            return cleaned

        return fieldsets

    # ---------------- PASSWORD AUTO GENERATION ----------------
    def save_model(self, request, obj, form, change):

        is_new_user = obj.pk is None

        if is_new_user:
            password = generate_secure_password()
            obj.set_password(password)
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

    # ---------------- PERMISSION FILTER ----------------
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
# Log Entry Admin
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

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    actions = ["delete_selected_logs"]

    def delete_selected_logs(self, request, queryset):
        queryset.delete()

    delete_selected_logs.short_description = "Delete selected log entries"

    def log_deletion(self, request, obj, object_repr):
        pass


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
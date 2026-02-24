from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import CompanyDocument
from .forms import AdminUserCreationForm
from .utils import generate_secure_password, send_user_credentials_email
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse


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
    search_fields = ("title", "author")
    ordering = ("-created_at",)

    # VIEW BUTTON
    def view_button(self, obj):
        url = reverse("secure_document_view", args=[obj.id])
        return format_html(
            '<a class="button" target="_blank" href="{}">View</a>',
            url
        )

    view_button.short_description = "View"

    # EDIT BUTTON
    def edit_button(self, obj):
        url = reverse("admin:documents_companydocument_change", args=[obj.id])
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            url
        )

    edit_button.short_description = "Edit"





def custom_admin_index(request):
    return HttpResponseRedirect("/admin/documents/companydocument/")

admin.site.index = custom_admin_index
# ===============================
# Custom User Admin
# ===============================
class CustomUserAdmin(UserAdmin):
    model = User
    add_form = AdminUserCreationForm
    readonly_fields = ('last_login', 'date_joined')

    # ✅ NEW: Custom list display
    list_display = (
        "username",
        "email",
        "edit_button",
        "activity_button",
    )

    # ❌ Remove clickable username
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
        url = reverse("admin:auth_user_change", args=[obj.id])
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            url
        )
    edit_button.short_description = "Edit"

    # ---------------- ACTIVITY BUTTON ----------------
    def activity_button(self, obj):
        url = reverse("admin:admin_logentry_changelist") + f"?user__id__exact={obj.id}"
        return format_html(
            '<a class="button" href="{}">Activity</a>',
            url
        )
    activity_button.short_description = "Activity"

    # ---------------- ADD FORM ----------------
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)

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

        super().save_model(request, obj, form, change)

        if is_new_user:
            send_user_credentials_email(
                username=obj.username,
                password=password,
                email=obj.email
            )

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

    # Remove filters
    list_filter = ()

    # Remove bulk actions
    actions = None

    # Custom columns
    list_display = (
        "name",
        "edit_button",
    )

    # Make name NOT clickable
    list_display_links = None
    # Edit button
    def edit_button(self, obj): 
        url = reverse("admin:auth_group_change", args=[obj.id])
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            url
        )
# ===============================
# Log Entry Admin (User Activity)
# ===============================
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_repr', 'action_flag', 'action_time')
    list_filter = ('user',)


# ===============================
# Register Everything
# ===============================
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
admin.site.register(CompanyDocument, CompanyDocumentAdmin)

admin.site.site_header = "Theta Docs Admin"
admin.site.site_title = "Theta Docs Admin"
admin.site.index_title = "Theta Docs Management"
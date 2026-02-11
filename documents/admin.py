from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.conf import settings
from .models import CompanyDocument
from .forms import AdminUserCreationForm
from .utils import generate_secure_password, send_user_credentials_email


# -------------------------
# Company Document Admin
# -------------------------
class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "file_type", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at",)


# -------------------------
# Custom User Admin
# -------------------------
class CustomUserAdmin(UserAdmin):
    model = User
    add_form = AdminUserCreationForm

    # Fields shown while ADDING a user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "first_name", "last_name", "email"),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Force custom form ONLY while adding a user
        """
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        """
        Hide dangerous fields from Admin (not Main_Admin)
        """
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

    def save_model(self, request, obj, form, change):
        """
        Auto-generate password + email credentials on user creation
        """
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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Restrict permissions Admin can assign
        """
        if (
            db_field.name == "user_permissions"
            and not request.user.is_superuser
        ):
            kwargs["queryset"] = Permission.objects.filter(
                codename="view_companydocument"
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -------------------------
# Custom Group Admin
# -------------------------
class CustomGroupAdmin(GroupAdmin):

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Restrict permissions Admin can assign to groups
        """
        if (
            db_field.name == "permissions"
            and not request.user.is_superuser
        ):
            kwargs["queryset"] = Permission.objects.filter(
                codename="view_companydocument"
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -------------------------
# Register Admins
# -------------------------
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
admin.site.register(CompanyDocument, CompanyDocumentAdmin)

admin.site.site_header = "Theta Docs Admin"
admin.site.site_title = "Theta Docs Admin"
admin.site.index_title = "Theta Docs Management"



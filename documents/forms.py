from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class UsernameEmailPasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

    def save(self, request):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            # 🔒 Security: do nothing (no leak)
            return

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(
            f"/reset/{uid}/{token}/"
        )

        send_mail(
            subject="Password Reset – Secure Docs",
            message=f"""
Hello {user.username},

You requested a password reset.

Reset your password using the link below:
{reset_link}

If you did not request this, ignore this email.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class AdminUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")







        
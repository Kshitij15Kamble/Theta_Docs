from django.apps import AppConfig


class DocumentsConfig(AppConfig):
   
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documents'

    def ready(self):
        from django.contrib.auth.models import User

        username = "Main_admin"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email="admin@example.com",
                password="Admin@123"
            )
from django.db import models
from django.contrib.auth.models import User, Group

class CompanyDocument(models.Model):

    FILE_TYPES = [
        ('PDF', 'PDF'),
        ('DOC', 'DOC'),
        ('DOCX', 'DOCX'),
        ('IMAGE', 'IMAGE'),
        ('NEWS', 'NEWS'),
    ]

    title = models.CharField(max_length=200)

    file = models.FileField(upload_to='protected/')

    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPES
    )

    accessible_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="documents",
        help_text="Users who can view this document"
    )

    accessible_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="group_documents",
        help_text="Groups who can view this document"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

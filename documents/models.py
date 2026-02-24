from django.db import models
from django.contrib.auth.models import User, Group

class CompanyDocument(models.Model):
    PUBLICATION_TYPES = [
        ('Magazine', 'Magazine'),
        ('Book', 'Book'),
        ('Article', 'Article'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publication_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='protected/')

    accessible_by = models.ManyToManyField(User, blank=True)
    accessible_groups = models.ManyToManyField(Group, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

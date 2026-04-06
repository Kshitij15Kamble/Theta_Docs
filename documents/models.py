from django.db import models
from django.contrib.auth.models import User, Group
import re

# Words that must always stay uppercase
UPPER_WORDS = {"AI", "ML", "API", "PDF", "IoT", "NLP"}


def smart_format_text(text):
    if not text:
        return text

    text = text.strip()
    text = text.title()

    for word in UPPER_WORDS:
        text = re.sub(rf"\b{word.title()}\b", word, text)

    return text


def format_author_name(name):
    if not name:
        return name

    name = name.strip()
    return " ".join(part.capitalize() for part in name.split())


class CompanyDocument(models.Model):
    PUBLICATION_TYPES = [
        ('Magazine', 'Magazine'),
        ('Book', 'Book'),
        ('Article', 'Article'),
    ]

    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publication_type = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='protected/')
    cover_image = models.ImageField(
        upload_to="covers/",
        blank=True,
        null=True
    )

    accessible_by = models.ManyToManyField(User, blank=True)
    accessible_groups = models.ManyToManyField(Group, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    # ================= SAVE (UPDATED) =================
    def save(self, *args, **kwargs):

        # 🔥 DELETE OLD FILE IF REPLACED
        try:
            old = CompanyDocument.objects.get(pk=self.pk)
            if old.file and old.file != self.file:
                old.file.delete(save=False)
        except CompanyDocument.DoesNotExist:
            pass

        # Format fields
        if self.title:
            self.title = smart_format_text(self.title)

        if self.author:
            self.author = format_author_name(self.author)

        if self.publication_type:
            self.publication_type = smart_format_text(self.publication_type)

        # ❌ removed string conversion of publication_year (keep as int)

        super().save(*args, **kwargs)

    # ================= DELETE (NEW) =================
    def delete(self, *args, **kwargs):

        # 🔥 DELETE FILE FROM STORAGE
        if self.file:
            self.file.delete(save=False)

        super().delete(*args, **kwargs)
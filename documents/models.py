from django.db import models
from django.contrib.auth.models import User, Group
import re

# Words that must always stay uppercase
UPPER_WORDS = {"AI", "ML", "API", "PDF", "IoT", "NLP"}

def smart_format_text(text):
    if not text:
        return text

    text = text.strip()

    # Convert to title case
    text = text.title()

    # Fix specific uppercase words
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
    def save(self, *args, **kwargs):

    # Format all manually entered text fields
        if hasattr(self, "title"):
            self.title = smart_format_text(self.title)

        if hasattr(self, "author"):
            self.author = format_author_name(self.author)

        if hasattr(self, "publication_type"):
            self.publication_type = smart_format_text(self.publication_type)

        if hasattr(self, "publication_year"):
            if self.publication_year:
                self.publication_year = str(self.publication_year).strip()

        super().save(*args, **kwargs)
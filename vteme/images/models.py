from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()

class Image(models.Model):
    user = models.ForeignKey(
        User,
        related_name='images_created',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)
    users_like = models.ManyToManyField(
        User,
        related_name='images_liked',
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title[:50]




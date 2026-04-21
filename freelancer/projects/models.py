from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ProjectModel(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        IN_PROGRESS = "in_progress", "В работе"
        IN_REVISION = "in_revision", "На доработке"
        CANCELED = "canceled", "Отменён"
        FINISHED = "finished", "Завершён"

    name = models.CharField(max_length=254)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    customer = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"


class FileModel(models.Model):
    url = models.URLField(max_length=254)
    filename = models.CharField(max_length=254)
    readable_filename = models.CharField(max_length=254)
    extension = models.CharField(max_length=8)
    version = models.PositiveIntegerField(default=0)
    version_comment = models.CharField(max_length=254, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(
        ProjectModel,
        on_delete=models.CASCADE,
        related_name="files",
    )

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        if not self.readable_filename.endswith(self.extension):
            self.readable_filename = f"{self.readable_filename}.{self.extension}"
        if not self.version_comment:
            self.version_comment = f"Версия {self.version}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-version"]
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

import random

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

    uuid = models.UUIDField(editable=False)
    name = models.CharField(max_length=254)  # Название проекта
    slug = models.SlugField(unique=True, blank=True)  # Уникальный слаг
    description = models.TextField()  # Общее описание проекта
    customer = models.CharField(max_length=100)  # Заказчик проекта
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания проекта
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )  # Статус на выбор
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )  # Владелец проекта (автор)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generate(f"{self.owner.username} {self.name} {random.randint(1000, 9999)}")
        super().save(*args, **kwargs)

    @staticmethod
    def get_status_badge_class(status):
        badges = {
            "new": "secondary",
            "in_progress": "outline",
            "in_revision": "outline",
            "canceled": "destructive",
            "finished": "default",
        }
        return badges[status]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"


class FileModel(models.Model):
    url = models.URLField(max_length=2000)  # Прямая ссылка на скачивание
    dirty_file_url = models.URLField(max_length=2000, null=True)  # Ссылка на грязный файл для предпросмотра
    filename = models.CharField(max_length=254)  # Название файла на сервере
    slug = models.SlugField(unique=True, blank=True)
    readable_filename = models.CharField(max_length=254)  # Название файла при скачивании
    bucket = models.CharField(max_length=63)  # Бакет, в котором хранится файл
    object_path = models.CharField(max_length=2000)  # Путь до объекта с файлом на бакете
    upload_id = models.UUIDField(editable=False, null=True)  # Временный ID во время загрузки в объектное хранилище
    extension = models.CharField(max_length=8)  # Расширение файла
    version = models.PositiveIntegerField(default=0)  # Номер версии (от 0)
    version_comment = models.TextField()  # Комментарий к версии
    uploaded_at = models.DateTimeField(auto_now_add=True)  # ДатаВремя загрузки
    project = models.ForeignKey(
        ProjectModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
    )  # Прикрепление к проекту

    def __str__(self):
        return self.url

    def get_version(self):
        if self.project:
            last_version = FileModel.objects.filter(project=self.project) \
                .aggregate(models.Max('version'))['version__max']

            if last_version is None:
                return 0
            else:
                return last_version + 1
        else:
            return 0

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.version = self.get_version()

        if not self.extension:
            self.extension = self.filename.split(".")[-1]

        if not self.readable_filename.endswith(self.extension):
            self.readable_filename = f"{self.readable_filename}.{self.extension}"

        if not self.slug:
            self.slug = slug_generate(f"{self.project.owner.username} {self.readable_filename} {self.version}")

        if not self.version_comment:
            self.version_comment = f"Версия {self.version}"

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-version"]
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"


def slug_generate(string: str):
    ru_to_en = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i", "й": "y",
        "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
        "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh", "ъ": "y", "ы": "i", "ь": "y", "э": "e", "ю": "u",
        "я": "ya",
    }
    slug = ""
    for s in string.lower():
        if s in ru_to_en.keys():
            slug = f"{slug}{ru_to_en[s]}"
        else:
            slug = f"{slug}{s}"
    slug = slugify(slug)
    return slug

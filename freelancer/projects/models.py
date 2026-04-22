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

    name = models.CharField(max_length=254) #  Название проекта
    slug = models.SlugField(unique=True, blank=True)    #  Уникальный слаг
    description = models.TextField()    #  Общее описание проекта
    customer = models.CharField(max_length=100) #  Заказчик проекта
    created_at = models.DateTimeField(auto_now_add=True)    #  Дата создания проекта
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )   #  Статус на выбор
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )   #  Владелец проекта (автор)

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
    url = models.URLField(max_length=254)   #  Прямая ссылка на скачивание
    filename = models.CharField(max_length=254) #  Название файла на сервере
    readable_filename = models.CharField(max_length=254)    #  Название файла при скачивании
    upload_id = models.UUIDField()  #  Временный ID во время загрузки в объектное хранилище
    extension = models.CharField(max_length=8)  #  Расширение файла
    version = models.PositiveIntegerField(default=0)    #  Номер версии (от 0)
    version_comment = models.CharField(max_length=254, blank=True)  #  Комментарий к версии
    uploaded_at = models.DateTimeField(auto_now_add=True)   #  ДатаВремя загрузки
    project = models.ForeignKey(
        ProjectModel,
        on_delete=models.CASCADE,
        related_name="files",
    )   #  Прикрепление к проекту

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_version = FileModel.objects.filter(project=self.project) \
                .aggregate(Max('version'))['version__max']

            if last_version is None:
                self.version = 0
            else:
                self.version = last_version + 1

        if not self.extension:
            self.extension = self.filename.split(".")[-1]

        if not self.readable_filename.endswith(self.extension):
            self.readable_filename = f"{self.readable_filename}.{self.extension}"

        if not self.version_comment:
            self.version_comment = f"Версия {self.version}"

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-version"]
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

import datetime
import uuid
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from random import randint

import requests
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django_rq import job

from .forms import ProjectForm, FileForm
from .models import ProjectModel, FileModel


@dataclass
class ProjectDataClass:
    """
    Датакласс содержит необходимые данные для отрисовки в template карточек проектов
    """
    title: str  # Название проекта
    status_label: str  # Надпись для пользователя
    status_key: str  # Цвет карточки. Варианты: "default", "in_progress", "review", "done", "paused", "draft"
    status_badge_class: str  # Класс бейджа. Варианты: "default", "secondary", "outline", "destructive"
    customer_name: str  # Имя заказчика
    last_version: int  # Последняя версия
    last_upload_date: str  # dd.mm.yyyy
    last_upload_time: str  # hh:mm
    slug: str  # uuid конкретного проекта


@login_required
def all_projects_view(request):
    context = {
        "projects": list(),
        "status_filters": {
            "all": {"value": "all", "label": "Все", "active": True},
            "new": {"value": "new", "label": "Новые", "active": False},
            "in_progress": {"value": "in_progress", "label": "В работе", "active": False},
            "in_revision": {"value": "in_revision", "label": "На доработке", "active": False},
            "canceled": {"value": "canceled", "label": "Отменены", "active": False},
            "finished": {"value": "finished", "label": "Завершены", "active": False},
        },
        "customer_filters": {
            "all": {"value": "all", "label": "Все", "active": True},
        },
        "current_status": request.GET.get("status", ""),
        "current_customer": request.GET.get("customer", ""),
        "has_filters": bool(request.GET),
        "reset_filters_url": reverse("all_projects"),
        "create_project_url": reverse("project_create"),
    }

    # Помечаем, активны ли фильтры "Всё"
    context["status_filters"]["all"]["active"] = True if context["current_status"] in ("", "all") else False
    context["customer_filters"]["all"]["active"] = True if context["current_customer"] in ("", "all") else False

    # Получаем списки проектов и заказчиков пользователя
    user_projects = ProjectModel.objects.filter(owner=request.user).all()
    customers = user_projects.values_list("customer", flat=True).distinct()

    # Наполняем фильтр по заказчикам актуальными данными
    for customer in customers:
        customer_key = customer.lstrip("\\")
        context["customer_filters"][customer_key] = {
            "value": customer_key,
            "label": customer,
            "active": False,
        }

    # Если стоит фильтр на статус, фильтруем проекты
    if context["current_status"] not in ("", "all"):
        context["status_filters"][context["current_status"]]["active"] = True
        user_projects = user_projects.filter(status=context["current_status"]).all()

    # Если стоит фильтр на заказчика, фильтруем проекты
    if context["current_customer"] not in ("", "all"):
        context["customer_filters"][context["current_customer"]]["active"] = True
        user_projects = user_projects.filter(customer=context["current_customer"]).all()

    # Собираем только релевантные проекты в датаклассы
    for project in user_projects:
        last_file = FileModel.objects.filter(project=project).last()
        project_dc = ProjectDataClass(
            title=project.name,
            status_label=project.get_status_display(),
            status_key=project.status,
            status_badge_class=project.get_status_badge_class(project.status),
            customer_name=project.customer,
            last_version=last_file.version if last_file else "NaN",
            last_upload_date=last_file.uploaded_at.strftime("%d.%m.%Y") if last_file else "NaN",
            last_upload_time=last_file.uploaded_at.strftime("%H:%m") if last_file else "NaN",
            slug=project.slug,
        )
        context["projects"].append(project_dc)

    return render(request, "projects/all_projects.html", context)


def project_view(request, project_slug):
    return render(request, "projects/project.html", {"project_slug": project_slug})


@login_required
def project_create_view(request):
    project_form = ProjectForm(data=request.POST or None)

    project_uuid = request.GET.get("uuid")
    if not project_uuid:
        project_uuid = uuid.uuid4()
        base_url = reverse("project_create")
        return redirect(f"{base_url}?uuid={project_uuid}")

    if request.method == "POST":
        if project_form.is_valid():
            project = ProjectModel(
                uuid=project_uuid,
                name=project_form.cleaned_data["name"],
                description=project_form.cleaned_data["description"],
                customer=project_form.cleaned_data["customer"],
                owner=request.user,
            )
            project.save()

            unpinned_files = FileModel.objects.filter(project=None, upload_id=project_uuid).all()
            for up in unpinned_files:
                up.project = project
                up.save()

            return redirect("all_projects")

    return render(request, "projects/project_create.html", {"project_form": project_form})


@login_required()
def upload_file_view(request):
    upload_form = FileForm(data=request.POST or None)
    project_uuid = request.GET.get("uuid")

    if request.method == 'POST':
        raw_file = request.FILES.get('file')
        upload_id = request.POST.get("upload_id")

        upload_result = upload_file(raw_file, upload_id)

        if upload_result["status"] == "ok":
            file = FileModel(
                url=upload_result["url"],
                filename=upload_result["filename"],
            )

            file.version = file.get_version()
            filename_without_extension, extension = file.filename.rsplit(sep=".", maxsplit=1)
            file.readable_filename = f"{filename_without_extension} v{file.version}.{extension}"
            file.extension = extension
            file.version_comment = f"Версия {file.version}"

            project = ProjectModel.objects.filter(uuid=project_uuid).first()
            if not project:
                file.upload_id = project_uuid
            else:
                file.project = project

            file.save()

            return JsonResponse({"status": "ok"}, status=200)

    return render(request, "projects/upload_file.html", {"upload_form": upload_form})


def upload_file(file, upload_id):
    if not file:
        return JsonResponse({'error': 'Нет файла'}, status=400)

    cache_upload_id = f"object_{upload_id}"
    cache.set(cache_upload_id, 0, timeout=5 * 60)

    with open("iam_token.txt", "r", encoding="utf-8") as token_file:
        iam_token = token_file.read()

    bucket_name = "test-without-versions"

    filename = f"media/{uuid.uuid4()}_{file.name}"
    object_path = f"{datetime.datetime.now().timestamp()}_{filename.split('/')[-1]}"

    with open(f'{filename}', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # В этот момент файл на сервере, но загрузка в Хранилище еще не начата

    object_upload_task.delay(
        bucket_name,
        object_path,
        iam_token,
        filename,
        cache_upload_id,
    )

    return {
        "status": "ok",
        "url": f"https://storage.yandexcloud.net/{bucket_name}/{object_path}",
        "filename": file.name,
    }


def get_upload_value_view(request, upload_id):
    value = cache.get(f"object_{upload_id}", -1)
    data = {
        "progress": round(value, 2),
    }
    return JsonResponse(data)


# Вернет upload_id составной загрузки, который нужно передавать со всеми остальными запросами загрузки
def start_upload(bucket, key, iam_token):
    url = f"https://storage.yandexcloud.net/{bucket}/{key}?uploads"
    headers = {"Authorization": f"Bearer {iam_token}"}
    response = requests.request(method="POST", url=url, headers=headers)

    xml_string = response.content.decode()
    root = ET.fromstring(xml_string)
    ns = root.tag.split("}")[0].strip("{")  # namespace xml (xmlns)
    try:
        upload_id = root.find(f"{{{ns}}}UploadId").text
    except AttributeError:
        upload_id = None

    return upload_id


# Бьет файл на чанки и нумерует
def read_in_chunks(file, chunk_size=10 * 1024 * 1024):
    part_number = 1
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        yield part_number, chunk
        part_number += 1


# Загружает чанк файла в хранилище
def upload_part(bucket, key, headers, upload_id, cache_upload_id, uploaded_parts, part_number, chunk):
    url = f"https://storage.yandexcloud.net/{bucket}/{key}?partNumber={part_number}&uploadId={upload_id}"
    r = requests.put(url, headers=headers, data=chunk)
    e_tag = r.headers.get("ETag")

    uploaded_parts[0] = uploaded_parts[0] + 1
    value = (uploaded_parts[0] / uploaded_parts[1]) * 50
    cache.set(cache_upload_id, value, timeout=5 * 60)

    return part_number, e_tag


# Сборка объекта в хранилище и завершение загрузки
def complete_upload(bucket, key, iam_token, upload_id, filename, e_tags, cache_upload_id):
    url = f"https://storage.yandexcloud.net/{bucket}/{key}?uploadId={upload_id}"
    headers = {
        "Authorization": f"Bearer {iam_token}"
    }

    root = ET.Element("CompleteMultipartUpload")
    for item in e_tags:
        part = ET.SubElement(root, "Part")

        part_number = ET.SubElement(part, "PartNumber")
        part_number.text = str(item[0])

        e_tag = ET.SubElement(part, "ETag")
        e_tag.text = str(item[1])

    tree = ET.ElementTree(root)
    tmp_name = f"tmp/{randint(10000000, 99999999)}.xml"
    tree.write(tmp_name, encoding="utf-8", xml_declaration=True)

    response = requests.post(url, headers=headers, files={"file": open(tmp_name, "rb")})

    cache.set(cache_upload_id, 50, timeout=5 * 60)

    return response.content.decode()


# Загрузка файла в объектное хранилище
def object_upload(bucket, key, iam_token, filename, cache_upload_id):
    with open(filename, "rb") as f:
        parts = list(read_in_chunks(f))
    uploaded_parts = [0, len(parts) + 2]

    headers = {"Authorization": f"Bearer {iam_token}"}
    upload_id = start_upload(bucket, key, iam_token)

    with ThreadPoolExecutor(max_workers=6) as executor:
        e_tags = list(
            executor.map(lambda p: upload_part(bucket, key, headers, upload_id, cache_upload_id, uploaded_parts, *p),
                         parts))

    result = complete_upload(bucket, key, iam_token, upload_id, filename, e_tags, cache_upload_id)

    return result


@job
def object_upload_task(bucket, key, iam_token, filename, cache_upload_id):
    object_upload(bucket, key, iam_token, filename, cache_upload_id)

import datetime
import uuid
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from random import randint

import requests
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django_rq import job


def all_projects_view(request):
    return render(request, "projects/all_projects.html")


def upload_file_view(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        upload_id = request.POST.get("upload_id")

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

        return JsonResponse({'status': 'ok', 'filename': file.name})

    return render(request, "projects/upload_file.html")


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

import json
import os
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from random import randint

import jwt
import requests
import yandexcloud
from celery import shared_task
from django.core.cache import cache
from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

from .models import FileModel


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
    tmp_name = f"media/tmp/{randint(10000000, 99999999)}.xml"
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


def delete_files(file_ids_list: list = None, project_id: str = None):
    with open("iam_token.txt", "r", encoding="utf-8") as token_file:
        iam_token = token_file.read()
    headers = {"Authorization": f"Bearer {iam_token}"}

    if file_ids_list:
        files = FileModel.objects.filter(id__in=file_ids_list)

    elif project_id:
        files = FileModel.objects.filter(project=project_id).all()

    else:
        raise AttributeError("Не передан один из обязательных атрибутов: file_ids_list, project_id")

    for file in files:
        requests.delete(file.url, headers=headers)

    files.delete()

    return True


@shared_task
def object_upload_task(bucket, key, iam_token, filename, cache_upload_id):
    object_upload(bucket, key, iam_token, filename, cache_upload_id)


# Вспомогательная функция для чтения jwt
def create_jwt():
    key_path = os.getenv("JWT_KEY_PATH")

    # Чтение закрытого ключа из JSON-файла
    with open(key_path, 'r', encoding="utf-8") as f:
        obj = f.read()
        obj = json.loads(obj)
        private_key = obj['private_key']
        key_id = obj['id']
        service_account_id = obj['service_account_id']

    sa_key = {
        "id": key_id,
        "service_account_id": service_account_id,
        "private_key": private_key
    }

    now = int(time.time())

    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600
    }

    # Формирование JWT.
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    return (encoded_token, sa_key)


# Schedule функция генерации IAM-токена (раз в час)
@shared_task
def create_iam_token():
    encoded_jwt, sa_key = create_jwt()

    sdk = yandexcloud.SDK(service_account_key=sa_key)
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(
        CreateIamTokenRequest(jwt=encoded_jwt)
    )

    with open("iam_token.txt", "w", encoding="utf-8") as token_file:
        token_file.write(iam_token.iam_token)

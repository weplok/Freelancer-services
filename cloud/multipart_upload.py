import requests
import datetime
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from random import randint

with open("iam_token.txt", "r", encoding="utf-8") as token_file:
    IAM_TOKEN = token_file.read()

BUCKET_NAME = "test-without-versions"

LOCAL_FILE = "media/9dd3bca9-6b16-444e-b65b-2cad779ff38d_Minecraft_ 1.19.2 - Сетевая игра (сторонний сервер) 2022-12-20 19-17-44.mp4"

OBJECT_PATH = f"{datetime.datetime.now().timestamp()}_{LOCAL_FILE.split('/')[-1]}"


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
def upload_part(bucket, key, headers, upload_id, part_number, chunk):
    url = f"https://storage.yandexcloud.net/{bucket}/{key}?partNumber={part_number}&uploadId={upload_id}"
    r = requests.put(url, headers=headers, data=chunk)
    e_tag = r.headers.get("ETag")
    print(f"UPLOADED: {part_number} - {e_tag}")
    return part_number, e_tag


# Сборка объекта в хранилище и завершение загрузки
def complete_upload(bucket, key, iam_token, upload_id, filename, e_tags):
    url = f"https://storage.yandexcloud.net/{bucket}/{key}?uploadId={upload_id}"
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Disposition": filename.split('/')[-1],
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

    response = requests.post(url, headers, files={"file": open(tmp_name, "rb")})

    return response.content.decode()


# Загрузка файла в объектное хранилище
def object_upload(bucket, key, iam_token, filename):
    with open(filename, "rb") as f:
        parts = list(read_in_chunks(f))

    headers = {"Authorization": f"Bearer {iam_token}"}
    upload_id = start_upload(bucket, key, iam_token)

    with ThreadPoolExecutor(max_workers=6) as executor:
        e_tags = list(executor.map(lambda p: upload_part(bucket, key, headers, upload_id, *p), parts))

    result = complete_upload(bucket, key, iam_token, upload_id, filename, e_tags)

    return result


print(object_upload(BUCKET_NAME, OBJECT_PATH, IAM_TOKEN, LOCAL_FILE))

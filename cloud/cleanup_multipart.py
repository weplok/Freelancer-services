import xml.etree.ElementTree as ET

import requests

with open("iam_token.txt", "r", encoding="utf-8") as token_file:
    IAM_TOKEN = token_file.read()

BUCKET_NAME = "test-without-versions"


def list_uploads(bucket, iam_token):
    url = f"https://storage.yandexcloud.net/{bucket}?uploads"
    headers = {"Authorization": f"Bearer {iam_token}"}

    response = requests.request(method="GET", url=url, headers=headers)

    xml_string = response.content.decode()
    root = ET.fromstring(xml_string)
    ns = root.tag.split("}")[0].strip("{")  # namespace xml (xmlns)

    uploads_list = list()

    for upload in root.findall(f"{{{ns}}}Upload"):
        key = upload.find(f"{{{ns}}}Key").text
        upload_id = upload.find(f"{{{ns}}}UploadId").text
        uploads_list.append((key, upload_id,))

    return uploads_list


def abort_uploads(bucket, iam_token):
    uploads_list = list_uploads(bucket, iam_token)
    headers = {"Authorization": f"Bearer {iam_token}"}
    attempts = 0

    while len(uploads_list) != 0 and attempts < 5:
        print(f"Цикл чистки {attempts + 1}")
        for _ in range(len(uploads_list)):
            upload = uploads_list[0]

            url = f"https://storage.yandexcloud.net/{bucket}/{upload[0]}?uploadId={upload[1]}"
            r = requests.delete(url, headers=headers)

            print(f"Незавершенная загрузка удалена: {upload[1]}")
            uploads_list.remove(upload)

        uploads_list = list_uploads(bucket, iam_token)
        attempts += 1


abort_uploads(BUCKET_NAME, IAM_TOKEN)

import requests
import datetime

with open("../freelancer/iam_token.txt", "r", encoding="utf-8") as token_file:
    IAM_TOKEN = token_file.read()

BUCKET_NAME = "test-without-versions"

LOCAL_FILE = "media/photo_5334540864618960317_y_001.jpg"

OBJECT_PATH = f"{datetime.datetime.now().timestamp()}_{LOCAL_FILE.split('/')[-1]}"

headers = {
    "Authorization": f"Bearer {IAM_TOKEN}",
    "Content-Disposition": LOCAL_FILE.split('/')[-1],
}
files = {"file": open(LOCAL_FILE, "rb")}
url = f"https://storage.yandexcloud.net/{BUCKET_NAME}/{OBJECT_PATH}"

print("Start upload...")
response = requests.request(method="PUT", url=url, headers=headers, files=files)
print("Upload was ended!")

print(response.status_code, response.raw, sep="\n")

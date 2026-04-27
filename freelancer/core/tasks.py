import json
import time

import jwt
import yandexcloud
from django.conf import settings
from yandex.cloud.iam.v1.iam_token_service_pb2 import (CreateIamTokenRequest)
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub


# Вспомогательная функция для чтения jwt
def create_jwt():
    key_path = getattr(settings, "JWT_KEY_PATH")

    # Чтение закрытого ключа из JSON-файла
    with open(key_path, 'r') as f:
        obj = f.read()
        obj = json.loads(obj)
        private_key = obj['private_key']
        key_id = obj['id']
        service_account_id = obj['service_account_id']

    now = int(time.time())

    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 7200
    }

    # Формирование JWT.
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    return encoded_token


# Schedule функция генерации IAM-токена (раз в час)
def create_iam_token():
    jwt = create_jwt()

    sdk = yandexcloud.SDK(service_account_key=sa_key)
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(
        CreateIamTokenRequest(jwt=jwt)
    )

    with open("iam_token.txt", "w", encoding="utf-8") as token_file:
        token_file.write(iam_token.iam_token)

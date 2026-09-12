import http.client
import json
import os
import ssl
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from rpc.exceptions import JsonRpcTransportError, JsonRpcResponseError


class JsonRpcClient:

    def __init__(self, endpoint: str, certificate: str, key: str):
        self.endpoint = urlparse(endpoint)

        self._certificate = self._create_temp_file(certificate)
        self._key = self._create_temp_file(key)

        ssl_context = ssl.create_default_context()
        ssl_context.load_cert_chain(
            self._certificate,
            self._key
        )
        self._conn = http.client.HTTPSConnection(
            host=self.endpoint.hostname,
            port=self.endpoint.port or 443,
            context=ssl_context
        )

        self._request_id = 0
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @staticmethod
    def _create_temp_file(content):
        file = NamedTemporaryFile('w', encoding='utf-8', delete=False)
        file.write(content)
        file.close()
        return file.name

    def call(self, method: str, params: dict = None):
        self._request_id += 1
        data = {
            'jsonrpc': '2.0',
            'method': method,
            'id': self._request_id
        }
        if params is not None:
            data['params'] = params
        data = json.dumps(data)

        path = self.endpoint.path or '/'
        if self.endpoint.query:
            path += '?' + self.endpoint.query

        try:
            self._conn.request(
                method='POST',
                url=path,
                body=data,
                headers=self.headers
            )
            response = self._conn.getresponse()
            response_data = response.read()
        except OSError as e:
            raise JsonRpcTransportError(f'Не удалось подключиться к серверу: {e}') from e

        if response.status >= 400:
            raise JsonRpcTransportError(
                f'Ошибка HTTP: {response.status}\n{response.reason}\n{response_data}'
            )

        try:
            response_json = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise JsonRpcResponseError('Сервер вернул невалидный JSON') from e

        return response_json

    def close(self):
        self._conn.close()
        for file in (self._key, self._certificate):
            try:
                os.unlink(file)
            except OSError:
                ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

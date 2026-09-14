import json
from urllib.parse import urlparse

from rpc.exceptions import JsonRpcTransportError, JsonRpcResponseError, TransportError
from rpc.transport import Transport


class JsonRpcClient:

    def __init__(self, endpoint: str, transport: Transport):
        self._request_id = 0
        self.transport = transport
        self.endpoint = urlparse(endpoint)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

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
            response = self.transport.request(
                method='POST',
                url=path,
                body=data,
                headers=self.headers
            )
            response_data = response.read()
        except TransportError as e:
            raise JsonRpcTransportError(f'Не удалось подключиться к серверу: {e}') from e

        if response.status >= 400:
            raise JsonRpcTransportError(
                f'Ошибка HTTP: {response.status} {response.reason}\n{response_data}'
            )

        try:
            response_json = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise JsonRpcResponseError('Сервер вернул невалидный JSON') from e

        if 'error' in response_json:
            raise JsonRpcResponseError(f'Сервер вернул ошибку\n{response_json["error"]}')

        if 'result' in response_json:
            return response_json['result']
        return response_json

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.transport.close()

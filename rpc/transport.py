import http.client
import os
import ssl
from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from rpc.exceptions import TransportError


class Transport(ABC):

    @abstractmethod
    def request(self, method, url, body, headers): ...

    @abstractmethod
    def close(self): ...


class HttpsTransport(Transport):

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

    @staticmethod
    def _create_temp_file(content):
        file = NamedTemporaryFile('w', encoding='utf-8', delete=False)
        file.write(content)
        file.close()
        return file.name

    def request(self, method: str, url: str, body: str | bytes, headers: dict):
        try:
            self._conn.request(
                method=method,
                url=url,
                body=body,
                headers=headers,
            )
            return self._conn.getresponse()
        except OSError as e:
            raise TransportError(f'Не удалось подключиться к серверу: {e}') from e

    def close(self):
        self._conn.close()
        for file in (self._key, self._certificate):
            try:
                os.unlink(file)
            except OSError:
                ...

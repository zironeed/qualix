class JsonRpcError(Exception):
    ...


class JsonRpcTransportError(JsonRpcError):
    ...


class JsonRpcResponseError(JsonRpcError):
    ...

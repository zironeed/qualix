from rpc.client import JsonRpcClient
from rpc.transport import HttpsTransport


def create_json_rpc_client(endpoint: str, certificate: str, key: str) -> JsonRpcClient:
    transport = HttpsTransport(endpoint, certificate, key)
    return JsonRpcClient(endpoint, transport)

import requests


class ManualNfse:
    def __init__(self, api_id, api_key):
        self.__uri = "https://api.arquivei.com.br/v1/nfse/received/manual"
        self.__cursor = 0
        self.__header = {
            "Content-Type": "application/json",
            "x-api-id": api_id,
            "x-api-key": api_key
        }

    def get_manual_nfses(self, cursor=None):
        url = self.__uri
        if cursor is not None:
            if cursor > 0:
                self.__cursor = cursor
                url = f"{self.__uri}?cursor={self.__cursor}"
        document = requests.get(url, headers=self.__header)
        if document.status_code == 200:
            return document.json()
        else:
            raise Exception(f"Status code: {document.status_code}")


class ReceivedNfse:
    def __init__(self, api_id, api_key):
        self.__uri = "https://api.arquivei.com.br/v1/nfse/received"
        self.__cursor = 0
        self.__header = {
            "Content-Type": "application/json",
            "x-api-id": api_id,
            "x-api-key": api_key
        }
        self.failed = []

    def put_manual_status(self, body):
        url = f"{self.__uri}/isocr"
        document = requests.put(url, headers=self.__header, data=body)
        if document.status_code == 200:
            response = document.json()
            if response['data']['result']['failed'] != "[]":
                for item in response["data"]["result"]["failed"]:
                    self.failed.append(item)
        return document.status_code



import io
import json
import logging
from datetime import datetime, timezone
from enum import Enum

import requests
from PIL import Image

import s3_client

logger = logging.getLogger(__name__)


class LogEvent(str, Enum):
    """Log Event enum"""
    START = 'S'
    SHOW = 'SH'
    STOP = 'P'
    WARNING = 'WA'
    ERROR = 'ER'


class XSide:
    """
    2XSide client class that gets clients, items and item files
    """

    def __init__(self, host, email, password):
        self._host = host
        self._email = email
        self._password = password
        self.__tokens = {}
        self._authenticate()

    class ClientError(Exception):
        pass

    class Unauthorized(Exception):
        pass

    class TokenExpiredException(Exception):
        pass

    def _authenticate(self):
        body = {"email": self._email, "password": self._password}
        resp = requests.post(f"{self._host}/api/token/", json=body)
        if resp.status_code != 200:
            logger.error(resp.json())
            raise XSide.Unauthorized("Authorization failed")
        else:
            logger.info("Authorization successful")
            self.__tokens = resp.json()

    def _refresh_tokens(self):
        body = {"refresh": self.__tokens['refresh']}
        resp = requests.post(f"{self._host}/api/refresh/", json=body)
        if resp.status_code != 200:
            logger.error(f"Token refresh failed: {resp.json()}. Trying to reauthenticate")
            self._authenticate()
        else:
            logger.info("Access tokens refreshed successfully.")
            self.__tokens = resp.json()

    @property
    def _headers(self):

        access_token = self.__tokens.get("access", None)
        if access_token:
            headers = {
                "Authorization": f'Bearer {self.__tokens["access"]}'
            }
            return headers
        else:
            raise XSide.Unauthorized("Access token is not available")

    def __get(self, url, *args, **kwargs):
        for _ in range(3):
            resp = requests.get(url, *args, headers=self._headers, **kwargs)
            if 200 <= resp.status_code < 300:
                return resp.json()
            elif resp.status_code == 401 and resp.json().get("code", None) == "token_not_valid":
                self._refresh_tokens()

        raise XSide.ClientError(f"Unexpected response from the server. Response code: {resp.status_code}. Message: {resp.json()}")

    def __post(self, url, *args, **kwargs):
        for _ in range(3):
            resp = requests.post(url, *args, headers=self._headers, **kwargs)
            if 200 <= resp.status_code < 300:
                return resp.json()
            elif resp.status_code == 401 and resp.json().get("code", None) == "token_not_valid":
                self._refresh_tokens()

        raise XSide.ClientError(f"Unexpected response from the server. Response code: {resp.status_code}. Message: {resp.json()}")

    def get_clients(self, client_id: int = None, page_size=100, page=0):
        """
        Get clients
        :param client_id: (optional) client_id to get
        :params page_size: (optional)
        :params page: (optional) page number starting from 0
        :return:
        """
        params = {"page_size": page_size, "page": page}
        return self.__get(f"{self._host}/api/client/{client_id or ''}", params=params)

    def get_items(self, item_id: int = None, page_size: int = 100, page: int = 0):
        """
        Get items
        :param item_id: (optional) item_id to retrieve
        :params page_size: (optional) number of items per page
        :params page: (optional) page number starting from 0
        :return:
        """
        params = {"page_size": page_size, "page": page}
        return self.__get(f"{self._host}/api/item/{item_id or ''}", params=params)

    @staticmethod
    def fetch_image(path: str):
        """
        Fetches the image by path
        :param path: path on storage
        :return:
        """
        return io.BytesIO(s3_client.load_from_s3(path))

    def send_log(self, event: LogEvent, item_file: str = "", data: dict = None, timestamp: datetime = None, lat: float = 0.0, lon: float = 0.0):
        '''send log event to server'''
        timestamp_str = datetime.now(timezone.utc).isoformat() if timestamp is None else timestamp.astimezone(timezone.utc).isoformat()
        payload = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "event": event,
                        "item_file": item_file,
                        "data": json.dumps(data) if data is not None else None,
                        "timestamp": timestamp_str
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                }
            ]
        }
        resp = self.__post(f"{self._host}/api/incoming", json=payload)
        return resp

if __name__ == "__main__":
    from settings import XSIDE_HOST, XSIDE_USER, XSIDE_PASSWORD

    xside = XSide(host=XSIDE_HOST, email=XSIDE_USER, password=XSIDE_PASSWORD)
    print(xside.get_clients())
    print(xside.get_clients(page_size=2))
    print(xside.get_clients(page_size=2, page=1))
    print(xside.get_clients(1))
    print(xside.get_items())
    print(xside.get_items(1))
    print(xside.get_items(page_size=1))
    print(xside.get_items(page_size=1, page=1))
    image_data = xside.fetch_image(path='images/Client1/Test 6/whatsapp.png')
    image = Image.open(image_data)
    image.show()

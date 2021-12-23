import io
import logging

import requests
from PIL import Image

import s3_client
from settings import XSIDE_HOST, XSIDE_USER, XSIDE_PASSWORD

logger = logging.getLogger(__name__)


class XSide:
    """
    2XSide client class
    """

    class ClientError(Exception):
        pass

    class Unauthorized(Exception):
        pass

    class TokenExpiredException(Exception):
        pass

    def __init__(self):
        self.__tokens = {}
        self._authenticate()

    def _authenticate(self):
        body = {"email": XSIDE_USER, "password": XSIDE_PASSWORD}
        resp = requests.post(f"{XSIDE_HOST}/api/token/", json=body)
        if resp.status_code != 200:
            logger.error(resp.json())
        else:
            logger.info("Authorization successful")
            self.__tokens = resp.json()

    def _refresh_tokens(self):
        body = {"refresh": self.__tokens['refresh']}
        resp = requests.post(f"{XSIDE_HOST}/api/refresh/", json=body)
        if resp.status_code != 200:
            logger.error(f"Token refresh failed: {resp.json()}. Trying to reauthenticate")
            self._authenticate()
        else:
            logger.info("Access tokens refreshed successfully.")
            self.__tokens = resp.json()

    @property
    def _headers(self):
        headers = {
            "Authorization": f'Bearer {self.__tokens["access"]}'
        }
        return headers

    def __get(self, url, *args, **kwargs):
        for _ in range(3):
            resp = requests.get(url, *args, headers=self._headers, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401 and resp.json().get("code", None) == "token_not_valid":
                self._refresh_tokens()

        raise XSide.ClientError(f"Unexpected response from the server. Response code: {resp.status_code}. Message: {resp.json()}")

    def get_clients(self, client_id: int = None):
        """
        Get clients
        :param client_id: (optional) client_id to get
        :return:
        """
        return self.__get(f"{XSIDE_HOST}/api/client/{client_id or ''}")

    def get_items(self, item_id: int = None):
        """
        Get items
        :param item_id: (optional) item_id to retrieve s
        :return:
        """
        return self.__get(f"{XSIDE_HOST}/api/item/{item_id or ''}")

    def fetch_image(self, path):
        """
        Fetches the image by path
        :param path: path on storage
        :return:
        """
        image = io.BytesIO(s3_client.load_from_s3(path))
        return image


if __name__ == "__main__":
    xside = XSide()
    print(xside.get_clients())
    print(xside.get_clients(1))
    print(xside.get_items())
    print(xside.get_items(52))
    image_data = xside.fetch_image(path='images/Client1/Test 6/whatsapp.png')
    image = Image.open(image_data)
    image.show()

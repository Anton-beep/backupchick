from typing import *
import requests


class TelegramAPI:
    def __init__(self, token: str, api_url: str = 'https://api.telegram.org'):
        self.token = token
        self.api_url = api_url

    async def get_updates(self, offset: int = None, timeout: int = 5) -> requests.Response:
        url = f'{self.api_url}/bot{self.token}/getUpdates'
        params = {
            'timeout': timeout,
            'offset': offset
        }

        while True:
            try:
                return requests.get(url, params)
            except Exception as e:
                pass

    async def send_message(self, chat_id: int, text: str, parse_mode: str = 'Markdown') -> requests.Response:
        url = f'{self.api_url}/bot{self.token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }

        while True:
            try:
                return requests.post(url, params)
            except Exception as e:
                pass

    async def send_file(self, chat_id: int, file_name: str, file_data: bytes) -> requests.Response:
        url = f'{self.api_url}/bot{self.token}/sendDocument'
        params = {
            'chat_id': chat_id,
        }

        while True:
            try:
                return requests.post(url, data=params, files={'document': (file_name, file_data)}, timeout=None)
            except Exception as e:
                pass

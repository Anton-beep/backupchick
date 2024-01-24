import asyncio
import logging
import os
import shutil
from typing import *
from datetime import datetime as dt

from ..telegramAPI.api import TelegramAPI

import schedule


class Offset:
    """Store last offset in file"""

    def __init__(self, file_path: str):
        self.dir_path = file_path

        # read last offset from file
        try:
            with open(self.dir_path, 'r') as f:
                self.offset = int(f.read())
        except FileNotFoundError:
            with open(self.dir_path, 'w') as f:
                f.write('0')
            self.offset = 0

    def get(self) -> int:
        return self.offset

    def set(self, offset: int):
        self.offset = offset
        with open(self.dir_path, 'w') as f:
            f.write(str(offset))


class WhiteList:
    """White list of users that can recieve backups"""

    def __init__(self, file_path: str):
        self.dir_path = file_path

        # read last offset from file
        try:
            with open(self.dir_path, 'r') as f:
                self.white_list = f.read().split('\n')
            if '' in self.white_list:
                self.white_list.remove('')
        except FileNotFoundError:
            with open(self.dir_path, 'w') as f:
                f.write('')
            self.white_list = []

    def get(self) -> List[int]:
        return list(map(int, self.white_list))

    def add(self, user_id: int):
        self.white_list.append(str(user_id))
        with open(self.dir_path, 'w') as f:
            f.write('\n'.join(self.white_list))

    def contains(self, user_id: int) -> bool:
        return str(user_id) in self.white_list


class Bot:
    def __init__(self, telegram_token: str, chat_password: str, backup_interval: int):
        self.telegram_api = TelegramAPI(telegram_token)
        self.chat_password = chat_password
        self.backup_interval = backup_interval

        self.offset = Offset('offset.txt')
        self.white_list = WhiteList('white_list.txt')

        self.triggers_actions = {
            self.trigger_ping: self.action_ping,
            self.trigger_auth: self.action_auth,
            self.trigger_status: self.action_status,
            self.trigger_get_backup: self.action_get_backup
        }

    # triggers

    @staticmethod
    def trigger_ping(update: dict) -> bool:
        try:
            return Bot.get_message_text(update).lower() == '%ping'
        except ValueError:
            return False

    def trigger_auth(self, update: dict) -> bool:
        try:
            return Bot.get_message_text(update) == f'%password {self.chat_password}'
        except ValueError:
            return False

    @staticmethod
    def trigger_status(update: dict) -> bool:
        try:
            return Bot.get_message_text(update) == f'%status'
        except ValueError:
            return False

    @staticmethod
    def trigger_get_backup(update: dict) -> bool:
        try:
            return Bot.get_message_text(update) == f'%get_backup'
        except ValueError:
            return False

    # actions

    def action_ping(self, update: dict):
        try:
            chat_id = Bot.get_chat_id(update)
            asyncio.run(self.telegram_api.send_message(chat_id, 'pong'))
        except ValueError:
            logging.warning(f'No chat id in update: {update}')

    def action_auth(self, update: dict):
        try:
            chat_id = Bot.get_chat_id(update)
            if self.white_list.contains(chat_id):
                asyncio.run(self.telegram_api.send_message(chat_id, 'This chat is already in white list'))
                return

            asyncio.run(self.telegram_api.send_message(chat_id, 'Authentication successful'))
            self.white_list.add(chat_id)
        except ValueError:
            logging.warning(f'No chat id in update: {update}')

    def action_status(self, update: dict):
        try:
            chat_id = Bot.get_chat_id(update)
            if self.white_list.contains(chat_id):
                asyncio.run(self.telegram_api.send_message(chat_id, 'This chat is in white list'))
            else:
                asyncio.run(self.telegram_api.send_message(chat_id, 'This chat is not in white list'))
        except ValueError:
            logging.warning(f'No chat id in update: {update}')

    def action_get_backup(self, update: dict):
        try:
            chat_id = Bot.get_chat_id(update)
            if not self.white_list.contains(chat_id):
                asyncio.run(self.telegram_api.send_message(chat_id, 'This chat is not in white list'))
                return

            asyncio.run(self.telegram_api.send_message(chat_id, 'Creating backup...'))
            self.create_and_send_backup('backupDir', chat_id)
        except ValueError:
            logging.warning(f'No chat id in update: {update}')

    # additional functions

    @staticmethod
    def get_message_text(update: dict) -> str:
        if 'message' in update:
            if 'text' in update['message']:
                return update['message']['text']
        raise ValueError('No message text in update')

    @staticmethod
    def get_chat_id(update: dict) -> int:
        if 'message' in update:
            if 'chat' in update['message']:
                if 'id' in update['message']['chat']:
                    return update['message']['chat']['id']
        raise ValueError('No chat id in update')

    def create_and_send_backup(self, backup_dir: str, chat_id: int | str):
        shutil.make_archive('backup', 'zip', backup_dir)
        asyncio.run(self.telegram_api.send_file(
            chat_id,
            f'backup{dt.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip',
            open('backup.zip', 'rb').read(),
        ))

    def send_backups_to_whitelist(self, backup_dir: str):
        for user_id in self.white_list.get():
            if not os.path.exists(backup_dir):
                os.mkdir(backup_dir)
            self.create_and_send_backup(backup_dir, user_id)

    # main loop

    def serve(self):
        schedule.every(self.backup_interval).seconds.do(self.send_backups_to_whitelist, 'backupDir')

        while True:
            offset_temp = self.offset.get()
            updates = asyncio.run(self.telegram_api.get_updates(offset_temp)).json()['result']

            for update in updates:
                offset_temp = update['update_id'] + 1

                for trigger, action in self.triggers_actions.items():
                    if trigger(update):
                        action(update)

            self.offset.set(offset_temp)

            schedule.run_pending()

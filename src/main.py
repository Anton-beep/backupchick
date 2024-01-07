import argparse
import logging
import os

from src.bot.bot import Bot


def init_logging():
    logging.basicConfig(
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.WARNING
    )


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('--telegram_token', type=str, help='Telegram bot token', required=True)
    parser.add_argument('--backup_interval', type=int, help='Backup interval in seconds', required=True)
    parser.add_argument('--chat_password', type=str, help='Password for chat', required=True)
    parser.add_argument('--remove_white_list', type=bool, help='Remove user from white list',
                        required=False)

    return parser.parse_args()


def main():
    init_logging()
    config = arguments()
    logging.log(logging.INFO, "Start")

    if config.remove_white_list and os.path.exists('white_list.txt'):
        os.remove('white_list.txt')

    bot = Bot(config.telegram_token, config.chat_password, config.backup_interval)
    bot.serve()


if __name__ == "__main__":
    main()

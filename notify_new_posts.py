import os
import json
import time
import requests
import importlib
from config import acc_4_mon

# Глобальный словарь для хранения уведомленных постов
notified_posts = {}

# Ваш Telegram Bot Token и Chat ID
TELEGRAM_BOT_TOKEN = '7391995490:AAFFhOJmsWz9sUmNNDFKyGVolC-xwcZyjoM'
TELEGRAM_CHAT_ID = '-1002189787340'

# Функция для отправки сообщения в Telegram


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'  # Поддержка HTML-разметки
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Message sent to Telegram: {text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")

# Функция для чтения данных из acc_4_mon.py для получения списка аккаунтов


def read_account_monitor():
    try:
        # Перезагрузите модуль для получения актуальных данных
        importlib.reload(acc_4_mon)
        if 'account_monitor' in dir(acc_4_mon):
            return acc_4_mon.account_monitor
    except ImportError:
        return []

# Функция для мониторинга новых постов и отправки уведомлений


def notify_new_posts():
    while True:
        account_monitor = read_account_monitor()

        if not account_monitor:
            print("No accounts found in acc_4_mon.py")
            time.sleep(10)  # Пауза перед следующей попыткой
            continue

        for username in account_monitor:
            filename = f"{username}_filtered_tweets.json"
            filepath = os.path.join("result", filename)

            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                    # Здесь добавляем логику для отслеживания новых постов
                    new_posts = []
                    for post in data:
                        post_link = post['link']
                        if post_link not in notified_posts.get(username, []):
                            new_posts.append(post)

                    # Отправка уведомлений или другая логика здесь
                    if new_posts:
                        for post in new_posts:
                            post_text = post.get('text', 'No text')
                            post_link = post.get('link', 'No link')
                            post_date = post.get('date', 'No date')
                            user_info = post.get('user', {})
                            post_username = user_info.get(
                                'username', 'No username')

                            if isinstance(post_date, int):  # Убедитесь, что это timestamp
                                post_date = time.strftime(
                                    '%Y-%m-%d %H:%M:%S', time.gmtime(post_date))

                            message = (
                                f"New post from:\n{post_username}\n\n"
                                f"Date: {post_date}\n\n"
                                f"{post_text}\n\n"
                                f"{post_link}"
                            )
                            send_telegram_message(message)

                        # Обновляем список уведомленных постов для аккаунта
                        notified_posts.setdefault(username, []).extend(
                            [post['link'] for post in new_posts])

                except Exception as e:
                    print(f"Error loading or processing {filename}: {e}")
            else:
                print(f"File {filename} not found")

        # Пауза перед следующей проверкой (например, каждые 10 секунд)
        time.sleep(10)


# Основной код для запуска мониторинга новых постов
if __name__ == "__main__":
    notify_new_posts()

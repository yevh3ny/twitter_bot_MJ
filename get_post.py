from ntscraper import Nitter
import json
import os

# Используем аккаунты для отслеживания из конфигурации
try:
    from config.acc_4_mon import account_monitor
except ImportError:
    account_monitor = ['']

# Используем ключевые слова из конфигурации
try:
    from config.keywords import keywords
except ImportError:
    keywords = ['']

# Создаем папку для результатов, если она не существует
result_dir = 'result'
os.makedirs(result_dir, exist_ok=True)
nitter_server = "https://nitter.lucabased.xyz"

for account in account_monitor:
    if account:  # Проверяем, что аккаунт не пустой
        # Получаем последние 100 твитов пользователя
        tweets = Nitter(skip_instance_check=True).get_tweets(
            account, mode='user', number=100, instance=nitter_server)

        # Сохраняем все твиты в файл с именем пользователя в папке result
        all_tweets_filename = os.path.join(result_dir, f"{account}.json")
        with open(all_tweets_filename, "w") as file:
            json.dump(tweets, file, indent=4)
        print(f"Все твиты сохранены в файл {all_tweets_filename}")

        tweets_list = tweets.get("tweets", [])

        # Фильтруем твиты по ключевым словам
        filtered_tweets = []
        for tweet in tweets_list:
            tweet_text = tweet.get('text', '').lower()
            for keyword in keywords:
                if keyword.lower().strip() in tweet_text:
                    filtered_tweets.append(tweet)
                    break  # Если нашли одно ключевое слово, нет необходимости проверять другие

        # Сохраняем отфильтрованные твиты в файл JSON в папке result
        filtered_tweets_filename = os.path.join(
            result_dir, f"{account}_filtered_tweets.json")
        with open(filtered_tweets_filename, "w") as file:
            json.dump(filtered_tweets, file, indent=4)

        print(f"Найдено {len(filtered_tweets)} твитов, соответствующих ключевым словам.")
        print(f"Отфильтрованные твиты сохранены в файл {filtered_tweets_filename}")

import subprocess
import time

while True:
    # Запускаем скрипт и ждем его завершения
    subprocess.run(["python3", "get_post.py"])
    # Ждем 10 секунд перед следующим запуском
    time.sleep(10)

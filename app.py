from flask import Flask, render_template, request, redirect, url_for, flash
import os
import tweepy
import json
import random
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

config_dir = 'config'
acc_file = os.path.join(config_dir, 'acc_4_mon.py')
keywords_file = os.path.join(config_dir, 'keywords.py')
acc_com_file = os.path.join(config_dir, 'acc_4_com.py')
auto_mode_file = os.path.join(config_dir, 'auto_mode.py')


def read_account_monitor():
    if os.path.exists(acc_file):
        with open(acc_file) as file:
            content = file.read()
            account_monitor = {}
            exec(content, {}, account_monitor)
            return account_monitor['account_monitor']
    return []


def read_keywords():
    if os.path.exists(keywords_file):
        with open(keywords_file) as file:
            content = file.read()
            keywords = {}
            exec(content, {}, keywords)
            return keywords['keywords']
    return []


def read_com_accounts():
    if os.path.exists(acc_com_file):
        with open(acc_com_file) as file:
            content = file.read()
            com_accounts = {}
            exec(content, {}, com_accounts)
            return com_accounts['ACCOUNTS']
    return []


def read_selected_com_accounts():
    selected_file = os.path.join(config_dir, 'selected_com_accounts.py')
    if os.path.exists(selected_file):
        with open(selected_file) as file:
            content = file.read()
            selected_com_accounts = {}
            exec(content, {}, selected_com_accounts)
            return selected_com_accounts['SELECTED_ACCOUNTS']
    return []


def read_auto_mode():
    if os.path.exists(auto_mode_file):
        with open(auto_mode_file) as file:
            content = file.read()
            auto_mode = {}
            exec(content, {}, auto_mode)
            return auto_mode.get('AUTO_MODE', False)
    return False


@app.route('/save_auto_mode', methods=['POST'])
def save_auto_mode_route():
    auto_mode = request.form.get('auto_mode') == 'on'

    with open(auto_mode_file, 'w') as file:
        file.write(f"AUTO_MODE = {auto_mode}\n")

    flash('Auto mode setting saved successfully!')
    return redirect(url_for('settings'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/settings', methods=['GET'])
def settings():
    account_monitor = read_account_monitor()
    keywords = read_keywords()
    com_accounts = read_com_accounts()
    selected_com_accounts = read_selected_com_accounts()
    auto_mode = read_auto_mode()
    return render_template('settings.html', account_monitor=account_monitor, keywords=keywords, com_accounts=com_accounts, selected_com_accounts=selected_com_accounts, auto_mode=auto_mode)


@app.route('/save_com_accounts', methods=['POST'])
def save_com_accounts():
    selected_accounts = request.form.getlist('com_accounts')

    # Преобразование строкового формата в формат словарей
    selected_accounts_dicts = [eval(account) for account in selected_accounts]

    with open(os.path.join(config_dir, 'selected_com_accounts.py'), 'w') as file:
        file.write("SELECTED_ACCOUNTS = ")
        json.dump(selected_accounts_dicts, file, indent=4)

    flash('Commenting accounts saved successfully!')
    return redirect(url_for('settings'))


@app.route('/save_accounts', methods=['POST'])
def save_accounts():
    input1 = request.form.get('input1') or 'None'
    accounts = [acc.strip() for acc in input1.split(',')]

    with open(acc_file, 'w') as file:
        file.write(f"account_monitor = {accounts}\n")

    flash('Settings saved successfully! WAIT 60 seconds!!!')
    return redirect(url_for('settings'))


@app.route('/save_keywords', methods=['POST'])
def save_keywords():
    keyword1 = request.form.get('keyword1') or 'None'
    keywords = [kw.strip() for kw in keyword1.split(',')]

    with open(keywords_file, 'w') as file:
        file.write(f"keywords = {keywords}\n")

    flash('Keywords saved successfully! WAIT 60 seconds!!!')
    return redirect(url_for('settings'))


@app.route('/posts')
def posts():
    return render_template('posts.html')


@app.route('/all_posts')
def all_posts():
    try:
        account_monitor = read_account_monitor()

        accounts = account_monitor

        account_posts = {}
        for account in accounts:
            filename = f"{account}.json"
            filepath = os.path.join("result", filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    account_data = json.load(file)
                    posts = account_data['tweets']
                    account_posts[account] = posts
            else:
                account_posts[account] = []

        return render_template('all_posts.html', accounts=accounts, account_posts=account_posts)
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return render_template('error.html', message=f'Wait until the data is loaded and refresh the page! {e}')


@app.route('/keyword_posts')
def keyword_posts():
    try:
        account_monitor = read_account_monitor()

        accounts = account_monitor

        account_posts = {}
        for account in accounts:
            filename = f"{account}_filtered_tweets.json"
            filepath = os.path.join("result", filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    account_data = json.load(file)
                    posts = []
                    for tweet in account_data:
                        post = {
                            'link': tweet['link'],
                            'text': tweet['text'],
                            'username': tweet['user']['username'],
                            'date': tweet['date'],
                            'avatar': tweet['user']['avatar']
                        }
                        posts.append(post)
                    account_posts[account] = posts
            else:
                account_posts[account] = []

        return render_template('keyword_posts.html', accounts=accounts, account_posts=account_posts)
    except Exception as e:
        print(f"Error loading data: {e}")
        return render_template('error.html', message=f'Error loading data: {e}')


@app.route('/commenting', methods=['POST'])
def commenting():
    selected_posts = request.form.getlist('selected_posts')

    posts_info = []
    for post in selected_posts:
        posts_info.append({
            'link': post
        })

    return render_template('commenting.html', posts_info=posts_info)


@app.route('/send_comment', methods=['POST'])
def send_comment():
    text_comments = request.form.get('comment')
    tweet_ids = request.form.getlist('tweet_ids[]')

    from config.selected_com_accounts import SELECTED_ACCOUNTS

    comments = text_comments.split('\n')  # Разделить комментарии по строкам

    for i, comment in enumerate(comments):
        if i >= len(SELECTED_ACCOUNTS):
            break  # Прекратить, если комментариев больше, чем аккаунтов

        account = SELECTED_ACCOUNTS[i]
        api_key = account['CONSUMER_KEY']
        api_secret = account['CONSUMER_SECRET']
        bearer_token = account['BEARER_TOKEN']
        access_token = account['ACCESS_TOKEN']
        access_token_secret = account['ACCESS_TOKEN_SECRET']

        client = tweepy.Client(bearer_token, api_key, api_secret,
                               access_token, access_token_secret)
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, access_token, access_token_secret)
        api = tweepy.API(auth)

        for tweet_id in tweet_ids:
            if comment.strip():  # Проверить, что комментарий не пустой
                response = client.create_tweet(
                    in_reply_to_tweet_id=tweet_id, text=comment.strip())
                print(response)
                # Задержка в 30 секунд перед отправкой следующего комментария
                time.sleep(10)
    return render_template('comm_success.html', flash="Comments sent successfully!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

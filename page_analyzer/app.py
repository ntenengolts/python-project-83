import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from flask import request, redirect, flash, render_template, url_for
from urllib.parse import urlparse
from validators import url as is_valid_url
from datetime import datetime
from db import get_connection
from . import app  # импорт Flask-приложения


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    raw_url = request.form.get('url', '').strip()
    if not is_valid_url(raw_url) or len(raw_url) > 255:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized = raw_url
    created_at = datetime.now()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (normalized,))
            result = cur.fetchone()
            if result:
                flash('Страница уже существует', 'info')
                return redirect(url_for('show_url', url_id=result[0]))
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                (normalized, created_at)
            )
            new_id = cur.fetchone()[0]
            conn.commit()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', url_id=new_id))


@app.route('/urls/<int:url_id>')
def show_url(url_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s",
                (url_id,)
            )
            url = cur.fetchone()

            cur.execute(
                "SELECT id, status_code, h1, title, description, created_at "
                "FROM url_checks "
                "WHERE url_id = %s ORDER BY created_at DESC",
                (url_id,)
            )
            checks = cur.fetchall()

    return render_template('url.html', url=url, checks=checks)


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def add_check(url_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем информацию о сайте
            cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            result = cur.fetchone()
            if not result:
                flash('Сайт не найден', 'danger')
                return redirect(url_for('show_urls'))

            site_name = result[0]
            created_at = datetime.now()

            try:
                # Выполняем запрос к сайту
                response = requests.get(site_name, timeout=10)
                response.raise_for_status()
                status_code = response.status_code

                # Парсим HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                h1 = soup.find('h1').get_text(strip=True) if soup.find('h1') else None
                title = soup.title.string if soup.title else None
                description_tag = soup.find('meta', attrs={'name': 'description'})
                description = description_tag['content'] if description_tag else None

            except RequestException as _:
                flash('Произошла ошибка при проверке', 'danger')
                return redirect(url_for('show_url', url_id=url_id))
            except Exception as _:
                flash('Произошла ошибка при парсинге HTML', 'danger')
                return redirect(url_for('show_url', url_id=url_id))

            # Создаём новую проверку
            cur.execute(
                "INSERT INTO url_checks "
                "(url_id, status_code, h1, title, description, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (url_id, status_code, h1, title, description, created_at)
            )
            cur.fetchone()
            conn.commit()

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', url_id=url_id))


@app.route('/urls')
def show_urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls ORDER BY id DESC")
            urls = cur.fetchall()

            updated_urls = []
            for url_row in urls:
                cur.execute(
                    "SELECT created_at, status_code "
                    "FROM url_checks WHERE url_id = %s "
                    "ORDER BY created_at DESC LIMIT 1",
                    (url_row[0],)
                )
                last_check = cur.fetchone()
                if last_check:
                    last_check_date, status_code = last_check
                else:
                    last_check_date, status_code = None, None

                # Добавляем дату и статус к данным сайта
                updated_url = url_row + (last_check_date, status_code)
                updated_urls.append(updated_url)

    return render_template('urls.html', urls=updated_urls)


@app.route('/test')
def test():
    return "Hello from Flask!", 200


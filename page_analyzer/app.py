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
    raw_url = request.form.get('url')
    if not is_valid_url(raw_url) or len(raw_url) > 255:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized = urlparse(raw_url).netloc
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
    return render_template('url.html', url=url)


@app.route('/urls')
def show_urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls ORDER BY id DESC")
            urls = cur.fetchall()
    return render_template('urls.html', urls=urls)


@app.route('/test')
def test():
    return "Hello from Flask!", 200


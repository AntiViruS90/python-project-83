import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

# from page_analyzer.db import (
#     add_check_to_db,
#     add_url_to_db,
#     get_checks_desc,
#     get_url_by_id,
#     get_url_by_name,
#     get_urls_with_latest_check,
# )
from page_analyzer.db import UrlRepository
from page_analyzer.html_parser import parse_page
from page_analyzer.url_validator import validate

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

repo = UrlRepository()


def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@app.get('/')
def page_analyzer():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    new_url = request.form.get('url')

    error = validate(new_url)

    if error:
        flash(f'{error}', 'danger')
        return render_template('index.html'), 422

    normal_url = normalize_url(new_url)

    if old_url_data:= repo.get_url_by_name(normal_url):
        flash('Страница уже существует', 'primary')
        return redirect(url_for('show_url', id=old_url_data[0].id))

    new_url_id = repo.add_url_to_db(normal_url)
    flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=new_url_id))


@app.get('/urls')
def show_all_urls():
    all_urls = repo.get_urls_with_latest_check()
    return render_template('details.html', all_urls=all_urls)


@app.get('/urls/<int:id>')
def show_url(id):
    url_data = repo.get_url_by_id(id)
    all_checks = repo.get_checks_desc(id)
    message = get_flashed_messages(with_categories=True)

    return render_template(
        'list.html',
        url_data=url_data,
        all_checks=all_checks,
        message=message
    )


@app.post('/urls/<id>/checks')
def add_check(id):
    url = repo.get_url_by_id(id)

    try:
        response = requests.get(url[0].name)
        response.raise_for_status()

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')

        return redirect(url_for('show_url', id=id))

    status_code = response.status_code
    page_data = parse_page(response.text)
    repo.add_check_to_db(id, status_code, page_data)
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))

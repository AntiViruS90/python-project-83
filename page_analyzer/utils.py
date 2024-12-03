from urllib.parse import urlparse
from validators import url as validate


def validate_url(input_url):
    if not input_url:
        return "URL обязательно должен быть заполнен"
    if not validate(input_url):
        return "Не корректный URL-адрес"
    if len(input_url) > 255:
        return "Введенный URL-адрес превышает 255 символов"


def normalize_url(url):
    parse_url = urlparse(url)
    return f"{parse_url.scheme}://{parse_url.netloc}"

import psycopg2
from psycopg2.extras import NamedTupleCursor


class DbManager:

    def __init__(self, app):
        self.app = app

    @staticmethod
    def exec_with_in_db(commit):
        def flag(func):
            def inner(self, *args, **kwargs):
                try:
                    with psycopg2.connect(
                            self.app.config['DATABASE_URL']
                    ) as conn:
                        with conn.cursor(
                                cursor_factory=NamedTupleCursor
                        ) as cursor:
                            result = func(self, cursor, *args, **kwargs)
                            if commit:
                                conn.commit()
                                return result
                            else:
                                conn.commit()
                                return result
                except psycopg2.Error as e:
                    print(f"Ошибка при выполнении транзакции {e}")
                    raise e

            return inner

        return flag

    @exec_with_in_db(commit=True)
    def insert_url_in_db(self, cursor, url):
        cursor.execute(
            "INSERT INTO urls (name) VALUES (%s) RETURNING *",
            (url,)
        )
        url_data = cursor.fetchone()
        return url_data

    @exec_with_in_db(commit=True)
    def insert_url_check_in_db(self, cursor, check):
        cursor.execute(
            "INSERT INTO url_checks("
            "url_id, "
            "status_code, "
            "h1, "
            "title, "
            "description"
            ")"

            "VALUES (%s, %s, %s, %s, %s)",
            (
                check['url_id'],
                check['response'],
                check['h1'],
                check['title'],
                check.get('description', ' ')
            )
        )

    @exec_with_in_db(commit=False)
    def get_url_from_urls_list(self, cursor, url_id):
        cursor.execute("SELECT * FROM urls WHERE id=%s", (url_id,))
        decired_url = cursor.fetchone()
        return decired_url if decired_url else False

    @exec_with_in_db(commit=False)
    def get_url_from_urls_checks_list(self, cursor, url_id):
        cursor.execute(
            "SELECT * FROM url_checks WHERE url_id=%s "
            "ORDER BY id DESC", (url_id, )
        )
        result = cursor.fetchall()

        return result

    @exec_with_in_db(commit=True)
    def get_url_by_name(self, cursor, url):
        cursor.execute("SELECT * FROM urls WHERE name=%s", (url, ))
        url_id = cursor.fetchone()

        return url_id.id if url_id else None

    @exec_with_in_db(commit=False)
    def get_urls_list(self, cursor):
        query = (
            "SELECT DISTINCT ON (urls.id) urls.id AS id, "
            "url_checks.id AS check_id, "
            "url_checks.status_code AS status_code, "
            "url_checks.created_at AS created_at, "
            "urls.name AS name "
            "FROM urls "
            "LEFT JOIN url_checks ON urls.id = url_checks.url_id "
            "ORDER BY urls.id DESC, check_id DESC"
        )
        cursor.execute(query)

        return cursor.fetchall()

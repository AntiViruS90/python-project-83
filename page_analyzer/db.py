import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


class UrlRepository:
    def __init__(self):
        self.connection = None

    def fetch_all(self, query, values=()):
        with get_db_connection() as cur:
            cur.execute(query, values)
            return cur.fetchall()

    def add_url_to_db(self, url):
        query = """INSERT INTO urls (name) VALUES (%s) RETURNING id"""
        with get_db_connection() as cur:
            cur.execute(query, (url, ))
            new_id = cur.fetchone()[0]

        return new_id

    def get_url_by_name(self, url):
        query = """SELECT * FROM urls WHERE name = %s"""
        url_data = self.fetch_all(query, (url, ))

        return url_data

    def get_url_by_id(self, url_id):
        query = """SELECT * FROM urls WHERE id = %s"""
        value = (url_id, )
        with get_db_connection() as cur:
            cur.execute(query, value)
            url_data = cur.fetchall()

        return url_data

    def add_check_to_db(self, url_id, status_code, page_data):
        query = """
            INSERT INTO url_checks (
                url_id,
                status_code,
                h1,
                title,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
                """
        values = (
            url_id,
            status_code,
            page_data['h1'],
            page_data['title'],
            page_data['description']
        )

        with get_db_connection() as cur:
            cur.execute(query, values)

    def get_urls_with_latest_check(self):
        query = """
            SELECT  urls.id,
                    urls.name,
                    COALESCE(url_checks.status_code::text, '') AS status_code,
                    COALESCE(MAX(url_checks.created_at)::text, '') AS latest_check
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, url_checks.status_code
            ORDER BY urls.id DESC
        """
        all_urls_with_latest_check = self.fetch_all(query)
        return all_urls_with_latest_check

    def get_checks_desc(self, url_id):
        query = """
            SELECT id,
                   status_code,
                   COALESCE(h1, '') as h1,
                   COALESCE(title, '') as title,
                   COALESCE(description, '') as description,
                   created_at::text
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        all_checks = self.fetch_all(query, (url_id, ))
        return all_checks

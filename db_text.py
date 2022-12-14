from logging import fatal
import psycopg2
from utils import host, user, password, db_name

try:
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )
        print(f"Server version {cursor.fetchone()}")
except Exception as ex:
    fatal(ex)
finally:
    if connection:
        connection.close()
import psycopg2

from loguru import logger
from config import database, user, password, host, port


def db_clean():
    try:
        connection = psycopg2.connect(database=database,
                                      user=user,
                                      password=password,
                                      host=host,
                                      port=port)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                    DELETE FROM tickets_table
                    WHERE time_create < (NOW() - interval '1 minute');""")

            connection.commit()
            if cursor.rowcount:
                logger.info(f'Cleared {cursor.rowcount} records.')

    except Exception as ex:
        logger.error(f'Cleaner | {ex}')
    finally:
        if connection:
            connection.close()


def main():
    db_clean()


if __name__ == '__main__':
    main()

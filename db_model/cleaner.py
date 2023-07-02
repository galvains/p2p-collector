from loguru import logger


def db_clean(connection) -> None:
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                    DELETE FROM tickets_table
                    WHERE time_create < (NOW() - interval '1 minute');""")

            connection.commit()
            if cursor.rowcount:
                logger.info(f'Cleared {cursor.rowcount} records.')

    except Exception as ex:
        logger.error(f'DB-CLEAN | {ex}')

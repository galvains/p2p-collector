# import aiopg

from loguru import logger


def db_insert(connection, data: dict) -> None:
    try:
        with connection.cursor() as cursor:

            if data['exchange_id'] == 3:
                cursor.execute(f"""INSERT INTO tickets (nick_name, price, orders, available, max_limit, min_limit,
                                rate, pay_methods, currency, coin, trade_type, link, time_create, exchange_id)
                                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s WHERE NOT EXISTS(
                                SELECT 1 FROM tickets
                                WHERE nick_name = %s AND link = %s)""",
                               (data['nick_name'], data['price'], data['orders'], data['available'],
                                data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
                                data['currency'], data['coin'], data['trade_type'], data['link'],
                                data['exchange_id'], data['nick_name'], data['link']))
            else:
                cursor.execute(f"""INSERT INTO tickets (nick_name, price, orders, available, max_limit, min_limit,
                                rate, pay_methods, currency, coin, trade_type, link, time_create, exchange_id)
                                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s WHERE NOT EXISTS(
                                SELECT 1 FROM tickets
                                WHERE nick_name = %s AND price = %s)""",
                               (data['nick_name'], data['price'], data['orders'], data['available'],
                                data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
                                data['currency'], data['coin'], data['trade_type'], data['link'],
                                data['exchange_id'], data['nick_name'], data['price']))

            connection.commit()

    except Exception as ex:
        logger.error(f'DB-INSERT | {ex}')
        connection.rollback()


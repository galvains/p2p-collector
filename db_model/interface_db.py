import aiopg

from loguru import logger
from config import database, user, password, host, port


def db_insert(connection, data: dict) -> None:
    try:
        with connection.cursor() as cursor:

            if data['exchange_id'] == 3:
                cursor.execute(f"""INSERT INTO tickets_table (nick_name, price, orders, available, max_limit, min_limit,
                                rate, pay_methods, currency, coin, trade_type, link, time_create, exchange_id)
                                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s WHERE NOT EXISTS(
                                SELECT 1 FROM tickets_table
                                WHERE nick_name = %s AND link = %s)""",
                               (data['nick_name'], data['price'], data['orders'], data['available'],
                                data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
                                data['currency'], data['coin'], data['trade_type'], data['link'],
                                data['exchange_id'], data['nick_name'], data['link']))
            else:
                cursor.execute(f"""INSERT INTO tickets_table (nick_name, price, orders, available, max_limit, min_limit,
                                rate, pay_methods, currency, coin, trade_type, link, time_create, exchange_id)
                                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s WHERE NOT EXISTS(
                                SELECT 1 FROM tickets_table
                                WHERE nick_name = %s AND price = %s)""",
                               (data['nick_name'], data['price'], data['orders'], data['available'],
                                data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
                                data['currency'], data['coin'], data['trade_type'], data['link'],
                                data['exchange_id'], data['nick_name'], data['price']))

            connection.commit()

    except Exception as ex:
        logger.error(f'DB-INSERT | {ex}')


async def aio_db_insert(data: dict) -> None:
    dsn = f'dbname={database} user={user} password={password} host=127.0.0.1'
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                if data['exchange_id'] == 3:
                    await cur.execute(f"""INSERT INTO tickets_table (nick_name, price, orders, available, max_limit, min_limit,
                                rate, pay_methods, currency, coin, trade_type, link, time_create, exchange_id)
                                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s WHERE NOT EXISTS(
                                SELECT 1 FROM tickets_table
                                WHERE nick_name = %s AND link = %s)""",
                                      (data['nick_name'], data['price'], data['orders'], data['available'],
                                       data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
                                       data['currency'], data['coin'], data['trade_type'], data['link'],
                                       data['exchange_id'], data['nick_name'], data['link']))
                else:
                    await cur.execute(f"""INSERT INTO tickets_table (nick_name, price, orders, available, max_limit, min_limit,
                                rate, pay_methods, currency, coin, trade_type, link, time_create, exchange_id)
                                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s WHERE NOT EXISTS(
                                SELECT 1 FROM tickets_table
                                WHERE nick_name = %s AND price = %s)""",
                                      (data['nick_name'], data['price'], data['orders'], data['available'],
                                       data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
                                       data['currency'], data['coin'], data['trade_type'], data['link'],
                                       data['exchange_id'], data['nick_name'], data['price']))
                ret = []
                async for row in cur:
                    ret.append(row)
                assert ret == [(1,)]
    logger.info('all done-aio_db_insert')


import psycopg2

from config import database, user, password, host, port


def db_print(connection) -> None:
    try:

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * from tickets_table")
            print(cursor.fetchall())

    except Exception as ex:
        print(f'Error by {ex}')
    finally:
        if connection:
            connection.close()
            print('Session closed.')


def db_insert(data: dict) -> None:
    try:
        connection = psycopg2.connect(database=database,
                                      user=user,
                                      password=password,
                                      host=host,
                                      port=port)

        with connection.cursor() as cursor:

            # cursor.execute(f"""INSERT INTO tickets_table (nick_name, price, orders, available, max_limit, min_limit,
            #                 rate, pay_methods, currency, coin, trade_type, link, exchange_id)
            #                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            #                (data['nick_name'], data['price'], data['orders'], data['available'],
            #                 data['max_limit'], data['min_limit'], data['rate'], data['pay_methods'],
            #                 data['currency'], data['coin'], data['trade_type'], data['link'],
            #                 data['exchange_id']))

            # for paxful
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
            # print('Value add')

    except Exception as ex:
        print(f'Error by {ex}')
    finally:
        if connection:
            connection.close()
            # print('Session closed.')


def main():
    db_insert()


if __name__ == '__main__':
    main()

import asyncio
import psycopg2

from loguru import logger
from threading import Thread
from utils.proxies import set_proxy
from db_model.cleaner import db_clean
from config import database, user, password, host, port
from .engine import distributor_binance, distributor_paxful, distributor_bybit


class TaskManager(object):
    """
    Менеджер для создания задач, исходя из данных прокси
    """

    def __init__(self, proxy_data: dict, number: int):
        self.proxy = proxy_data
        self.number = number

    def check_rstream(self):
        logger.info(self.get_all())

    def get_all(self):
        if self.number == 0:
            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                self.bin_btc(conn)
                self.pax_btc(conn)
        elif self.number == 1:
            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                self.byb_btc(conn)
                self.pax_usdt(conn)
        elif self.number == 2:
            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                self.bin_eth(conn)
                self.byb_usdc(conn)
                self.pax_usdc(conn)
        elif self.number == 3:
            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                self.high_loaded(conn)
        elif self.number == 4:
            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                self.none1(conn)

    # @staticmethod
    # def _get_connect_db():

    def high_loaded(self, conn):
        tasks = [
            asyncio.create_task(distributor_binance('USDT', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('USDT', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('USDT', 'EUR', 'BUY', self.proxy, connect=conn)),

        ]

    def bin_btc(self, conn):

        tasks = [
            asyncio.create_task(distributor_binance('BTC', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('BTC', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('BTC', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('BTC', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def none1(self, conn):
        tasks = [
            asyncio.create_task(distributor_binance('USDT', 'EUR', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('USDT', 'USD', 'BUY', self.proxy, connect=conn)),
            # asyncio.create_task(distributor_bybit('USDT', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('USDT', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('USDT', 'EUR', 'SELL', self.proxy, connect=conn)),

        ]

    def bin_eth(self, conn):
        tasks = [
            asyncio.create_task(distributor_binance('ETH', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('ETH', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('ETH', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_binance('ETH', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def byb_btc(self, conn):
        tasks = [
            asyncio.create_task(distributor_bybit('BTC', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('BTC', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('BTC', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('BTC', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def byb_usdc(self, conn):
        tasks = [
            asyncio.create_task(distributor_bybit('USDC', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('USDC', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('USDC', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_bybit('USDC', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def pax_btc(self, conn):
        tasks = [
            asyncio.create_task(distributor_paxful('BTC', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('BTC', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('BTC', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('BTC', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def pax_usdt(self, conn):
        tasks = [
            asyncio.create_task(distributor_paxful('USDT', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('USDT', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('USDT', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('USDT', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def pax_usdc(self, conn):
        tasks = [
            asyncio.create_task(distributor_paxful('USDC', 'USD', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('USDC', 'USD', 'SELL', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('USDC', 'EUR', 'BUY', self.proxy, connect=conn)),
            asyncio.create_task(distributor_paxful('USDC', 'EUR', 'SELL', self.proxy, connect=conn)),
        ]

    def __str__(self):
        return str(self.__dict__)


async def loader(threads_count: int, delay: int) -> None:
    logger.info('Pool created...')
    counter_laps = 1
    while True:
        try:
            logger.info(f'Lap: {counter_laps} started...')
            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                db_clean(conn)

            proxies = set_proxy()
            threads_list = list()

            for elem in range(threads_count):
                threads_list.append(TaskManager(proxy_data=proxies[elem], number=elem))

            for elem in threads_list:
                thr = Thread(target=elem.get_all())
                thr.start()
                thr.join()

            await asyncio.sleep(delay)
            counter_laps += 1

        except Exception as ex:
            logger.error(f'LOADER | {ex}')

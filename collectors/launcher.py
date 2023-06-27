import asyncio

from loguru import logger
from threading import Thread
from utils.proxies import set_proxy
from db_model.cleaner import db_clean
from .engine import distributor_binance, distributor_paxful, distributor_bybit

logger.add('../debug.log', format='{time} | {level} | {message}', level='DEBUG')


class TaskManager(object):
    """
    Менеджер для создания задач, исходя из данных прокси
    """

    def __init__(self, proxy_data: dict, number: int):
        self.proxy = proxy_data
        self.number = number
        # self.request_stream = 0

    def check_rstream(self):
        logger.info(self.get_all())

    def get_all(self):
        # logger.debug(f'In {self.__class__}')
        if self.number == 0:
            self.first_p_f_pack_tasks()
            self.second_p_f_pack_tasks()
            self.third_p_f_pack_tasks()
        elif self.number == 1:
            self.first_p_s_pack_tasks()
            self.second_p_s_pack_tasks()
            self.third_p_s_pack_tasks()
        elif self.number == 2:
            self.first_p_t_pack_tasks()
            self.second_p_t_pack_tasks()
            self.third_p_t_pack_tasks()
            # pass

    def first_p_f_pack_tasks(self):

        tasks = [
            asyncio.create_task(distributor_binance('BTC', 'USD', 'BUY', self.proxy)),
            # asyncio.create_task(distributor_binance('BTC', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_binance('BTC', 'EUR', 'BUY', self.proxy)),
            # asyncio.create_task(distributor_binance('BTC', 'EUR', 'SELL', self.proxy))
        ]

    def first_p_s_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_binance('USDT', 'USD', 'BUY', self.proxy)),
            # asyncio.create_task(distributor_binance('USDT', 'USD', 'SELL', self.proxy)),
            # asyncio.create_task(distributor_binance('USDT', 'EUR', 'BUY', self.proxy)),
            # asyncio.create_task(distributor_binance('USDT', 'EUR', 'SELL', self.proxy))
        ]

    def first_p_t_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_binance('ETH', 'USD', 'BUY', self.proxy)),
            asyncio.create_task(distributor_binance('ETH', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_binance('ETH', 'EUR', 'BUY', self.proxy)),
            asyncio.create_task(distributor_binance('ETH', 'EUR', 'SELL', self.proxy))
        ]

    def second_p_f_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_bybit('BTC', 'USD', 'BUY', self.proxy)),
            asyncio.create_task(distributor_bybit('BTC', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_bybit('BTC', 'EUR', 'BUY', self.proxy)),
            asyncio.create_task(distributor_bybit('BTC', 'EUR', 'SELL', self.proxy))
        ]

    def second_p_s_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_bybit('USDT', 'USD', 'BUY', self.proxy)),
            # asyncio.create_task(distributor_bybit('USDT', 'USD', 'SELL', self.proxy)),
            # asyncio.create_task(distributor_bybit('USDT', 'EUR', 'BUY', self.proxy)),
            # asyncio.create_task(distributor_bybit('USDT', 'EUR', 'SELL', self.proxy))
        ]

    def second_p_t_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_bybit('USDC', 'USD', 'BUY', self.proxy)),
            asyncio.create_task(distributor_bybit('USDC', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_bybit('USDC', 'EUR', 'BUY', self.proxy)),
            asyncio.create_task(distributor_bybit('USDC', 'EUR', 'SELL', self.proxy))
        ]

    def third_p_f_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_paxful('BTC', 'USD', 'BUY', self.proxy)),
            asyncio.create_task(distributor_paxful('BTC', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_paxful('BTC', 'EUR', 'BUY', self.proxy)),
            asyncio.create_task(distributor_paxful('BTC', 'EUR', 'SELL', self.proxy))
        ]

    def third_p_s_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_paxful('USDT', 'USD', 'BUY', self.proxy)),
            asyncio.create_task(distributor_paxful('USDT', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_paxful('USDT', 'EUR', 'BUY', self.proxy)),
            asyncio.create_task(distributor_paxful('USDT', 'EUR', 'SELL', self.proxy))
        ]

    def third_p_t_pack_tasks(self):
        tasks = [
            asyncio.create_task(distributor_paxful('USDC', 'USD', 'BUY', self.proxy)),
            asyncio.create_task(distributor_paxful('USDC', 'USD', 'SELL', self.proxy)),
            asyncio.create_task(distributor_paxful('USDC', 'EUR', 'BUY', self.proxy)),
            asyncio.create_task(distributor_paxful('USDC', 'EUR', 'SELL', self.proxy))
        ]

    def __str__(self):
        return str(self.__dict__)


async def loader(threads_count: int, delay: int) -> None:
    logger.info('Pool created...')
    counter = 1

    while True:
        try:
            logger.info(f'Lap: {counter} started...')
            db_clean()

            proxies = set_proxy()
            threads_list = list()

            for elem in range(threads_count):
                threads_list.append(TaskManager(proxy_data=proxies[elem], number=elem))

            for elem in threads_list:
                thr = Thread(target=elem.get_all())
                thr.start()
                thr.join()

            await asyncio.sleep(delay)
            counter += 1

        except asyncio.TimeoutError as ex:
            logger.error(f'Lap: {counter}')

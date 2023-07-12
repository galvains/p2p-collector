import asyncio
import psycopg2
import pickle

from loguru import logger
from threading import Thread
from utils.proxies import set_proxy
from db_model.cleaner import db_clean
from collectors.task_manager import distributor

from config import database, user, password, host, port
from .engine import distributor_binance, distributor_paxful, distributor_bybit


class TaskManager(object):
    """
    Менеджер для создания задач, исходя из данных прокси
    """

    def __init__(self, proxy_data: dict, threads_data: tuple, number: int):
        self.proxy = proxy_data
        self.data = threads_data
        self.number = number

    def get_all(self):
        for i in range(len(self.data)):
            data = self.data[i]

            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:

                for thr in data:
                    coin = thr[0]
                    fiat = thr[1]
                    trade = thr[2]

                    if i == 0:
                        asyncio.create_task(distributor_binance(coin, fiat, trade, self.proxy, conn))
                        logger.info(f'create task binance | {i} | {coin, fiat, trade}')
                    if i == 1:
                        asyncio.create_task(distributor_bybit(coin, fiat, trade, self.proxy, conn))
                        logger.info(f'create task bybit | {i} | {coin, fiat, trade}')
                    if i == 2:
                        asyncio.create_task(distributor_paxful(coin, fiat, trade, self.proxy, conn)),
                        logger.info(f'create task paxful | {i} | {coin, fiat, trade}')

            logger.info(f'connect to db closed! {self.proxy}')


async def loader(delay: int) -> None:
    logger.info('Pool created...')
    counter_laps = 1
    while True:
        try:
            logger.info(f'Lap: {counter_laps} started...')

            with psycopg2.connect(database=database, user=user, password=password, host=host, port=port) as conn:
                db_clean(conn)

            if counter_laps == 1 or counter_laps % 20 == 0:
                await distributor(limit_req=150, limit_exchange=4)

            with open('threads.data', 'rb') as file:
                threads_data = pickle.load(file)

            thr_list = list()
            proxies = set_proxy()

            bin_tasks = threads_data[0]
            byb_tasks = threads_data[1]
            pax_tasks = threads_data[2]
            len_tasks = max(len(bin_tasks), len(byb_tasks), len(pax_tasks))

            for elem in range(len_tasks):
                data = (bin_tasks[elem], byb_tasks[elem], pax_tasks[elem])
                thr_list.append(TaskManager(proxy_data=proxies[elem], threads_data=data, number=elem))

            for elem in thr_list:
                thr = Thread(target=elem.get_all())
                thr.start()
                thr.join()

            await asyncio.sleep(delay)

            counter_laps += 1

        except Exception as ex:
            logger.error(f'LOADER | {ex}')

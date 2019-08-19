import requests
from requests.exceptions import ReadTimeout, ConnectionError, RequestException, HTTPError
import json
import time
import logging
import glog
import threading
from multiprocessing.pool import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool

from data_process import data_process


def init_logging(log_file, level):
    """
    Initialize the logger, set the log level and format.
    :param log_file: the file location
    :param level log level, 10 is lowest, 50 is highest
    :return:logger
    """
    logger = logging.getLogger('my_logger')
    logger.setLevel(level)

    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class ApacheBenchmark(object):

    def __init__(self, kwargs):
        self.__dict__.update(kwargs)
        self.fail_time = 0
        # url,method,data 为当前请求所需的数据
        self.url = ""
        self.method = ""
        self.data = ""
        # 用于评价压测效果
        self.total_requests = self.number * self.concurrency
        self.timeout = self.time_limit/self.concurrency/self.number if self.time_limit else None

    def run_request(self, thread_name):
        """
        Send the request and record the result.
        :param thread_name: thread id
        :return: None
        """
        lock = threading.Lock()
        # glog.info('第{}个线程启动'.format(thread_name))

        # 通过循环可以在一个线程中对多个url按顺序进行请求
        for index, url in enumerate(self.urls):
            # 修改当前请求的参数值
            self.url = url
            self.method = self.methods[index]
            self.data = self.datas[index]
            # 根据method判断是否需要data
            if self.method == 'get':
                data = None
            else:
                data = json.dumps(self.data).encode('ascii')

            # 记录请求时间，requests库中的时间只记录了连接建立成功的时间
            start_time = time.time()

            # 用于判断能否与目标url建立连接，不能时会记录失败原因
            try:
                r = requests.request(self.method,
                                     self.url,
                                     cookies=self.cookies,
                                     headers=self.headers,
                                     data=data,
                                     timeout=self.timeout)
                # 记录请求结果，并将结果记录在日志之中
                if r.status_code == 200:
                    status = 'Success.'
                    glog.info('返回请求状态：{:10}'.format(status))
                else:
                    status = 'Fail，responded_code：{}'.format(r.status_code)
                    self.fail_time += 1
                    glog.warn('返回请求状态：{:10}, 失败次数{}.'.format(status, self.fail_time))

                # 将每次请求的时间写入到txt文件中，便于后续统计
                if hasattr(self, 'time_location'):
                    lock.acquire()
                    with open(self.time_location, 'a') as f:
                        f.write('{}\n'.format(r.elapsed.microseconds / 10 ** 6))
                    lock.release()

            except ConnectionError:
                end_time = time.time()
                self.fail_time += 1
                glog.error('失败请求耗时:{}.'.format(end_time - start_time))
                glog.error('网络问题，连接失败，当前失败次数{}.'.format(self.fail_time))

            except ReadTimeout:
                end_time = time.time()
                self.fail_time += 1
                glog.error('失败请求耗时:{}.'.format(end_time - start_time))
                glog.error('请求超时，当前失败次数{}.'.format(self.fail_time))

            except HTTPError:
                end_time = time.time()
                self.fail_time += 1
                glog.error('失败请求耗时:{}.'.format(end_time - start_time))
                glog.error('返回了不成功的状态码，当前失败次数{}.'.format(self.fail_time))

            except RequestException:
                end_time = time.time()
                self.fail_time += 1
                glog.error('失败请求耗时:{}.'.format(end_time - start_time))
                glog.error('其他原因导致连接失败，当前失败次数{}.'.format(self.fail_time))

    def run(self, pool_name):
        """
        Create a thread tool to execute the request
        :param pool_name:
        :return:
        """
        # glog.info('第{}个进程启动'.format(pool_name))
        thread_pool = ThreadPool(processes=self.number)
        thread_pool.map(self.run_request, range(self.number))
        thread_pool.close()
        thread_pool.join()

    def start(self):
        """
        Create a process pool to execute concurrent requests.
        :return:
        """
        process_pool = ProcessPool(processes=self.concurrency)
        process_pool.map(self.run, range(self.concurrency))
        process_pool.close()
        process_pool.join()

    def result_statistics(self, total_time):
        """
        Process the test results and write it to a log file.
        :param total_time: Program execution time
        :return: Average Requests Number Per Second
        """

        logger = init_logging(self.log_location, self.log_level)
        logger.info("===============================================")
        logger.info('URL: {}'.format(self.urls))
        logger.info('Total Requests Number: {}'.format(self.total_requests))
        logger.info('Concurrent Requests Number: {}'.format(self.concurrency))
        logger.info('Total Time Cost(seconds): {}'.format(total_time))
        logger.info('Average Time Per Request(seconds): {}'.format(total_time / self.total_requests))
        logger.info('Average Requests Number Per Second: {}'.format(self.total_requests / total_time))
        if hasattr(self, 'time_location'):
            try:
                result_dict = data_process(self.time_location)
                logger.info('Max Request Time(seconds): {}'.format(result_dict['max']))
                logger.info('Min Request Time(seconds): {}'.format(result_dict['min']))
                logger.info('Mean Request Time(seconds): {}'.format(result_dict['mean']))
                logger.info('Standard Deviation of Request Execution Time(seconds): {:5}'.format(result_dict['std']))
                logger.info('Execution Time for the First 25% of Request(seconds): {}'.format(result_dict['25.0%']))
                logger.info('Execution Time for the First 50% of Request(seconds): {}'.format(result_dict['50.0%']))
                logger.info('Execution Time for the First 75% of Request(seconds): {}'.format(result_dict['75.0%']))
            except UnboundLocalError:
                print('There is not a statistics result.')
        logger.info("===============================================")
        return self.total_requests / total_time



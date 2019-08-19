import sys
import json
import time
from optparse import OptionParser
from apache_benchmark import ApacheBenchmark


class ConfParse:

    def parse(self):
        """
        parse the args.

        :return dict
        """
        parser = OptionParser(
            description="The scripte is used to simulate apache benchmark(sending requests and testing the server)")
        parser.add_option("-c", "--conf", dest="config", help="The test script you want to choose.")
        (options, args) = parser.parse_args()

        # 必须指定配置文件，否则报错
        if not options.config:
            print('Need to specify the parameter option "-c"!')
        if '-h' in sys.argv or '--help' in sys.argv:
            print(__doc__)
        options = self.read_conf(options.config)
        return options

    def read_conf(self, config_json):
        """
        Read config from json

        :param config_json: name of the json file
        :return: dict
        """
        with open(config_json) as f:
            config = json.load(f)
        # 当前请求数
        config['number'] = 0
        return config


if __name__ == '__main__':
    # 读取配置文件
    parser = ConfParse()
    config_dict = parser.parse()
    # 通过循环进行批量测试
    for n in config_dict['numbers']:
        # 设置当前测试的线程数
        config_dict['number'] = n
        ab = ApacheBenchmark(config_dict)
        # 使用time统计执行过程所需的总时间
        start_time = time.time()
        ab.start()
        end_time = time.time()
        # 对统计的结果进行进一步的处理
        requests_peer_time = ab.result_statistics(end_time - start_time)

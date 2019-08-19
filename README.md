基于python的http压测工具

基本功能：
1.对指定的url进行压力测试，可以指定并发数与线程数。
2.统计结果，并计算评价参数，目前可以统计并发连接数，每秒连接数，最大，最小，平均，前25%，
50%，75%的连接完成时间。

使用方法：
python3 main.py -c conf.json 

-c参数用于指定配置文件

配置文件参数解释：
urls: 类型为list，需要进行测试的url，如果其中包含多个url时会按顺序进行请求

methods: 类型为list，请求需要的方法, 如果包含多个url时需要给每个url设置对应的方法

headers:  类型为dict， http请求时需要的头

concurrency: 类型为int， 并发数

numbers: 类型为list，线程数, 包含多个值时可以对目标url进行批量测试

time_limit: 类型为int, 请求时间限制

log_location: 类型为str, 日志文件所在的位置

log_level: 类型为int，日志的级别，默认为INFO

cookies: 类型为str，请求时所需的cookies

datas: 类型为list, post方法需要的data，get方法对应的值为""

time_location": 类型为list，单次请求时间统计结果存放的位置，可以缺省，缺省时可以减少IO时间消耗


文件描述：
conf.json: 配置文件
main.py: 工具入口，读取conf文件，将参数传递给ApacheBenchmark
apache_benchmark.py: ApacheBenchmark的实现文件，通过requests库实现
data_process.py: 单个请求的时间处理与统计函数
apache_benchmark.log: 用于记录统计结果
test文件中有个使用Flask搭建的测试服务，用于模拟登陆和浏览的过程，可以测试POST和GET方法。

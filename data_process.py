import numpy as np
import os


def data_process(file_name):
    """
    Process and count the execution time of the request
    :param file_name: File including each request's execution time
    :return: The statistical results dict
    """
    execution_time = []
    try:
        with open(file_name, 'r') as f:
            for time in f.readlines():
                execution_time.append(float(time))
        execution_time_array = np.array(execution_time)
        execution_time_array.sort()
        result_dict = dict()
        result_dict['max'] = execution_time_array.max()
        result_dict['min'] = execution_time_array.min()
        result_dict['mean'] = execution_time_array.mean()
        result_dict['std'] = execution_time_array.std()
        percentage_list = [0.25, 0.5, 0.75]
        for p in percentage_list:
            result_dict['{}%'.format(p * 100)] = execution_time_array[int(p * len(execution_time_array))]
        # 清理文件，便于下次统计
        os.remove(file_name)
    except FileNotFoundError:
        print('No such file.')

    return result_dict

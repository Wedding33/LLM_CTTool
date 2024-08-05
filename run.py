import argparse
import os
from rampconcurrent.ramp_model import RampUpThreadPool
from models.chat_completions import ChatCompletions
from utils.common_utils import init_dir
from utils.analyze_data import analyze_csv_data
from utils.config_utils import load_config

# 设置运行参数
parser = argparse.ArgumentParser(description='Run the application with a specific config.')
parser.add_argument('-config', default="./config/config_int4.py", help='The config file to use, e.g., config/config.py')
args = parser.parse_args()

config_path = args.config
if not os.path.isfile(config_path):
    print(f"Error: The config file '{config_path}' was not found.")

# 加载动态config
config = load_config(config_path)

# 初始化测试
prefix = init_dir()
chat_model = ChatCompletions(config, prefix)

# 启动线程池测试
pool = RampUpThreadPool.from_config(config, task_method=ChatCompletions.send_request, task_instance=chat_model, prefix=prefix)
pool.start()
pool.wait_for_completion()

ramp_log_file = chat_model.ramp_logger.filename
data_csv = chat_model.data_writer_file
print(f"数据文件:{data_csv}")
analyze_csv_data(data_csv, prefix=prefix)
import argparse
import importlib.util
import os
import sys
from rampconcurrent.ramp_model import RampUpThreadPool
from models.chat_completions import ChatCompletions
from utils.common_utils import init_dir
from utils.analyze_data import analyze_csv_data
from utils.draw import DrawRamp

def load_config(config_path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)
    return config

def main(config_path):
    if not os.path.isfile(config_path):
        print(f"Error: The config file '{config_path}' was not found.")
        return
    
    config = load_config(config_path)
    
    prefix = init_dir()
    chat_model = ChatCompletions(config, prefix)
    pool = RampUpThreadPool.from_config(config, task_method=ChatCompletions.send_request, task_instance=chat_model, prefix=prefix)
    pool.start()
    pool.wait_for_completion()


    #ramp_log_file = pool.ramp_log_file
    ramp_log_file = chat_model.ramp_logger.filename
    data_csv = chat_model.data_writer_file
    print(f"数据文件:{data_csv}")
    analyze_csv_data(data_csv, prefix=prefix)


parser = argparse.ArgumentParser(description='Run the application with a specific config.')
parser.add_argument('config', default="./config/config_wed.py", help='The config file to use, e.g., config/config1.py')
args = parser.parse_args()
main(args.config)

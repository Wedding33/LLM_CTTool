import logging
import datetime
import os
import configparser
import csv
import threading

class WLogger:
    def __init__(self, prefix, level=logging.INFO):
        self.loggers = {}
        self.level = level
        self.prefix = prefix
        self.current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.filename = os.path.join("logs", f'{self.prefix}_{self.current_datetime}.log')
        self._get_logger()

    def _get_logger(self):
            # 创建新的logger
            logger = logging.getLogger(f'{self.prefix}_{self.current_datetime}')
            logger.setLevel(self.level)
            # 创建日志格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # 创建文件处理器，设置编码为 utf-8
            fh = logging.FileHandler(self.filename, encoding='utf-8')
            fh.setLevel(self.level)
            fh.setFormatter(formatter)

            # 添加处理器到logger
            logger.addHandler(fh)
            self.logger = logger

    def log(self, level, message):
        getattr(self.logger, level)(message)
        # 手动刷新文件处理器
        for handler in self.logger.handlers:
            handler.flush()


class DataWriter:
    def __init__(self, prefix, suffix='.csv'):
        self.prefix = prefix
        self.suffix = suffix
        self.lock = threading.Lock()
        self.filename = os.path.join("data", self._generate_filename())
        self.write_row(("是否执行成功", "状态", "prompt token数", "响应token数","总token数", "收到第一个token耗时", "收到所有token耗时", "最后一个token与第一个token时间差", "失败原因"))

    def _generate_filename(self):
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{self.prefix}_{current_datetime}{self.suffix}"

    def write_line(self, line):
        with self.lock:
            with open(self.filename, 'a', encoding="utf-8") as file:  # 使用 'a' 模式以追加数据
                file.write(line + '\n')
    def write_row(self, row_tuple):
        with self.lock:
            with open(self.filename, 'a', newline='', encoding="utf-8") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(row_tuple)

def init_dir():
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    # 创建目录路径
    directory_path = os.path.join(os.getcwd(), "logs", current_datetime)

    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

if __name__ == "__main__":
    import time
    logger = WLogger("test")
    logger.log("info", "1")
    logger.log("info", "2")
    time.sleep(1)
    logger.log("info", "1")
    logger.log("info", "2")
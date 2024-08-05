import threading
import time
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.common_utils import WLogger
import asyncio

class RampUpThreadPool:
    def __init__(self, max_workers, ramp_up_time, task_method, task_instance, continuous_time, prefix=""):
        self.max_workers = max_workers
        self.ramp_up_time = ramp_up_time
        self.task_method = task_method
        self.task_instance = task_instance
        self.continuous_time = continuous_time
        # 提交任务的线程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.monitor_executor = ThreadPoolExecutor(max_workers=1)
        self.submit_executor = ThreadPoolExecutor(max_workers=32)
        self.submitted_tasks = 1  # 追踪提交的任务总数
        self.completed_tasks = 0
        self.current_tasks = 0
        self.lock = threading.Lock()
        self.submit_lock = threading.Lock()
        #self.ramp_step = max_workers // ramp_up_time
        self.logger = WLogger(f"{prefix}/RampUp_Model")
        self.current_target_task = 0
        self.last_target_task = 0
        self.ramp_log_file = self.logger.filename
        self.features = []

    @classmethod
    def from_config(cls, config, task_method, task_instance, prefix=""):
        return cls(
            max_workers=config.max_workers,
            ramp_up_time=config.ramp_up_time,
            task_method=task_method,
            task_instance=task_instance,
            continuous_time=config.continuous_time,
            prefix=prefix
        )
    
    def start(self):
        self.start_time = time.time()
        self.up_end_time = self.start_time + self.ramp_up_time
        self.total_end_time = self.start_time + self.continuous_time + self.ramp_up_time

        print("开始线程池")
        status = "上升"
        if self.ramp_up_time > 0:
            self.current_tasks = 0
        else:
            status = "保持"
            print(f"提交任务数量:{self.max_workers}")
            self.current_tasks = 0
            self.current_target_task = self.max_workers

        status = "上升"
        self.task_instance.start_time = time.time()
        # task_instance作用：传递submit函数需要用到
        
        for thread_id in range(self.max_workers):
            self.executor.submit(self.task_method, self.task_instance, status, thread_id)
        print("任务提交完成")

        self.task_instance.stable_start_time = time.time()
        self.task_instance.total_end_time = time.time() + self.continuous_time

        while time.time() < self.total_end_time:
            time.sleep(2)
        # time.sleep(2)的作用是避免繁忙等待，通过每2秒钟暂停一次来减少CPU的使用率，并实现一种轮询等待机制，确保在 self.total_end_time 之前程序持续运行。

    def stop(self):
        self.executor.shutdown(wait=True)

    def wait_for_completion(self):
        self.executor.shutdown(wait=True)

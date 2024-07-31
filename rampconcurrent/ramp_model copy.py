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
    
    def submit_tasks(self, statu):
        with self.submit_lock:
            # 拿到锁之后，计算是否还需要提交线程
            wait_num = self.executor._work_queue.qsize()
            self.current_tasks = self.submitted_tasks - self.completed_tasks
            add_num = self.current_target_task - self.current_tasks
            if wait_num > 0 or add_num <= 0:
                return
            self.submitted_tasks = self.submitted_tasks + add_num
            print(f"开始提交:{add_num}")
        futures = [self.executor.submit(self.task_method, self.task_instance, statu) for _ in range(add_num)]
        for future in futures:
            future.add_done_callback(self.task_completed)
        print("提交完成")

    # 线程完成只打印日志, 提交线程都放在 monitor_task
    def task_completed(self, future):
        try:
            with self.lock:
                #print("任务完成")
                self.completed_tasks += 1
                print("任务完成")
                wait_num = self.executor._work_queue.qsize()
                self.logger.log("info", f" {time.time() - self.start_time} 提交线程总数： {self.submitted_tasks}, 完成线程总数: {self.completed_tasks}, 正在执行的线程数: {self.current_tasks}, 最大线程数: {self.max_workers} 等待执行线程数: {wait_num}")
                #self.current_tasks = self.submitted_tasks - self.completed_tasks
        except Exception as e:
            print(e)
            pass

    # 监控一个线程
    def monitor_task(self):
        self.logger.log("info", "启动任务监控线程")
        step = self.max_workers / (self.up_end_time - self.start_time + 1)
        print("启动监控线程")
        print(f"statu: {time.time() - self.total_end_time}")
        while time.time() < self.total_end_time:
            wait_num = self.executor._work_queue.qsize()
            print(f"wait_num: {wait_num}")
            if wait_num > 0:
                self.current_tasks = self.current_target_task
            current_time = time.time()
            self.logger.log("info", f" {current_time - self.start_time} 提交线程总数： {self.submitted_tasks}, 完成线程总数: {self.completed_tasks}, 正在执行的线程数: {self.current_tasks}, 最大线程数: {self.max_workers} 等待执行线程数: {wait_num}")
            if wait_num == 0:
                if current_time < self.up_end_time:
                    self.current_target_task = int(step * (current_time -  self.start_time))
                    print(f"step:{step}  current_target_task : {self.current_target_task }")
                    add_num = self.current_target_task - self.current_tasks + 5
                    self.submit_tasks("上升")
                else:
                    print("保持")
                    self.current_target_task = self.max_workers
                    #add_num = self.max_workers - self.current_tasks + 5
                    #self.submit_tasks("保持", add_num)              
                    self.submit_executor.submit(self.submit_tasks, "保持")
            time.sleep(1)


    def start(self):
        self.start_time = time.time()
        self.up_end_time = self.start_time + self.ramp_up_time
        # 任务开始提交耗时，修正2秒
        self.total_end_time = self.start_time + self.continuous_time + self.ramp_up_time
        print(f"开始线程池 开始 {self.start_time}  结束 {self.total_end_time}")
        statu = "上升"
        if self.ramp_up_time > 0:
            self.current_tasks = 0
        else:
            statu = "保持"
            print(f"提交线程：{self.task_method}   {self.task_instance} 提交任务数量:{self.max_workers}")
            self.current_tasks = 0
            # 当前时间的目标线程数量
            self.current_target_task = self.max_workers

        # 主线程监控任务运行情况      
        #self.monitor_task()
    def stop(self):
        self.executor.shutdown(wait=True)

    def wait_for_completion(self):
        self.executor.shutdown(wait=True)

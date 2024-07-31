import requests
import time
import json
import traceback
import random
from utils.common_utils import WLogger, DataWriter
from transformers import AutoTokenizer
import copy
import warnings
from urllib3.exceptions import InsecureRequestWarning

# 忽略 InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

class ChatCompletions:

    def __init__(self, config, prefix="./"):
        self.url = config.api_url
        self.headers = config.api_headers
        self.data = config.api_data
        self.prompt_file = config.prompt_file
        self.is_continue = True
        self.max_thread = config.max_workers
        self.logger = WLogger(f"{prefix}/response")
        self.ramp_logger = WLogger(f"{prefix}/RampUp_Model")
        #self.response_logger = WLogger(f"{prefix}/response")
        #self.data_logger = WLogger(f"{prefix}/completion_data")
        self.data_writer = DataWriter(f"{prefix}/completion_data")
        self.data_writer_file = self.data_writer.filename
        self.tokenizer_path = config.tokenizer_path
        self.prompt2token_num = {}

        # 读取预置的prompt 文件
        self.prompt_list = self.read_prompts()
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path, trust_remote_code=True, use_fast=False)
        self.calculate_prompt_token_numbers()

        self.start_time = 0
        self.stable_start_time = 0
        self.total_end_time = time.time() + 60*1000
        self.completed_tasks = 0
        self.running_task = set()


    def calculate_prompt_token_numbers(self):
        for prompt in self.prompt_list:
            self.prompt2token_num[prompt] = self.tokenizer_num(prompt)

    def read_prompts(self):
        with open(self.prompt_file, 'r', encoding='utf-8') as file:
            return file.readlines()

    def tokenizer_num(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors='pt')
        input_ids = inputs.input_ids[0]
        return len(input_ids)


    def send_request(self, statu, thread_id):
        current_time = time.time()
        while current_time < self.total_end_time:
            if thread_id > self.max_thread:
                self.running_task.discard(thread_id)
                return
            else:
                self.running_task.add(thread_id)
            self.ramp_logger.log("info", f"完成线程总数: {self.completed_tasks}, 正在执行的线程数: {len(self.running_task)}, 最大线程数: {self.max_thread}")
            if current_time > self.stable_start_time:
                statu = "保持"
            result_line = None
            # 多线程
            data = copy.deepcopy(self.data)
            try:
                api_type = "multi"
                prompt = random.choice(list(self.prompt2token_num.keys()))
                if "messages" in  data:
                    data['messages'].append(dict(role="user", content=prompt))
                if "prompt" in data:
                    data['prompt'] = prompt
                    api_type = "single"
                prompt_token_num = self.prompt2token_num[prompt]
                self.logger.log("info", f"prompt: {prompt.strip()}    token num: {prompt_token_num}")
                start_time = time.time()
                response = requests.post(self.url, json=data, headers=self.headers, verify=False, stream=True, timeout=60)
                if response.status_code == 200:
                    if api_type == "multi":
                        result_line =  self.process_response(response, start_time, prompt_token_num, statu, prompt.strip())
                    else:
                        result_line =  self.process_response_single(response, start_time, prompt_token_num, statu, prompt.strip())
                else:
                    result_line = (False, statu, 0, 0, 0, 0, 0, 0, f"Response:{response.status_code}")
            except requests.ConnectionError as e:
                #print("连接错误:", e)
                result_line = (False, statu, 0, 0, 0, 0, 0, 0, "连接错误")
            except requests.HTTPError as e:
                #print("HTTP错误:", e)
                result_line = (False, statu, 0, 0, 0, 0, 0, 0, "HTTP错误")
            except Exception as e:
                print(e)
                traceback.print_exc()
                exception_type = type(e).__name__  # 获取异常类型的名称
                result_line = (False, statu, 0, 0, 0, 0, 0, 0, exception_type)
            self.data_writer.write_row(result_line)

            self.completed_tasks += 1
            current_time = time.time()
            #self.ramp_logger.log("info", f"完成线程总数: {self.completed_tasks}, 正在执行的线程数: {len(self.running_task)}, 最大线程数: {self.max_thread}")
            if current_time > self.stable_start_time:
                statu = "保持"
            print(f"{self.total_end_time - current_time}")
            # if self.is_continue and current_time < self.total_end_time:
            #     self.send_request(statu, thread_id)

    def process_response_single(self, response, start_time, prompt_token_num, statu, prompt):
        completion_token_num = prompt_token_num
        first_token = None
        first_token_time = 0
        full_token_time = 0
        tokens = []
        response_token_num = 0
        started = False
        for line in response.iter_lines():
            #print(line)
            try:
                if line:
                    #first_rec_time = time.time()
                    #print(f"第一个响应时长:{first_rec_time - start_time}")
                    json_str = line.decode("utf-8").lstrip('data: ')
                    if json_str.startswith("{") and json_str.endswith("}"):
                        json_data = json.loads(json_str)
                        choice_0 = json_data['choices'][0]
                        if 'text' in choice_0:
                            completion_token_num += 1
                            tk = choice_0['text']
                            if not first_token:
                                first_token = tk
                                first_token_time = time.time()
                                #self.logger.log("info", first_token)
                                #print(f"first_token: {first_token}")
                            tokens.append(tk)
                # elif first_token is None:
                #     return (False, statu, 0, 0, 0, 0, 0, 0, f"响应为空:  {line.decode('utf-8')}")
            except Exception as e:
                #print(f"{e}  {line}")
                self.logger.log("info", f"{e}  {line}")
                return (False, statu, 0, 0, 0, 0, 0, 0, f"{e}  {line.decode('utf-8')}")
                        

        full_token_time = time.time()
        response_token_num = len(tokens)
        full_text = "".join(tokens)
        self.logger.log("info", f"prompt: {prompt}  \n回答: {full_text}")
        #self.data_logger.log(level="info", message=f"True,{completion_token_num},{first_token_time - start_time},{full_token_time - start_time},{full_token_time - first_token_time}")
        #self.data_writer.write_line()
        return True, statu, prompt_token_num, response_token_num, completion_token_num, first_token_time - start_time, full_token_time - start_time, full_token_time - first_token_time, ""

    def process_response(self, response, start_time, prompt_token_num, statu, prompt):
        completion_token_num = prompt_token_num
        first_token = None
        first_token_time = 0
        full_token_time = 0
        tokens = []
        response_token_num = 0
        started = False
        for line in response.iter_lines():
            #print(line)
            try:
                if line:
                    #first_rec_time = time.time()
                    #print(f"第一个响应时长:{first_rec_time - start_time}")
                    json_str = line.decode("utf-8").lstrip('data: ')
                    if json_str.startswith("{") and json_str.endswith("}"):
                        json_data = json.loads(json_str)
                        choice_0 = json_data['choices'][0]
                        if 'content' in choice_0['delta']:
                            completion_token_num += 1
                            tk = choice_0['delta']['content']
                            if not first_token:
                                first_token = tk
                                first_token_time = time.time()
                                #self.logger.log("info", first_token)
                                #print(f"first_token: {first_token}")
                            tokens.append(tk)
                # elif first_token is None:
                #     return (False, statu, 0, 0, 0, 0, 0, 0, f"响应为空:  {line.decode('utf-8')}")
            except Exception as e:
                #print(f"{e}  {line}")
                self.logger.log("info", f"{e}  {line}")
                return (False, statu, 0, 0, 0, 0, 0, 0, f"{e}  {line.decode('utf-8')}")
                        

        full_token_time = time.time()
        response_token_num = len(tokens)
        full_text = "".join(tokens)
        self.logger.log("info", f"prompt: {prompt}  \n回答: {full_text}")
        #self.data_logger.log(level="info", message=f"True,{completion_token_num},{first_token_time - start_time},{full_token_time - start_time},{full_token_time - first_token_time}")
        #self.data_writer.write_line()
        return True, statu, prompt_token_num, response_token_num, completion_token_num, first_token_time - start_time, full_token_time - start_time, full_token_time - first_token_time, ""
import re

line="2024-06-13 15:36:18,712 - /home/apollo/pilot/concurrent_test/logs/2024-06-13_15-34/RampUp_Model_2024-06-13_15-34 - INFO - 提交线程总数： 1, 完成线程总数:999, 正在执行的线程数: -998, 最大线程数: 1000  等待执行线程数: 1"

time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
print(f"time_match:{time_match}")
count_match = re.search(r"正在执行的线程数: (\d+)", line)
print(f"count_match:{count_match}")
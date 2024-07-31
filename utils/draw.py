import re
import matplotlib.pyplot as plt
import datetime
import matplotlib
from matplotlib import font_manager

font_path = "./fonts/simsun.ttc"
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)
# 设置中文字体
plt.rcParams['font.sans-serif'] = prop.get_name()  # 或其他中文字体
plt.rcParams['axes.unicode_minus'] = False
matplotlib.use('Agg')

class DrawRamp:
    def __init__(self, log_file, config, title, prefix, y_axis):
        self.log_file = log_file
        self.max_workers = config.max_workers
        self.title = title
        self.prefix = prefix
        self.y_axis = y_axis
        self.config = config

    def parse_log_file(self):
        original_data = {}
        with open(self.log_file, 'r', encoding="utf-8") as file:
            for line in file:
                print(line)
                time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                print(f"time_match:{time_match}")
                count_match = re.search(r"正在执行的线程数: (-?\d+)", line)
                print(f"count_match:{count_match}")
                if time_match and count_match:
                    time_str = time_match.group(1)
                    time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    count = int(count_match.group(1))
                    count = min(count, self.max_workers)
                    original_data[time_obj] = count

        # 创建新的时间序列并填充缺失的秒
        if original_data:
            start_time = min(original_data.keys())
            end_time = max(original_data.keys())
            current_time = start_time
            self.timestamps = []
            self.executing_threads = []
            last_count = 0

            while current_time <= end_time:
                # 计算每个时间点与开始时间的差值（秒）
                seconds_since_start = (current_time - start_time).total_seconds()
                self.timestamps.append(seconds_since_start)
                self.executing_threads.append(original_data.get(current_time, last_count))
                last_count = original_data.get(current_time, last_count)
                current_time += datetime.timedelta(seconds=1)
        print(original_data)


    def plot_executing_threads(self):
        plt.plot(self.timestamps, self.executing_threads)
        plt.title(self.title)
        plt.xlabel('时间（秒）')
        plt.ylabel(self.y_axis)

        # 设置 Y 轴刻度
        y_ticks = list(plt.yticks()[0])
        max_executing_threads = max(self.executing_threads)
        if max_executing_threads not in y_ticks:
            y_ticks.append(max_executing_threads)
        plt.yticks(sorted(y_ticks))


        plt.gcf().autofmt_xdate()
        file_name = f"{self.prefix}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        plt.savefig(file_name)
        plt.close()


if __name__ == "__main__":
    draw = DrawRamp("/home/apollo/pilot/concurrent_test/logs/2024-06-13_15-25/RampUp_Model_2024-06-13_15-25.log", 5, '正在执行的线程数随时间变化', 'RampUp', '线程数')
    draw.parse_log_file()
    # print(draw.timestamps)
    # print(len(draw.executing_threads))
    # print(draw.executing_threads)
    draw.plot_executing_threads()

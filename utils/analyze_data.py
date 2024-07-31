import pandas as pd
import numpy as np
import datetime

def analyze_csv_data(filename, prefix=""):
    print(f"输出 summary, filename: {filename}")
    # 将 CSV 数据转换为 DataFrame
    df = pd.read_csv(filename)
    print(df.head(1)['是否执行成功'])
    print(df.head(1)['收到所有token耗时'])
    print(df.head(1)['prompt token数'])
    print(df['收到所有token耗时'])
    #return
    # 筛选状态为“保持”且第一列为True的行
    filtered_df = df[(df['状态'] == '保持') & (df['是否执行成功'] == True)]
    success_df = df[(df['是否执行成功'] == True)]

    # 如果没有符合条件的数据，则返回提示
    if filtered_df.empty:
        return "没有符合'状态为保持且执行成功'的数据。"
    
    # 计算总请求个数（状态为保持的行数）
    total_requests = len(df[df['状态'] == '保持'])
    
    # 计算成功率（第一列为True的个数除以状态为保持的总数）
    success_rate = len(filtered_df) / total_requests

    prompt_token_sum = filtered_df['prompt token数'].sum()
    response_token_sum = filtered_df['响应token数'].sum()
    total_token_sum = filtered_df['总token数'].sum()

    # 初始化一个字符串来存储格式化的统计数据
    formatted_stats = f"总请求个数: {total_requests}\n"
    formatted_stats += f"成功率: {success_rate:.2%}\n"
    formatted_stats += f"prompt token总数: {prompt_token_sum}\n"
    formatted_stats += f"响应token总数: {response_token_sum}\n"
    formatted_stats += f"prompt+响应 token总数: {total_token_sum}\n\n"


    print("----mean-----")
    # 假设 df 是你的数据框，'your_column' 是要转换的列
    filtered_df['收到所有token耗时'] = pd.to_numeric(filtered_df['收到所有token耗时'], errors='coerce').astype(float)

    print(filtered_df['收到所有token耗时'].head(2))
    #return 
    
    # 对于每个感兴趣的列，计算所需的统计数据并格式化输出
    for col in ['收到第一个token耗时', '收到所有token耗时', '最后一个token与第一个token时间差']:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce').astype(float)
        print(f"统计:{col}")
        stats = {
            'mean': filtered_df[col].mean(),
            'median': filtered_df[col].median(),
            '99%': np.percentile(filtered_df[col], 99),
            '95%': np.percentile(filtered_df[col], 95),
            '90%': np.percentile(filtered_df[col], 90)
        }
        
        formatted_stats += f"列: {col}\n"
        for key, value in stats.items():
            formatted_stats += f"  {key}: {value:.4f} 秒\n"
        formatted_stats += "\n"

    # 获取当前时间日期
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary_file = f"{prefix}/summary_{current_time}.txt"
    print(f"summary_file: {summary_file}")

    # 写入文件
    print(f"写")
    with open(summary_file, 'w', encoding='utf-8') as file:
        file.write(formatted_stats)
    print(f"：{formatted_stats}")
    return formatted_stats

if __name__ == "__main__":
    completed_file = "data\mars_v2_data_2024-01-17_16-08-51.csv"
    completed_file = "data\mars_v2_data_2024-01-21_14-24-43.csv"
    completed_file = "logs/2024-02-01_11-03/mars_v2_data_2024-02-01_11-03-39.csv"
    stats_text = analyze_csv_data(completed_file)
    print(stats_text)

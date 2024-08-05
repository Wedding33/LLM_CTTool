# 最大并发数
max_workers = 2
# 爬升时间
ramp_up_time = 0
# 最大并发持续时间
continuous_time = 200

# 读取prompt_file 中的内容发送给大模型，一行是一个prompt
prompt_file = "data/64.csv"
tokenizer_path = "tokenizer/Qwen-72B/"

# ----------接口相关配置-----------
api_headers = {
    "Content-Type": "application/json",
    "Authorization": "TEST-46542881-54d4-4096-b93d-6d5a3db326ac"
}

api_url = "http://10.57.136.28:7888/v1/chat/completions"
model_name = "eval_ZTEAIM-Qtest2-72-instruct"

api_data = dict(
    model=model_name,
    messages=[
        # dict(role="system", content=""),
        # dict(role="user", content=prompt)) 
    ],
    n=1,
    best_of=1,
    max_tokens=2048,
    temperature=0,
    use_beam_search=False,
    presence_penalty=1.2,
    frequency_penalty=0,
    stream=True,
    ignore_eos=True
)
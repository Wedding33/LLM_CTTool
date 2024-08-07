# 最大并发数
max_workers = 2
# 爬升时间
ramp_up_time = 0
# 最大并发持续时间
continuous_time = 100

# 读取prompt_file 中的内容发送给大模型，一行是一个prompt
prompt_file = "data/long_prompt.csv"
tokenizer_path = "tokenizer/Qwen-72B/"

# ----------接口相关配置-----------

api_headers = {
    "Content-Type": "application/json",
}

api_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat?access_token=" + "24.4141871cf9a4c2eb1970d44065911884.2592000.1725526993.282335-103733095"
model_name = "Yi-34B-Chat"

api_data = dict(
    model=model_name,
    messages=[
        # dict(role="system", content=""),
        # dict(role="user", content=prompt)) 
    ],
    n=1,
    best_of=1,
    max_tokens=2048,
    temperature=0.1,
    use_beam_search=False,
    penalty_score=1.2,
    frequency_penalty=0,
    stream=True,
    ignore_eos=True
)
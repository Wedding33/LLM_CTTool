from transformers import AutoTokenizer

line = "蒙古国的首都是乌兰巴托（Ulaanbaatar）\n冰岛的首都是雷克雅未克（Reykjavik）\n埃塞俄比亚的首都是"
line = "在EPC网络中哪个网元负责为UE分配IP地址?"


tokenizer = AutoTokenizer.from_pretrained("tokenize/models/qwen/Qwen-72B/", trust_remote_code=True, use_fast=False)
inputs = tokenizer(line, return_tensors='pt')
input_ids = inputs.input_ids[0]
print(f"token 的id, input_ids:{input_ids}")

decoded_text = tokenizer.decode(input_ids, skip_special_tokens=True)
print("token 的id 序列解码的效果:", decoded_text)

tokens = tokenizer.convert_ids_to_tokens(input_ids)
tokens = [token.decode("utf-8") for token in tokens]
print(f"token id 从字典中取出token, 再utf8解码:{tokens}")
print(f"文本字符长度: {len(line)}, token 长度 : {len(tokens)}")